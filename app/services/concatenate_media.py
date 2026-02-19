from moviepy import VideoFileClip, ImageClip, concatenate_videoclips
from app.services.apply_pan_effect import apply_pan_effect
from app.services.resize_and_center import resize_and_center
def concatenate_media(media_list, output_filename="public/outputs/output.mp4", orientation='portrait'):
    """
    Concatenates images and video clips based on the provided list.
    
    Args:
        media_list: List of tuples.
            - For images: ('image.jpg', duration_in_seconds, direction, intensity)
              direction can be: 'left', 'right', 'up', 'down', 'zoom_in', 'zoom_out', 'zoom', or None
              intensity is optional (default 1.15)
            - For videos: ('video.mp4', start_time, end_time)
        output_filename: Name for the output video file.
        orientation: 'portrait' or 'landscape'
    
    Example:
        media_list = [
            ('i1.jpg', 3, 'zoom_in', 1.2),  # Image with zoom effect
            ('v1.mp4', 2, 4),                # Video clip
            ('i2.jpg', 4, 'left'),           # Image panning left
            ('i3.jpg', 3, 'up', 1.3),        # Image panning up with custom intensity
        ]
    """
    clips = []
    
    # Set target dimensions based on orientation
    if orientation == 'portrait':
        target_width, target_height = 1080, 1920
    else:
        target_width, target_height = 1920, 1080
    
    for item in media_list:
        filename = item[0]
        
        # Determine if it's an image or video based on number of parameters
        if len(item) >= 2 and len(item) <= 4 and not isinstance(item[1], (int, float)) or (len(item) == 2):
            # This is ambiguous, default to image
            pass
        
        # Check if second parameter looks like a duration (for images) or start time (for videos)
        is_video = len(item) == 3 and isinstance(item[1], (int, float)) and isinstance(item[2], (int, float)) and item[2] > item[1]
        
        if is_video:  # Video
            start, end = item[1], item[2]
            video_clip = VideoFileClip(filename).subclipped(start, end)
            clip = resize_and_center(video_clip, target_width, target_height)
        
        else:  # Image with optional pan effect
            duration = item[1]
            direction = item[2] if len(item) > 2 else None
            intensity = item[3] if len(item) > 3 else 1.15
            
            img_clip = ImageClip(filename).with_duration(duration)
            
            if direction:
                clip = apply_pan_effect(img_clip, target_width, target_height, direction, intensity)
            else:
                clip = resize_and_center(img_clip, target_width, target_height)
        
        clips.append(clip)
    
    # Concatenate clips
    final_clip = concatenate_videoclips(clips, method='chain')
    
    # Write to file
    final_clip.write_videofile(
        output_filename,
        codec='libx264',
        audio_codec='aac',
        fps=30,
        preset='ultrafast',
        threads=8,
        bitrate='50k',
        audio_bitrate='2k',
        ffmpeg_params=['-crf', '23'],
        logger='bar'
    )
    
    # Close clips to free memory
    final_clip.close()
    for clip in clips:
        clip.close()
    
    print(f"Video saved as {output_filename}")

