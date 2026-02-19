from app.services import generate_prompts_from_prompt
from app.services import generate_script_from_prompt
from app.services import generate_voice_from_segments
from app.services import generate_media_sequence
from app.services import process_media_segments

from app.services import add_audio_to_video
from app.services import concatenate_media
from app.services import add_multiple_texts
from app.services import add_audio_to_video
from app.services import generate_media_sequence
from app.services import add_bgMusic_to_video


seg=generate_prompts_from_prompt("Make a 20-second promo video for a fitness app in a modern, energetic style")
script=generate_script_from_prompt(seg,"Make a 20-second promo video for a fitness app in a modern, energetic style")
# print(process_media_segments(seg,script))
generate_voice_from_segments(script,"public/audios/a.wav")
generate_media_sequence(seg,"public/media")

segement = process_media_segments(seg,script)
concatenate_media(segement[0], orientation='portrait')

add_multiple_texts(
    video_path="public/outputs/output.mp4",
    output_path="public/outputs/output_with_texts.mp4",
    texts=segement[1],
    font_size=47,
    color=(255,255,255,255),
    stroke_color="black",
    stroke_width=3,
    margin=(50, 100),
    )
add_audio_to_video("public/outputs/output_with_texts.mp4","public/audios/a.wav","public/outputs/output_with_audio.mp4")
add_bgMusic_to_video("public/outputs/output_with_audio.mp4","public/audios/bgMusic.mp3","public/outputs/final_output.mp4", bg_volume=0.08)
