# ATLAS

Adaptive Tactical Learning Assistant System

ATLAS is a desktop AI assistant built with Python that combines interaction with voice, live vision, gesture control, memory, and HUD.

Right now ATLAS combines voice, visuals, object detection, maps, automation, and experiments into one system.

This project started in 2023 as a personal way to build something that felt less like typing away at an AI and more like interacting with it on a personal level.

Eventually I want to translate parts of this into smart glasses.

---

## Current Features

### Core AI
- Conversational AI assistant
- Memory support
- Voice input and TTS output
- Persistent context

### Voice

* Wake words
* Text to speech
* AI responses
* State system

### Visuals

* Animated orb
* Audio visualizer
* HUD panels
* Tactical map
* Object Detection
* Boot sequence

### Vision

* YOLO object detection
* Scan mode
* Screen analysis
* OCR

### Controls

* Gesture support
* Hand tracking
* Mode switching

### Productivity

* Workspace launcher
* Coding mode
* Spotify support
* Desktop actions

---

## Modes
MAP  
Navigate and interact with the environment.

HUD  
Main information interface.

VOICE  
Listens to user input.

SCAN  
Object detection and analysis.

FOCUS  
Minimal workspace mode.
---

## States
* IDLE
* LISTENING
* THINKING
* SPEAKING
* SCANNING
* STANDBY
* FOCUS

---

## Tech Used
Python  
PySide6  
YOLOv8  
OpenCV  
MediaPipe  
Edge TTS  
Pygame  
MapLibre  
Tesseract OCR  
Open-Meteo 

---

## Setup

Clone:

```bash
git clone YOUR_REPO_LINK
```

Install packages:

```bash
pip install -r requirements.txt
```

Run:

```bash
python qtmain.py
```

You may edit:

```plaintext
settings.json
memory.json
workspace.json
config.py
.env
```

to customize behavior.

Templates are included.

---

## Why I Made This

I always thought the idea of having something like JARVIS was cool.

So instead of waiting until I knew everything, I started building.

This repo is basically me learning and building at the same time.

---

## Future Ideas

* Smart glasses
* Better UI
* Better memory
* More automation
* Better coding mode
* Local models
* ATLAS.exe setup

---

## Demo

Coming later.

## Screenshots

Coming later.

---

Current version committed: Summer 2026.
