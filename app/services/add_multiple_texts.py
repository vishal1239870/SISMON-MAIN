from moviepy import VideoFileClip, CompositeVideoClip, vfx, TextClip
import os

def add_multiple_texts(
    video_path,
    output_path,
    texts,
    font=os.path.join(os.getcwd(), "public/fonts/font1.ttf"),
    font_size=40,
    color='white',
    bg_color=None,
    stroke_color=None,
    stroke_width=0,
    method='caption',
    text_align='center',
    horizontal_align='center',
    vertical_align='bottom',
    size=(800, None),
    margin=(10, 10),
    interline=4,
    transparent=True,
):
    video = VideoFileClip(video_path)
    text_clips = []

    def zoom_in(t):
        zoom_duration = 0.3
        start_scale = 1.2
        end_scale = 1.0
        if t >= zoom_duration:
            return end_scale
        return start_scale - (start_scale - end_scale) * (t / zoom_duration)

    for text_content, start_time, end_time in texts:
        duration = end_time - start_time

        txt = TextClip(
            text=text_content,
            font=font,
            font_size=font_size,
            color=color,
            bg_color=bg_color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            method=method,
            text_align=text_align,
            horizontal_align=horizontal_align,
            vertical_align=vertical_align,
            size=size,
            margin=margin,
            interline=interline,
            transparent=transparent
        )

        txt = (
            txt.with_position((horizontal_align, vertical_align))
               .with_start(start_time)
               .with_duration(duration)
               .with_effects([
                   vfx.CrossFadeIn(0.1),
                   vfx.CrossFadeOut(0.1),
                   vfx.Resize(zoom_in),
               ])
        )

        text_clips.append(txt)

    final = CompositeVideoClip([video] + text_clips)

    final.write_videofile(
        output_path,
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

    video.close()
    for c in text_clips:
        c.close()
    final.close()

