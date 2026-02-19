import streamlit as st
import time
import os
from pathlib import Path

# Import your services
from app.services import (
    generate_prompts_from_prompt,
    generate_script_from_prompt,
    generate_voice_from_segments,
    generate_media_sequence,
    process_media_segments,
    concatenate_media,
    add_multiple_texts,
    add_audio_to_video,
    add_bgMusic_to_video
)

# Page configuration
st.set_page_config(
    page_title="AI Video Generator",
    page_icon="🎬",
    layout="wide"
)

# Title and description
st.title("🎬 CineMorph: AI Powered Video Generator")
st.markdown("Generate professional videos from text prompts using AI")

# Create necessary directories if they don't exist
Path("public/audios").mkdir(parents=True, exist_ok=True)
Path("public/media").mkdir(parents=True, exist_ok=True)
Path("public/outputs").mkdir(parents=True, exist_ok=True)

# Initialize session state
if 'video_generated' not in st.session_state:
    st.session_state.video_generated = False
if 'video_path' not in st.session_state:
    st.session_state.video_path = None
if 'generation_time' not in st.session_state:
    st.session_state.generation_time = 0

# Input section
st.markdown("### 📝 Enter Your Prompt")
user_prompt = st.text_area(
    "Describe the video you want to create:",
    placeholder="Example: Make a 20-second promo video for a fitness app in a modern, energetic style",
    height=100
)

# Generate button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_button = st.button("🚀 Generate Video", use_container_width=True, type="primary")

# Video generation process
if generate_button and user_prompt:
    st.session_state.video_generated = False
    st.session_state.video_path = None
    
    # Progress container
    progress_container = st.container()
    
    with progress_container:
        st.markdown("### 🔄 Generating Your Video...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        timer_text = st.empty()
        
        # Start timer
        start_time = time.time()
        
        try:
            # Step 1: Generate prompts
            status_text.text("⏳ Step 1/8: Generating prompts...")
            progress_bar.progress(10)
            seg = generate_prompts_from_prompt(user_prompt)
            
            # Step 2: Generate script
            status_text.text("⏳ Step 2/8: Creating script...")
            progress_bar.progress(20)
            script = generate_script_from_prompt(seg, user_prompt)
            
            # Step 3: Generate voice
            status_text.text("⏳ Step 3/8: Generating voiceover...")
            progress_bar.progress(35)
            audio_path = "public/audios/a.wav"
            generate_voice_from_segments(script, audio_path)
            
            # Step 4: Generate media sequence
            status_text.text("⏳ Step 4/8: Creating media sequence...")
            progress_bar.progress(50)
            generate_media_sequence(seg, "public/media")
            
            # Step 5: Process media segments
            status_text.text("⏳ Step 5/8: Processing media segments...")
            progress_bar.progress(60)
            segment = process_media_segments(seg, script)
            
            # Step 6: Concatenate media
            status_text.text("⏳ Step 6/8: Concatenating media...")
            progress_bar.progress(70)
            concatenate_media(segment[0], orientation='portrait')
            
            # Step 7: Add text overlays
            status_text.text("⏳ Step 7/8: Adding text overlays...")
            progress_bar.progress(80)
            add_multiple_texts(
                video_path="public/outputs/output.mp4",
                output_path="public/outputs/output_with_texts.mp4",
                texts=segment[1],
                font_size=47,
                color=(255, 255, 255, 255),
                stroke_color="black",
                stroke_width=3,
                margin=(50, 100),
            )
            
            # Step 8: Add audio
            status_text.text("⏳ Step 8/8: Adding audio...")
            progress_bar.progress(90)
            add_audio_to_video(
                "public/outputs/output_with_texts.mp4",
                audio_path,
                "public/outputs/output_with_audio.mp4"
            )
            
            # Step 9: Add background music (if exists)
            status_text.text("⏳ Final step: Adding background music...")
            progress_bar.progress(95)
            final_output_path = "public/outputs/final_output.mp4"
            
            if os.path.exists("public/audios/bgMusic.mp3"):
                add_bgMusic_to_video(
                    "public/outputs/output_with_audio.mp4",
                    "public/audios/bgMusic.mp3",
                    final_output_path,
                    bg_volume=0.08
                )
            else:
                # If no background music, use the audio version as final
                os.rename("public/outputs/output_with_audio.mp4", final_output_path)
            
            # Complete
            progress_bar.progress(100)
            end_time = time.time()
            generation_time = end_time - start_time
            
            st.session_state.video_generated = True
            st.session_state.video_path = final_output_path
            st.session_state.generation_time = generation_time
            
            status_text.empty()
            progress_bar.empty()
            
            # Success message
            st.success(f"✅ Video generated successfully in {generation_time:.2f} seconds!")
            
        except Exception as e:
            st.error(f"❌ Error generating video: {str(e)}")
            st.exception(e)

# Display generated video
if st.session_state.video_generated and st.session_state.video_path:
    st.markdown("---")
    st.markdown("### 🎥 Your Generated Video")
    
    # Display generation time
    st.info(f"⏱️ Generation Time: {st.session_state.generation_time:.2f} seconds")
    
    # Display video with custom dimensions
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        # Add custom CSS to control video size
        st.markdown("""
            <style>
            .custom-video video {
                max-width: 200px;
                max-height: 356px;
                width: 200px;
                height: 356px;
                margin: 0 auto;
                display: block;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            </style>
        """, unsafe_allow_html=True)
        
        if os.path.exists(st.session_state.video_path):
            # Wrap video in a div with custom class
            st.markdown('<div class="custom-video">', unsafe_allow_html=True)
            
            video_file = open(st.session_state.video_path, 'rb')
            video_bytes = video_file.read()
            st.video(video_bytes)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Download button
            st.download_button(
                label="⬇️ Download Video",
                data=video_bytes,
                file_name="generated_video.mp4",
                mime="video/mp4",
                use_container_width=True
            )
        else:
            st.error("Video file not found!")

# Footer
st.markdown("---")