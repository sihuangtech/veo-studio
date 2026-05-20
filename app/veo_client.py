import json
import os
import re
import shutil
import tempfile
import time
from datetime import datetime
from google import genai
from google.genai import types
from google.oauth2 import service_account
from .config import Config
from .utils import setup_logger

logger = setup_logger("VeoClient")

class VeoClient:
    def __init__(
        self,
        api_key=None,
        base_url=None,
        https_proxy=None,
        text_model=None,
        auth_mode=None,
        service_account_file=None,
        project=None,
        location=None,
    ):
        try:
            effective_auth_mode = self._normalize_auth_mode(auth_mode or Config.get_auth_mode())
            effective_proxy = https_proxy or Config.HTTPS_PROXY
            effective_base_url = base_url or Config.GOOGLE_GENAI_BASE_URL
            self.text_model = text_model or Config.get_current_text_model()

            if effective_proxy:
                logger.info(f"Using proxy: {effective_proxy}")
                # 中文注释：代理写入环境变量，供 google-genai 底层 HTTP 客户端读取。
                os.environ["HTTPS_PROXY"] = effective_proxy
                os.environ["HTTP_PROXY"] = effective_proxy

            client_kwargs = self._build_client_kwargs(
                auth_mode=effective_auth_mode,
                api_key=api_key,
                service_account_file=service_account_file,
                project=project,
                location=location,
            )
            if effective_base_url:
                normalized_base_url = effective_base_url.strip()
                logger.info(f"Using custom GenAI base URL: {normalized_base_url}")
                client_kwargs["http_options"] = types.HttpOptions(base_url=normalized_base_url)

            self.client = genai.Client(**client_kwargs)
            current_model = Config.get_current_model()
            logger.info(
                f"Initialized VeoClient with auth mode: {effective_auth_mode}, "
                f"model: {current_model}, text model: {self.text_model}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize VeoClient: {e}")
            raise

    @staticmethod
    def _normalize_auth_mode(auth_mode):
        auth_mode = (auth_mode or "ai_studio").strip().lower().replace("-", "_")
        if auth_mode in ("google_ai_studio", "aistudio", "api_key"):
            return "ai_studio"
        if auth_mode in ("enterprise", "vertex", "vertexai", "service_account"):
            return "enterprise"
        raise ValueError("auth_mode must be ai_studio or enterprise")

    @staticmethod
    def _load_service_account_credentials(service_account_file):
        if not service_account_file:
            return None
        if not os.path.exists(service_account_file):
            raise FileNotFoundError(service_account_file)
        # 中文注释：Service Account 走 OAuth scope，适合企业/云项目权限控制。
        return service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

    def _build_client_kwargs(self, auth_mode, api_key=None, service_account_file=None, project=None, location=None):
        if auth_mode == "ai_studio":
            effective_api_key = api_key or Config.GOOGLE_API_KEY
            if not effective_api_key:
                raise ValueError("Google AI Studio API Key is required")
            return {"api_key": effective_api_key}

        effective_project = project or Config.GOOGLE_CLOUD_PROJECT
        effective_location = location or Config.GOOGLE_CLOUD_LOCATION
        effective_service_account_file = service_account_file or Config.GOOGLE_SERVICE_ACCOUNT_FILE

        if not effective_project:
            raise ValueError("Google Cloud project is required for enterprise authentication")
        if not effective_location:
            raise ValueError("Google Cloud location is required for enterprise authentication")

        client_kwargs = {
            "enterprise": True,
            "project": effective_project,
            "location": effective_location,
        }
        credentials = self._load_service_account_credentials(effective_service_account_file)
        if credentials:
            client_kwargs["credentials"] = credentials
        return client_kwargs

    def _load_prompt_template(self, relative_path):
        base_dir = os.path.dirname(__file__)
        path = os.path.join(base_dir, relative_path)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _extract_json(self, text):
        if not text:
            raise ValueError("Empty response")
        text = text.strip()
        if text.startswith("{") and text.endswith("}"):
            return json.loads(text)

        fenced_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL | re.IGNORECASE)
        if fenced_match:
            return json.loads(fenced_match.group(1))

        obj_match = re.search(r"(\{.*\})", text, flags=re.DOTALL)
        if obj_match:
            return json.loads(obj_match.group(1))

        raise ValueError("Failed to parse JSON from model response")

    def _build_output_filename(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        output_dir = os.path.join(Config.BASE_DIR, "output")
        os.makedirs(output_dir, exist_ok=True)
        return os.path.join(output_dir, f"generated_video_{timestamp}.mp4")

    def analyze_reference_video(self, reference_video_path, user_prompt=None, prompt_language="zh"):
        if not reference_video_path:
            raise ValueError("reference_video_path is required")
        if not os.path.exists(reference_video_path):
            raise FileNotFoundError(reference_video_path)

        upload_path = reference_video_path
        temp_dir = None
        try:
            try:
                upload_path.encode("ascii")
            except UnicodeEncodeError:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                project_temp_dir = os.path.join(base_dir, ".temp")
                if not os.path.exists(project_temp_dir):
                    os.makedirs(project_temp_dir)
                temp_dir = tempfile.mkdtemp(prefix="veo_reference_", dir=project_temp_dir)
                _, ext = os.path.splitext(reference_video_path)
                if not ext:
                    ext = ".mp4"
                upload_path = os.path.join(temp_dir, f"reference_video_{int(time.time())}{ext}")
                shutil.copy2(reference_video_path, upload_path)

            logger.info(f"Uploading reference video: {upload_path}")
            uploaded = self.client.files.upload(file=upload_path)
            
            logger.info(f"Waiting for file to be processed (current state: {uploaded.state})...")
            max_wait = 120
            wait_time = 0
            while uploaded.state != "ACTIVE" and wait_time < max_wait:
                time.sleep(2)
                uploaded = self.client.files.get(name=uploaded.name)
                logger.info(f"File state: {uploaded.state}")
                wait_time += 2
            
            if uploaded.state != "ACTIVE":
                raise RuntimeError(f"File processing timeout. Final state: {uploaded.state}")
            
            logger.info(f"File is ready (state: {uploaded.state})")
        finally:
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)
        model = self.text_model

        if (prompt_language or "").lower().startswith("en"):
            template_path = "prompts/reference_video_analysis_en.txt"
        else:
            template_path = "prompts/reference_video_analysis.txt"

        template = self._load_prompt_template(template_path)
        prompt = template.replace("{{user_prompt}}", user_prompt or "")

        logger.info("Analyzing reference video and generating copywriting...")
        response = self.client.models.generate_content(
            model=model,
            contents=[uploaded, prompt],
        )
        data = self._extract_json(getattr(response, "text", None))
        return data

    def generate_video_from_reference(
        self,
        reference_video_path,
        user_prompt,
        prompt_language="zh",
        aspect_ratio="16:9",
        person_generation="allow_adult",
        negative_prompt=None,
        seed=None,
        model_name=None,
    ):
        analysis = self.analyze_reference_video(reference_video_path, user_prompt=user_prompt, prompt_language=prompt_language)
        veo_prompt = analysis.get("veo_prompt")
        if not veo_prompt:
            raise ValueError("Model response missing 'veo_prompt'")

        final_prompt = veo_prompt
        video_path = self.generate_video(
            prompt=final_prompt,
            aspect_ratio=aspect_ratio,
            person_generation=person_generation,
            negative_prompt=negative_prompt,
            seed=seed,
            model_name=model_name,
        )

        return {
            "video_path": video_path,
            "analysis": analysis,
            "final_prompt": final_prompt,
        }

    def generate_video(
        self,
        prompt,
        aspect_ratio="16:9",
        person_generation="allow_adult",
        negative_prompt=None,
        seed=None,
        model_name=None,
    ):
        """
        Generates a video using the Veo model.
        
        Args:
            prompt (str): The text prompt for video generation.
            aspect_ratio (str): Aspect ratio "16:9" or "9:16".
            person_generation (str): "allow_adult" or "dont_allow".
            negative_prompt (str): Optional negative prompt.
            seed (int): Optional seed for generation.
            
        Returns:
            str: Path to the saved video file or None if failed.
        """
        logger.info(f"Starting video generation with prompt: '{prompt}'")
        
        try:
            # Configure generation options
            config_params = {
                "aspect_ratio": aspect_ratio,
            }
            
            # person_generation is currently not supported by the Veo 3.1 preview API
            # if person_generation and person_generation != "allow_adult":
            #     config_params["person_generation"] = person_generation
                
            if negative_prompt:
                config_params["negative_prompt"] = negative_prompt
            # Note: seed support depends on model version, add if supported by types.GenerateVideosConfig
            # Checking type definition or assuming kwargs if flexible. 
            # Based on search, seed is available for Veo 3 models.
            if seed is not None:
                config_params["seed"] = seed

            config = types.GenerateVideosConfig(**config_params)
            
            # Initiate generation
            current_model = model_name or Config.get_current_model() # Get latest selection
            operation = self.client.models.generate_videos(
                model=current_model,
                prompt=prompt,
                config=config
            )
            
            logger.info("Video generation request submitted. Waiting for completion...")
            
            # Poll for completion
            retry_count = 0
            max_retries = 5
            
            while not operation.done:
                time.sleep(5) # Poll every 5 seconds
                try:
                    operation = self.client.operations.get(operation)
                    retry_count = 0 # Reset retry count on success
                    logger.info("Status: Processing...")
                except Exception as e:
                    retry_count += 1
                    logger.warning(f"Network error during polling (attempt {retry_count}/{max_retries}): {e}")
                    if retry_count >= max_retries:
                        logger.error("Max retries exceeded. Aborting.")
                        raise e
                    time.sleep(2) # Wait a bit before retrying
                
            operation_error = getattr(operation, "error", None)
            if operation_error:
                raise RuntimeError(f"Video generation failed: {operation_error}")

            response = getattr(operation, "response", None)
            generated_videos = getattr(response, "generated_videos", None) if response else None
            if not generated_videos:
                logger.warning("Operation completed but no generated videos were returned.")
                return None

            video_file = generated_videos[0]
            filename = self._build_output_filename()

            logger.info(f"Downloading video to {filename}...")
            self.client.files.download(file=video_file.video)
            video_file.video.save(filename)

            logger.info(f"Video saved successfully: {filename}")
            return filename
                
        except Exception as e:
            logger.error(f"An error occurred during video generation: {e}")
            print(f"CRITICAL ERROR: {e}")
            # Re-raise exception so GUI can catch it and display it
            raise e
