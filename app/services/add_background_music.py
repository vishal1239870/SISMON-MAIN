from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip

def add_bgMusic_to_video(video_path, audio_path, output_path, bg_volume=0.05):
    """
    Add background music to video while keeping the original audio.
    Adjusts background music to match video duration (loops or truncates as needed).

    Parameters:
        video_path (str): Path to the input video file.
        audio_path (str): Path to the audio file to attach.
        output_path (str): Path to save the final video with audio.
        bg_volume (float): Volume multiplier for background music (0.0 to 1.0).
                          Default is 0.05 (5% of original volume).
    """
    # Load video and background audio
    video = VideoFileClip(video_path)
    bg_audio = AudioFileClip(audio_path)
    
    video_duration = video.duration
    audio_duration = bg_audio.duration
    
    # Adjust background music to match video duration
    if audio_duration > video_duration:
        # If audio is longer, trim it to video duration
        bg_audio = bg_audio.subclipped(0, video_duration)
    elif audio_duration < video_duration:
        # If audio is shorter, loop it to match video duration
        num_loops = int(video_duration / audio_duration) + 1
        bg_audio = bg_audio.loop(n=num_loops).subclipped(0, video_duration)
    
    # Reduce background music volume
    bg_audio_lowered = bg_audio.with_volume_scaled(bg_volume)
    
    # Get the original video audio
    original_audio = video.audio
    
    # Mix original audio with background music
    if original_audio is not None:
        mixed_audio = CompositeAudioClip([original_audio, bg_audio_lowered])
    else:
        # If video has no audio, just use background music
        mixed_audio = bg_audio_lowered
    
    # Set mixed audio to video
    video_with_audio = video.with_audio(mixed_audio)
    
    # Write output video
    video_with_audio.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac"
    )
    
    # Close clips
    video.close()
    bg_audio.close()
