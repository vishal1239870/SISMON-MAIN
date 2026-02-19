import random

def process_media_segments(visual_segments, script_segments):
    """
    Combines visual segments and script segments into the final lists for video generation.
    Each video segment will use its own file named "<segment_number>.mp4" (no clubbing).
    Returns:
        media_list: list of tuples for visuals
            - images: (filename, duration_seconds, 'zoom_in', zoom_amount)
            - videos: (filename, start_time, end_time)  # start_time=0, end_time=duration_seconds
        texts: list of tuples (script_text, start_time, end_time)
    """
    media_list = []
    texts = []

    # --- Build media_list (Visuals) ---
    for segment in visual_segments:
        s_type = segment['type'] if isinstance(segment, dict) else segment.type
        s_num = segment['segment_number'] if isinstance(segment, dict) else segment.segment_number
        s_duration = segment.get('duration_seconds') if isinstance(segment, dict) else getattr(segment, 'duration_seconds', None)

        if s_type == "image":
            # Format: (Filename, Duration, Effect, Zoom_Amount)
            filename = f"public/media/{s_num}.png"
            zoom_amount = round(random.uniform(1.1, 1.5), 2)
            media_list.append((filename, s_duration, 'zoom_in', zoom_amount))

        elif s_type == "video":
            # Use a separate file per segment number (no clubbing)
            filename = f"public/media/{s_num}.mp4"

            # If the segment provides duration_seconds, use it as end; otherwise default to 4s
            # (you can change the default as needed)
            if s_duration is None:
                s_duration = 4

            # Format: (Filename, Start_Time, End_Time)
            media_list.append((filename, 0, s_duration))

    # --- Build texts (Script/Overlay) ---
    for item in script_segments:
        script_text = item['script'] if isinstance(item, dict) else item.script
        start_time = item['start_time'] if isinstance(item, dict) else item.start_time
        end_time = item['end_time'] if isinstance(item, dict) else item.end_time

        # Remove all newlines and reformat with newline after every 6 words
        script_text = script_text.replace('\n', ' ')
        words = script_text.split()
        formatted_lines = []
        for i in range(0, len(words), 5):
            formatted_lines.append(' '.join(words[i:i+5]))
        script_text = '\n'.join(formatted_lines)

        texts.append((script_text, start_time, end_time))

    return media_list, texts
