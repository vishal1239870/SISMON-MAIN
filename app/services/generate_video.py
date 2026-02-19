# import requests
# import os
# import time  # For polling delays

# def download_file(url, filename, output_dir="public/media"):
#     """Download file from URL and save locally"""
#     # Create output directory if it doesn't exist
#     os.makedirs(output_dir, exist_ok=True)
#     filepath = os.path.join(output_dir, filename)
    
#     print(f"Downloading video from {url} to {filepath}...")
#     response = requests.get(url, stream=True)
#     response.raise_for_status()
    
#     with open(filepath, 'wb') as f:
#         for chunk in response.iter_content(chunk_size=8192):
#             f.write(chunk)
    
#     print(f"✓ Video saved: {filepath}")
#     return filepath

# def generate_video_from_prompt(prompt, segment_number, duration_seconds=5, aspect_ratio="9:16", output_dir="public/media"):
#     """
#     Generate a video from a prompt using Kie.ai Runway API (async with polling).
    
#     Args:
#         prompt: Text prompt for video generation
#         segment_number: Segment number for naming
#         duration_seconds: Duration of the video (5 or 10 seconds only)
#         aspect_ratio: Video aspect ratio (e.g., "16:9", "9:16"). Default: "16:9"
#         output_dir: Directory to save the video
        
#     Returns:
#         Path to the saved video file, or None on failure
#     """
#     print(f"\n{'='*80}")
#     print(f"Generating VIDEO for Segment {segment_number} ({duration_seconds}s)")
#     print(f"{'='*80}")
#     print(f"Prompt: {prompt[:100]}...")
    
#     try:
#         url = "https://api.kie.ai/api/v1/runway/generate"

#         payload = {
#             "prompt": prompt,
#             "model": "runway-duration-5-generate",  # Adjust if needed for 10s
#             "callBackUrl": "https://api.example.com/callback",
#             "duration": duration_seconds,
#             "quality": "720p",
#             "aspectRatio": aspect_ratio,
#             "waterMark": ""  # Set to "" for no watermark, or e.g., "your-brand"
#         }
#         headers = {
#             "Authorization": f"Bearer {os.getenv('KIE_API_KEY')}",
#             "Content-Type": "application/json"
#         }

#         # Start the generation job
#         response = requests.post(url, json=payload, headers=headers)
#         response.raise_for_status()
#         api_data = response.json()
        
#         if api_data.get("code") != 200:
#             print(f"✗ API error starting job: {api_data.get('msg', 'Unknown error')}")
#             return None
        
#         task_id = api_data.get("data", {}).get("taskId")
#         if not task_id:
#             print("✗ No taskId returned from API.")
#             return None
        
#         print(f"✓ Job started with taskId: {task_id}")
#         print("Polling for completion...")

#         # Poll for status
#         status_url = f"https://api.kie.ai/api/v1/runway/record-detail?taskId={task_id}"
#         max_polls = 60  # ~5-10 min max wait; adjust as needed
#         poll_interval = 10  # seconds between polls
        
#         for attempt in range(max_polls):
#             status_response = requests.get(status_url, headers=headers)
#             status_response.raise_for_status()
#             status_data = status_response.json()
            
#             if status_data.get("code") != 200:
#                 print(f"✗ Status check failed: {status_data.get('msg', 'Unknown error')}")
#                 return None
            
#             state = status_data.get("data", {}).get("state")
#             print(f"Poll {attempt + 1}/{max_polls}: State = {state}")
            
#             if state == "success":
#                 video_info = status_data.get("data", {}).get("videoInfo", {})
#                 video_url = video_info.get("videoUrl")
#                 if video_url:
#                     video_filename = f"{segment_number}.mp4"
#                     return download_file(video_url, video_filename, output_dir)
#                 else:
#                     print("✗ No videoUrl in successful response.")
#                     return None
#             elif state in ["failed", "error"]:
#                 error_msg = status_data.get("data", {}).get("errorMsg", "Unknown error")
#                 print(f"✗ Job failed: {error_msg}")
#                 return None
            
#             # Still processing; wait and retry
#             if attempt < max_polls - 1:
#                 time.sleep(poll_interval)
        
#         print("✗ Timeout: Job took too long to complete.")
#         return None
        
#     except requests.exceptions.RequestException as e:
#         print(f"✗ Network/API error: {str(e)}")
#         return None
#     except Exception as e:
#         print(f"✗ Unexpected error: {str(e)}")
#         return None


import requests
import os
import time  # For polling delays

def download_file(url, filename, output_dir="public/media"):
    """Download file from URL and save locally"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
    print(f"Downloading video from {url} to {filepath}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"✓ Video saved: {filepath}")
    return filepath

def get_api_keys():
    """Get all available API keys from environment variables"""
    api_keys = []
    for i in range(1, 5):  # KIE_API_KEY1 through KIE_API_KEY6
        key = os.getenv(f'KIE_API_KEY{i}')
        if key:
            api_keys.append(key)
    return api_keys

def is_rate_limit_error(api_data):
    """Check if the error indicates a rate limit/quota exceeded"""
    if api_data.get("code") != 200:
        msg = api_data.get("msg", "").lower()
        # Check for common rate limit error messages
        rate_limit_indicators = ["limit", "quota", "exceeded", "rate", "too many"]
        return any(indicator in msg for indicator in rate_limit_indicators)
    return False

def generate_video_from_prompt(prompt, segment_number, duration_seconds=5, aspect_ratio="9:16", output_dir="public/media"):
    """
    Generate a video from a prompt using Kie.ai Runway API (async with polling).
    Automatically falls back to alternate API keys if rate limit is exceeded.
    
    Args:
        prompt: Text prompt for video generation
        segment_number: Segment number for naming
        duration_seconds: Duration of the video (5 or 10 seconds only)
        aspect_ratio: Video aspect ratio (e.g., "16:9", "9:16"). Default: "9:16"
        output_dir: Directory to save the video
        
    Returns:
        Path to the saved video file, or None on failure
    """
    print(f"\n{'='*80}")
    print(f"Generating VIDEO for Segment {segment_number} ({duration_seconds}s)")
    print(f"{'='*80}")
    print(f"Prompt: {prompt[:100]}...")
    
    api_keys = get_api_keys()
    if not api_keys:
        print("✗ No API keys found in environment variables (KIE_API_KEY1-6)")
        return None
    
    print(f"Found {len(api_keys)} API key(s)")
    
    # Try each API key in sequence
    for key_index, api_key in enumerate(api_keys, 1):
        print(f"\n--- Attempting with API Key #{key_index} ---")
        
        try:
            url = "https://api.kie.ai/api/v1/runway/generate"

            payload = {
                "prompt": prompt,
                "model": "runway-duration-5-generate",  # Adjust if needed for 10s
                "callBackUrl": "https://api.example.com/callback",
                "duration": duration_seconds,
                "quality": "720p",
                "aspectRatio": aspect_ratio,
                "waterMark": ""  # Set to "" for no watermark, or e.g., "your-brand"
            }
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            # Start the generation job
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            api_data = response.json()
            
            # Check for rate limit error
            # if is_rate_limit_error(api_data):
            #     print(f"✗ Rate limit exceeded for API Key #{key_index}: {api_data.get('msg', 'Unknown error')}")
            #     if key_index < len(api_keys):
            #         print(f"→ Switching to next API key and retrying same video...")
            #         continue  # Try next API key for the SAME video
            #     else:
            #         print("✗ All API keys exhausted")
            #         return None
            
            if api_data.get("code") != 200:
                print(f"✗ Rate limit exceeded for API Key #{key_index}: {api_data.get('msg', 'Unknown error')}")
                if key_index < len(api_keys):
                    print(f"→ Switching to next API key and retrying same video...")
                    continue  # Try next API key for the SAME video
                else:
                    print("✗ All API keys exhausted")
                    return None
            
            task_id = api_data.get("data", {}).get("taskId")
            if not task_id:
                print("✗ No taskId returned from API.")
                return None
            
            print(f"✓ Job started with taskId: {task_id}")
            print("Polling for completion...")

            # Poll for status
            status_url = f"https://api.kie.ai/api/v1/runway/record-detail?taskId={task_id}"
            max_polls = 60  # ~5-10 min max wait; adjust as needed
            poll_interval = 10  # seconds between polls
            
            for attempt in range(max_polls):
                status_response = requests.get(status_url, headers=headers)
                status_response.raise_for_status()
                status_data = status_response.json()
                
                if status_data.get("code") != 200:
                    print(f"✗ Status check failed: {status_data.get('msg', 'Unknown error')}")
                    return None
                
                state = status_data.get("data", {}).get("state")
                print(f"Poll {attempt + 1}/{max_polls}: State = {state}")
                
                if state == "success":
                    video_info = status_data.get("data", {}).get("videoInfo", {})
                    video_url = video_info.get("videoUrl")
                    if video_url:
                        video_filename = f"{segment_number}.mp4"
                        return download_file(video_url, video_filename, output_dir)
                    else:
                        print("✗ No videoUrl in successful response.")
                        return None
                elif state in ["failed", "error"]:
                    error_msg = status_data.get("data", {}).get("errorMsg", "Unknown error")
                    print(f"✗ Job failed: {error_msg}")
                    return None
                
                # Still processing; wait and retry
                if attempt < max_polls - 1:
                    time.sleep(poll_interval)
            
            print("✗ Timeout: Job took too long to complete.")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Network/API error with Key #{key_index}: {str(e)}")
            # Check if it's a 429 (rate limit) status code
            if hasattr(e.response, 'status_code') and e.response.status_code == 429:
                if key_index < len(api_keys):
                    print(f"→ Switching to next API key...")
                    continue
                else:
                    print("✗ All API keys exhausted")
                    return None
            return None
        except Exception as e:
            print(f"✗ Unexpected error: {str(e)}")
            return None
    
    print("✗ All API keys failed")
    return None