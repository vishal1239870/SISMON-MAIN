from google import genai
from google.genai import types
import wave
import os
import subprocess
import shutil

# ---------------------------
# Utilities: save wav & transcript
# ---------------------------

def save_wav(filename, pcm, channels=1, rate=24000, sample_width=2):
    """Save PCM data as WAV file (raw PCM bytes from API)."""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)

def build_transcript(segments):
    """Convert timestamped segments to plain transcript string"""
    return " ".join(seg["script"] for seg in segments)

# ---------------------------
# FFmpeg helpers
# ---------------------------

def _ffprobe_duration(path):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path
    ]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {path}: {p.stderr.strip()}")
    return float(p.stdout.strip())

def _run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return p.returncode, p.stdout, p.stderr

# ---------------------------
# New adjuster using ffmpeg (policy aware)
# ---------------------------

def adjust_audio_policy(input_file, output_file, target_duration,
                        max_speed_for_stretch=2.0,
                        allow_trim_when_too_fast=True):
    """
    Adjust audio to exact target_duration using ffmpeg.
    - Keeps a temp WAV for the atempo chain
    - Converts temp WAV to final codec (wav or mp3) with proper encoder args
    Policy:
      - If target_duration > original -> stretch (slow down) using atempo chain (net < 1)
      - If target_duration < original and speed <= max_speed_for_stretch -> speed up via atempo chain
      - If target_duration < original and speed > max_speed_for_stretch and allow_trim_when_too_fast -> trim instead
    Returns final saved duration in seconds.
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Determine final output encoder args
    ext = os.path.splitext(output_file)[1].lower()
    if ext == ".wav":
        output_args = ["-acodec", "pcm_s16le"]
    elif ext == ".mp3":
        output_args = ["-codec:a", "libmp3lame", "-b:a", "192k"]
    else:
        # allow other extensions but recommend .wav or .mp3
        raise ValueError(f"Unsupported output format: {ext}. Use .wav or .mp3")

    orig_dur = _ffprobe_duration(input_file)
    print(f"Original duration: {orig_dur:.3f}s target: {target_duration:.3f}s")

    # If already very close just copy
    if abs(orig_dur - target_duration) < 0.01:
        print("Duration within 10ms. Copying file.")
        shutil.copy(input_file, output_file)
        return orig_dur

    speed = orig_dur / target_duration
    print(f"Computed speed factor (orig/target) = {speed:.6f}")

    # Decide net atempo factor (what ffmpeg atempo should implement)
    if target_duration > orig_dur:
        # need to slow down => net < 1
        net = 1.0 / speed
        print("Target longer than original -> will slow down (net atempo < 1)")
    else:
        if speed <= max_speed_for_stretch:
            net = speed
            print(f"Target shorter but within speed threshold ({max_speed_for_stretch}) -> speed up (net atempo)")
        else:
            # too big a speed change requested
            print(f"Required speed {speed:.2f} exceeds max allowed {max_speed_for_stretch}")
            if allow_trim_when_too_fast:
                # Trim the original to requested duration (prefer naturalness over aggressive speeding)
                print("Policy: trimming original file to the target duration (no aggressive speeding).")
                cmd_trim = [
                    "ffmpeg", "-y", "-i", input_file,
                    "-t", f"{target_duration:.6f}"
                ] + output_args + [output_file]
                code, out, err = _run(cmd_trim)
                if code != 0:
                    raise RuntimeError(f"ffmpeg trim failed:\n{err}")
                final = _ffprobe_duration(output_file)
                print(f"Trimmed and saved {output_file} duration {final:.6f}s")
                return final
            else:
                print("Policy: allow aggressive atempo chaining (may sound unnatural).")
                net = speed

    # Build atempo chain (ffmpeg atempo supports 0.5..2.0 per filter)
    remaining = net
    factors = []
    while remaining > 2.0:
        factors.append(2.0)
        remaining /= 2.0
    while remaining < 0.5:
        factors.append(0.5)
        remaining /= 0.5
    factors.append(remaining)
    factors = [max(0.5, min(2.0, float(f))) for f in factors]
    filter_chain = ",".join(f"atempo={f:.6f}" for f in factors)
    print("FFmpeg atempo filter chain:", filter_chain)

    # run atempo into a temp PCM WAV (safe intermediate)
    temp_output = output_file + ".tmp.wav"
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", input_file,
        "-filter:a", filter_chain,
        "-acodec", "pcm_s16le",
        temp_output
    ]
    code, out, err = _run(ffmpeg_cmd)
    if code != 0:
        raise RuntimeError(f"ffmpeg atempo failed:\n{err}")

    new_dur = _ffprobe_duration(temp_output)
    print(f"After atempo chain duration: {new_dur:.6f}s")

    # If close to target just convert temp -> final codec
    if abs(new_dur - target_duration) < 0.01:
        conv_cmd = ["ffmpeg", "-y", "-i", temp_output] + output_args + [output_file]
        code, out, err = _run(conv_cmd)
        if code != 0:
            raise RuntimeError(f"ffmpeg conversion failed:\n{err}")
        if os.path.exists(temp_output):
            os.remove(temp_output)
        return target_duration

    # If temp is longer than target trim it and encode to final codec
    if new_dur > target_duration:
        cmd_trim = [
            "ffmpeg", "-y", "-i", temp_output,
            "-t", f"{target_duration:.6f}"
        ] + output_args + [output_file]
        code, out, err = _run(cmd_trim)
        if code != 0:
            raise RuntimeError(f"ffmpeg trim failed:\n{err}")
    else:
        # temp shorter -> pad with silence then cut to exact duration then encode
        pad_amount = target_duration - new_dur
        cmd_pad = [
            "ffmpeg", "-y", "-i", temp_output,
            "-af", f"apad=pad_dur={pad_amount:.6f}",
            "-t", f"{target_duration:.6f}"
        ] + output_args + [output_file]
        code, out, err = _run(cmd_pad)
        if code != 0:
            raise RuntimeError(f"ffmpeg pad failed:\n{err}")

    # cleanup
    if os.path.exists(temp_output):
        os.remove(temp_output)

    final_dur = _ffprobe_duration(output_file)
    print("Final saved duration:", final_dur)
    return final_dur

# ---------------------------
# TTS flow: generate voice and call adjuster
# ---------------------------

def generate_voice_from_segments(segments, out_file="output.wav", adjust_timing=True):
    """
    Generate voice using Google TTS and optionally adjust timing with ffmpeg policy adjuster.
    segments: list of dicts with "script" and "end_time" keys at minimum.
    """
    # Build transcript
    transcript = "Read the following script with an energetic, motivating tone: "
    transcript += build_transcript(segments)

    print("Calling Google TTS API...")
    client = genai.Client()  # ensure GEMINI API key set in env as before

    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=transcript,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name='Kore'
                    )
                )
            )
        )
    )

    # Extract PCM bytes from API response
    pcm_data = response.candidates[0].content.parts[0].inline_data.data

    # Prepare file paths
    out_dir = os.path.dirname(out_file) or "."
    os.makedirs(out_dir, exist_ok=True)
    out_basename = os.path.basename(out_file)
    temp_file = os.path.join(out_dir, "temp_" + out_basename)

    # Save raw PCM to temp wav
    save_wav(temp_file, pcm_data)
    print(f"Initial audio saved to {temp_file}")

    # Adjust timing if requested
    if adjust_timing and segments:
        target_duration = segments[-1]["end_time"]
        print(f"Target duration from segments: {target_duration}s")
        final_dur = adjust_audio_policy(temp_file, out_file, target_duration)
        # cleanup temp
        if os.path.exists(temp_file):
            os.remove(temp_file)
        print(f"✓ Final audio saved to {out_file} duration {final_dur:.3f}s")
        return out_file, final_dur
    else:
        # move temp file to final path (no timing adjustment)
        shutil.move(temp_file, out_file)
        final_dur = _ffprobe_duration(out_file)
        print(f"Moved {temp_file} to {out_file} duration {final_dur:.3f}s")
        return out_file, final_dur

