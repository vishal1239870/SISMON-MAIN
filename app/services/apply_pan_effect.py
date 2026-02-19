from moviepy import ColorClip, CompositeVideoClip, vfx

def apply_pan_effect(clip, target_width, target_height, direction='zoom', intensity=1.15):
    """
    Applies a slow pan/zoom effect to an image clip while ensuring frame is always covered.
    
    Args:
        clip: The image clip to animate
        target_width: Target width for the output
        target_height: Target height for the output
        direction: 'left', 'right', 'up', 'down', 'zoom_in', 'zoom_out', 'zoom' (alias for zoom_in)
        intensity: How much to scale/move (1.15 = 15% larger/movement)
    """
    clip_width, clip_height = clip.size
    duration = clip.duration
    clip_aspect = clip_width / clip_height
    target_aspect = target_width / target_height
    
    # First, scale image to COVER the frame (matching the larger dimension needed)
    if clip_aspect > target_aspect:
        # Clip is wider, match HEIGHT
        base_height = target_height
        base_width = int(target_height * clip_aspect)
    else:
        # Clip is taller, match WIDTH
        base_width = target_width
        base_height = int(target_width / clip_aspect)
    
    # Scale up further by intensity to allow for movement while staying covered
    scale_factor = intensity
    scaled_width = int(base_width * scale_factor)
    scaled_height = int(base_height * scale_factor)
    
    # Apply zoom effects
    if direction in ['zoom_in', 'zoom']:
        def zoom_func(t):
            progress = t / duration
            # Start at base size (covering frame), end at scaled size
            start_w, start_h = base_width, base_height
            end_w, end_h = scaled_width, scaled_height
            current_w = int(start_w + (end_w - start_w) * progress)
            current_h = int(start_h + (end_h - start_h) * progress)
            return (current_w, current_h)
        
        def position_func(t):
            current_size = zoom_func(t)
            x = -(current_size[0] - target_width) // 2
            y = -(current_size[1] - target_height) // 2
            return (x, y)
        
        animated_clip = clip.with_effects([vfx.Resize(zoom_func)]).with_position(position_func)
        
    elif direction == 'zoom_out':
        def zoom_func(t):
            progress = t / duration
            # Start at scaled size, end at base size (covering frame)
            start_w, start_h = scaled_width, scaled_height
            end_w, end_h = base_width, base_height
            current_w = int(start_w - (start_w - end_w) * progress)
            current_h = int(start_h - (start_h - end_h) * progress)
            return (current_w, current_h)
        
        def position_func(t):
            current_size = zoom_func(t)
            x = -(current_size[0] - target_width) // 2
            y = -(current_size[1] - target_height) // 2
            return (x, y)
        
        animated_clip = clip.with_effects([vfx.Resize(zoom_func)]).with_position(position_func)
    
    else:
        # Pan effects - use scaled size
        scaled_clip = clip.resized((scaled_width, scaled_height))
        
        def position_func(t):
            progress = t / duration  # 0 to 1
            
            if direction == 'left':
                # Pan from right to left
                max_offset = scaled_width - target_width
                x = -int(max_offset * progress)
                y = -(scaled_height - target_height) // 2
                
            elif direction == 'right':
                # Pan from left to right
                max_offset = scaled_width - target_width
                x = -int(max_offset * (1 - progress))
                y = -(scaled_height - target_height) // 2
                
            elif direction == 'up':
                # Pan from bottom to top
                max_offset = scaled_height - target_height
                x = -(scaled_width - target_width) // 2
                y = -int(max_offset * progress)
                
            elif direction == 'down':
                # Pan from top to bottom
                max_offset = scaled_height - target_height
                x = -(scaled_width - target_width) // 2
                y = -int(max_offset * (1 - progress))
            
            else:
                # No movement (center)
                x = -(scaled_width - target_width) // 2
                y = -(scaled_height - target_height) // 2
            
            return (x, y)
        
        animated_clip = scaled_clip.with_position(position_func)
    
    # Create background and composite
    bg = ColorClip(size=(target_width, target_height), 
                   color=(0, 0, 0), 
                   duration=duration)
    
    final = CompositeVideoClip([bg, animated_clip], size=(target_width, target_height))
    
    return final

