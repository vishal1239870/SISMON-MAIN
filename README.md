# 🎬 CineMorph: AI Powered Video Generation Agent

> Transform a single text prompt into a complete video with AI-generated visuals, narration, and voice-over

---

## ✅ Overview

The CineMorph pipeline is designed to transform a single user prompt into a complete AI-generated video. It works in several stages:

1. **Prompt Expansion:**
The user’s prompt is expanded into multiple detailed visual segments using Gemini text models. The same model also generates a matching narration script.

2. **Visual Generation:**
Each segment is used to generate images or short video clips using Gemini/Runway video and image generation models.

3. **Timeline Assembly:**
All generated visuals are arranged into a structured timeline so each segment plays in the correct sequence and duration.

4. **Narration & Audio Processing:**
The narration text is added as on-screen subtitles.
Narration audio is synthesized using Gemini TTS, while FFmpeg and SoundFile are used to clean, normalize, and sync the audio with the visuals.

5. **Final Rendering:**
Finally, the processed audio and video are merged using FFmpeg and exported as a high-quality MP4 file.


**No manual editing required** — just provide a prompt and get a finished video!

---

## ✨ Features

- **One-Prompt Workflow**: Single input generates complete video output
- **Intelligent Content Breakdown**: Automatically segments your idea into visual scenes
- **Dual Media Support**: Generates both static images and video clips
- **Natural Voice-Over**: AI-generated narration with proper timing
- **Professional Effects**: Pan, zoom, and motion effects on static images
- **Format Flexibility**: Supports both portrait and landscape orientations
- **Subtitle Integration**: Automatic text overlay synchronized with narration

---

## 🏗️ Architecture
```
User Prompt
    ↓
┌─────────────────────────────────────────────┐
│  1. Prompt Expansion (Gemini)               │
│     → Breaks down into visual segments      │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│  2. Script Generation (Gemini)              │
│     → Creates narration for each segment    │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│  3. Media Generation (Runway/Gemini)        │
│     → Generates images or video clips       │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│  4. Video Assembly (MoviePy + FFmpeg)       │
│     → Stitches clips with effects           │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│  5. Audio Generation (Gemini TTS)           │
│     → Converts narration to speech          │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│  6. Audio Merge (FFmpeg)                    |
│     → Combines video + audio + subtitles    │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│  7. Final Merge (FFmpeg)                    │
│     → Combined video + background music     │
└─────────────────────────────────────────────┘
Final Video (MP4) → public/outputs/
```

---

## 🛠️ Technologies

| Component | Technology |
|-----------|-----------|
| **Text Processing** | Google Gemini (Prompt expansion & scripting) |
| **Visual Generation** | Runway / Gemini |
| **Voice Synthesis** | Gemini Text-to-Speech |
| **Video Composition** | MoviePy + FFmpeg |
| **Audio Processing** | FFmpeg + SoundFile |
| **Package Management** | UV (Python package manager) |

---

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **FFmpeg**: Required for video/audio processing
- **API Keys**: 
  - Google Gemini API key
  - Kie.AI API key (for Runway integration)

---

## 🚀 Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/Himanshuu2125/sismon.git
cd sismon
```

### Step 2: Install FFmpeg

<details>
<summary><b>Windows</b></summary>

1. **Download FFmpeg**
   - Visit [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)
   - Download `ffmpeg-release-essentials.zip` under "Release builds"

2. **Extract and Setup**
```bash
   # Extract the ZIP file
   # Rename folder to 'ffmpeg' and move to C:\ffmpeg
```

3. **Add to System PATH**
   - Press `Win + R` → type `sysdm.cpl` → Enter
   - Go to **Advanced** → **Environment Variables**
   - Under **System variables**, select **Path** → **Edit**
   - Click **New** → Add `C:\ffmpeg\bin`
   - Click **OK** on all dialogs

4. **Verify Installation**
```bash
   ffmpeg -version
```

</details>

<details>
<summary><b>macOS</b></summary>
```bash
# Using Homebrew
brew install ffmpeg

# Verify installation
ffmpeg -version
```

</details>

<details>
<summary><b>Linux (Ubuntu/Debian)</b></summary>
```bash
# Update package list
sudo apt update

# Install FFmpeg
sudo apt install ffmpeg

# Verify installation
ffmpeg -version
```

</details>

### Step 3: Install UV Package Manager
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 4: Set Up Environment Variables

Create a `.env` file in the project root:
```bash
# .env file
GEMINI_API_KEY=your_gemini_api_key_here
KIE_API_KEY=your_kie_api_key_here
```

**Or set them in your system:**
```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY="your_key_here"
$env:KIE_API_KEY="your_key_here"

# macOS/Linux
export GEMINI_API_KEY="your_key_here"
export KIE_API_KEY="your_key_here"
```

### Step 5: Install Python Dependencies
```bash
# Sync all dependencies using UV
uv sync
```

---

## 🎯 Usage

**CineMorph offers two ways to generate videos:**

---

### 🖥️ Option 1: Terminal/Command Line Interface

#### Basic Usage
```bash
uv run test.py
```

#### Custom Prompt

Edit `test.py` to pass your custom prompt:
```python
prompt = "Create a 30-second video about the journey of a coffee bean from farm to cup"
seg = generate_prompts_from_prompt(prompt)  # line 15
script = generate_script_from_prompt(seg, prompt)  # line 16
```

---

### 🌐 Option 2: Web Interface (Streamlit)

#### Launch the Streamlit UI
```bash
streamlit run main.py
```

This will open a web browser with an interactive interface where you can:
- ✍️ Enter your prompt in a text box
- 📊 Monitor the generation progress in real-time
- 🎥 Preview and download your generated video

**Access the interface at:** `http://localhost:8501`

---

## 📂 Output Location

Generated videos will be saved in:
```
public/outputs/final_video.mp4
```

Intermediate files:
```
public/images/    # Generated images
public/videos/    # Generated video clips
public/audio/     # Generated audio files
```

---

## 🔧 Configuration

Customize video settings by editing the pipeline parameters:
```python
# Example configurations
FONT_SIZE = 50
COLOR = "black"            # or "blue", "red", etc
ORIENTATION = "landscape"  # or "portrait"
EFFECT_TYPE = "zoom"       # "pan", "zoom", or "none"
```