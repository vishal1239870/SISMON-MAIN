from moviepy import VideoFileClip, AudioFileClip

def add_audio_to_video(video_path, audio_path, output_path):
    """
    Replace or attach an audio track to a video using MoviePy.

    Parameters:
        video_path (str): Path to the input video file.
        audio_path (str): Path to the audio file to attach.
        output_path (str): Path to save the final video with audio.
    """
    # Load video and audio
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)

    # Set audio to video (replaces existing audio)
    video_with_audio = video.with_audio(audio)

    # Write output video
    video_with_audio.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac"
    )

    # Close clips
    video.close()
    audio.close()