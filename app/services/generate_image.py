from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)
    
def generate_image_from_prompt(prompt, segment_number, output_dir="public/media"):

    print(f"\n{'='*80}")
    print(f"Generating IMAGE for Segment {segment_number}")
    print(f"{'='*80}")
    print(f"Prompt: {prompt[:100]}...")
    
    try:
        # response = client.models.generate_images(
        #     model='gemini-2.5-flash-image',
        #     prompt=prompt,
        #     config=types.GenerateImagesConfig(
        #         number_of_images=1, 
        #     )
        # )
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt,  # Or [prompt] if passing as a list
            config=types.GenerateContentConfig(
                response_modalities=['Image'],
            )
        )
        
        # os.makedirs(output_dir, exist_ok=True)
        
        # Save the generated image
        # for idx, generated_image in enumerate(response.generated_images):
        #     filename = f"{segment_number:02d}.png"
        #     filepath = os.path.join(output_dir, filename)
            
        #     # Save the image
        #     generated_image.image.save(filepath)
        #     print(f"✓ Image saved: {filepath}")
            
        #     # Optionally display the image
        #     # generated_image.image.show()
            
        #     return filepath
        image_saved = False
        for idx, part in enumerate(response.parts):
            if part.inline_data is not None:
                # Convert inline data to PIL Image
                generated_image = part.as_image()
                
                filename = f"{segment_number}.png"
                filepath = os.path.join(output_dir, filename)
                
                # Save the image
                generated_image.save(filepath)
                print(f"✓ Image saved: {filepath}")
                
                image_saved = True
                break  # Stop after first image (single output)
            elif part.text is not None:
                print(f"Text output: {part.text}")  # Fallback for any text
        
        if not image_saved:
            raise ValueError("No image generated in response.")
            
    except Exception as e:
        print(f"✗ Error generating image: {str(e)}")
        return None
