from moviepy import  ColorClip, CompositeVideoClip

def resize_and_center(clip, target_width, target_height):
    """
    Resizes clip to cover the entire target dimensions while maintaining aspect ratio,
    then centers it (cropping excess if necessary).
    """
    clip_width, clip_height = clip.size
    clip_aspect = clip_width / clip_height
    target_aspect = target_width / target_height
    
    if clip_aspect > target_aspect:
        new_height = target_height
        new_width = int(target_height * clip_aspect)
    else:
        new_width = target_width
        new_height = int(target_width / clip_aspect)
    
    resized_clip = clip.resized((new_width, new_height))
    
    x_center = (target_width - new_width) // 2
    y_center = (target_height - new_height) // 2
    
    bg = ColorClip(size=(target_width, target_height), 
                   color=(0, 0, 0), 
                   duration=resized_clip.duration)
    
    resized_clip = resized_clip.with_position((x_center, y_center))
    final = CompositeVideoClip([bg, resized_clip], size=(target_width, target_height))
    
    return final

