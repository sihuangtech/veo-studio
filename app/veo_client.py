import json
import os
import re
import shutil
import tempfile
import time
from google import genai
from google.genai import types
from .config import Config
from .utils import setup_logger

logger = setup_logger("VeoClient")

class VeoClient:
    def __init__(self):
        try:
            if Config.HTTPS_PROXY:
                logger.info(f"Using proxy: {Config.HTTPS_PROXY}")
                # Ensure it's set in os.environ for underlying libraries
                os.environ["HTTPS_PROXY"] = Config.HTTPS_PROXY
                os.environ["HTTP_PROXY"] = Config.HTTPS_PROXY

            client_kwargs = {"api_key": Config.GOOGLE_API_KEY}
            if Config.GOOGLE_GENAI_BASE_URL:
                base_url = Config.GOOGLE_GENAI_BASE_URL.strip()
                logger.info(f"Using custom GenAI base URL: {base_url}")
                client_kwargs["http_options"] = types.HttpOptions(base_url=base_url)

            self.client = genai.Client(**client_kwargs)
            current_model = Config.get_current_model()
            logger.info(f"Initialized VeoClient with model: {current_model}")
        except Exception as e:
            logger.error(f"Failed to initialize VeoClient: {e}")
            raise

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
        finally:
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)
        model = Config.GEMINI_TEXT_MODEL

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
        )

        return {
            "video_path": video_path,
            "analysis": analysis,
            "final_prompt": final_prompt,
        }

    def generate_video(self, prompt, aspect_ratio="16:9", person_generation="allow_adult", negative_prompt=None, seed=None):
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
            current_model = Config.get_current_model() # Get latest selection
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
                
            if operation.result:
                generated_videos = operation.response.generated_videos
                if not generated_videos:
                    logger.warning("No videos were generated.")
                    return None
                
                # Save the first video
                video_file = generated_videos[0]
                timestamp = int(time.time())
                
                # Ensure output directory exists
                output_dir = "output"
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                    
                filename = os.path.join(output_dir, f"generated_video_{timestamp}.mp4")
                
                logger.info(f"Downloading video to {filename}...")
                self.client.files.download(file=video_file.video)
                video_file.video.save(filename)
                
                logger.info(f"Video saved successfully: {filename}")
                return filename
            else:
                logger.error("Operation completed but no result found.")
                return None
                
        except Exception as e:
            logger.error(f"An error occurred during video generation: {e}")
            print(f"CRITICAL ERROR: {e}")
            # Re-raise exception so GUI can catch it and display it
            raise e
