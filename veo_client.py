import time
from google import genai
from google.genai import types
from config import Config
from utils import setup_logger

logger = setup_logger("VeoClient")

class VeoClient:
    def __init__(self):
        try:
            if Config.HTTPS_PROXY:
                logger.info(f"Using proxy: {Config.HTTPS_PROXY}")
                # Ensure it's set in os.environ for underlying libraries
                import os
                os.environ["HTTPS_PROXY"] = Config.HTTPS_PROXY
                os.environ["HTTP_PROXY"] = Config.HTTPS_PROXY
            
            self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)
            logger.info(f"Initialized VeoClient with model: {Config.VEO_MODEL_NAME}")
        except Exception as e:
            logger.error(f"Failed to initialize VeoClient: {e}")
            raise

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
            operation = self.client.models.generate_videos(
                model=Config.VEO_MODEL_NAME,
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
                import os
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
