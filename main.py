import sys
from config import Config
from veo_client import VeoClient
from utils import setup_logger

logger = setup_logger("Main")

def main():
    print("=== Google Veo Video Generation Studio ===")
    
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        logger.error(str(e))
        print(f"\nError: {e}")
        print("Please create a .env file with your GOOGLE_API_KEY.")
        sys.exit(1)
        
    try:
        client = VeoClient()
    except Exception:
        sys.exit(1)
        
    while True:
        print("\n--- New Video Generation Task ---")
        prompt = input("Enter your video prompt (or 'q' to quit): ").strip()
        
        if prompt.lower() == 'q':
            print("Exiting...")
            break
            
        if not prompt:
            print("Prompt cannot be empty.")
            continue
            
        # Get optional parameters
        print("\nOptional Parameters (press Enter to use default):")
        
        ar_input = input("Aspect Ratio [16:9]: ").strip()
        aspect_ratio = ar_input if ar_input else "16:9"
        
        pg_input = input("Person Generation [allow_adult]: ").strip()
        person_generation = pg_input if pg_input else "allow_adult"
        
        print("\nGenerating video... This may take a while.")
        
        result_path = client.generate_video(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            person_generation=person_generation
        )
        
        if result_path:
            print(f"\nSUCCESS: Video generated at {result_path}")
        else:
            print("\nFAILED: Video generation failed. Check logs for details.")

if __name__ == "__main__":
    main()
