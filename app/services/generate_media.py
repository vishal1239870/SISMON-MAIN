from google import genai
import os
from dotenv import load_dotenv
from app.services.generate_image import generate_image_from_prompt
from app.services.generate_video import generate_video_from_prompt

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

def generate_media_sequence(segments, output_dir="public/media"):
    """
    Generate all media (images and videos) from a list of segments
    
    Args:
        segments: List of segment dictionaries with keys:
                    - segment_number (int)
                    - type (str): "image" or "video"
                    - duration_seconds (int)
                    - prompt (str)
        output_dir: Directory to save all generated media
        
    Returns:
        List of dictionaries with segment info and file paths
    """
    print("\n" + "="*80)
    print("STARTING MEDIA GENERATION PIPELINE")
    print("="*80)
    print(f"Total segments to generate: {len(segments)}")
    
    # # Create output directory with timestamp
    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # output_dir = os.path.join(output_dir, f"sequence_{timestamp}")
    
    results = []
    
    # Validate video count
    video_count = sum(1 for s in segments if s['type'] == 'video')
    print(f"\nVideo count: {video_count}")
    if not (2 <= video_count <= 4 and video_count % 2 == 0):
        print("⚠️  WARNING: Video count should be 2 or 4 (even number)")
    
    # Generate each segment
    a,b=["",0,""],[]
    for segment in segments:
        segment_num = f"{segment['segment_number']}"
        media_type = segment['type']
        duration = segment['duration_seconds']
        prompt = segment['prompt']
        if media_type == 'image':
            filepath = generate_image_from_prompt(
                prompt=prompt,
                segment_number=segment_num,
                output_dir=output_dir
            )
        if media_type == 'video':
            filepath = generate_video_from_prompt(
                prompt=prompt,
                segment_number=segment_num,
                duration_seconds=duration,
                output_dir=output_dir
            )
            # if(a[0]==""):
            #     a[0]+=segment_num
            #     a[1]+=duration
            #     a[2]+=prompt
            # else:
            #     b.append((a[0]+segment_num,a[1]+duration,a[2]+"\n\nthen after a transition (at exact 4 sec) generate   \n" + prompt))
            #     a=["",0,""]
        # else:
        #     print(f"✗ Unknown media type: {media_type}")
        #     filepath = None
        
        results.append({
            'segment_number': segment_num,
            'type': media_type,
            'duration_seconds': duration,
            'filepath': filepath,
            'status': 'success' if filepath else 'failed'
        })
    # for segment in b:
    #     segment_num = segment[0]
    #     duration = segment[1]
    #     prompt = segment[2]
    #     filepath = generate_video_from_prompt(
    #         prompt=prompt,
    #         segment_number=segment_num,
    #         duration_seconds=duration,
    #         output_dir=output_dir
    #     )
    #     results.append({
    #         'segment_number': segment_num,
    #         'type': 'video',
    #         'duration_seconds': duration,
    #         'filepath': filepath,
    #         'status': 'success' if filepath else 'failed'
    #     })

    return results
