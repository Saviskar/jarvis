# Jarvis Clapper 👏

Ever had a midnight idea that just wouldn’t let you sleep? 🌙

I was scrolling through Instagram recently and saw a few reels of people clapping to trigger their smart home setups. It immediately hit that nostalgia button taking me back to the first time I watched Iron Man and dreamed of having my own JARVIS.

Instead of tossing and turning, I decided to hop onto my Linux machine and build my own version.

Using Python and some real-time audio processing, I developed a script that listens for a specific **double-clap** pattern. Now, a quick clap sequence triggers my daily workflow, opening my terminal and browser automatically.

It’s not quite a Mark XLII armor suit yet, but it’s a fun step in that direction! 🛠️

If you want to bring a bit of Stark Industries to your own setup, I’ve open-sourced the code on GitHub.

---

## What this project does

- Listens continuously through your microphone.
- Detects a **double-clap** pattern.
- Triggers your workflow once (then exits):
  - Opens Antigravity desktop app
  - Opens GitHub and Notion in Firefox
  - Opens terminal
- You can change which apps and websites are opened by editing `trigger_system()` in [jarvis_ear.py](jarvis_ear.py).
- The current open commands are Linux-oriented. Update them based on your operating system (Fedora/Ubuntu/Windows/macOS).

---

## Requirements

- Python 3.10+
- Working microphone
- `numpy`
- `pyaudio`

> Note: `pyaudio` needs PortAudio system libraries. Install OS packages first (steps below).

---

## Project setup (common)

1. Clone/download the repository.
2. Open terminal in the project folder.
3. (Recommended) create and activate a virtual environment.
4. Install Python dependencies.
5. Run the script.

---

## Fedora Linux (KDE/GNOME)

### 1) Install system audio dependencies

```bash
sudo dnf install -y python3 python3-pip portaudio portaudio-devel
```

### 2) Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install Python packages

```bash
pip install --upgrade pip
pip install numpy pyaudio
```

### 4) Run

```bash
python3 jarvis_ear.py
```

### 5) Use

- Stay quiet during calibration.
- Do a clear double clap.
- Script executes once and exits.

### 6) Fedora-specific app commands

Current `trigger_system()` is tuned for Fedora/KDE:
- `antigravity`
- `firefox`
- `konsole`

If your terminal is different, update [jarvis_ear.py](jarvis_ear.py) in `trigger_system()`.

---

## Ubuntu Linux

### 1) Install system audio dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip portaudio19-dev
```

### 2) Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install Python packages

```bash
pip install --upgrade pip
pip install numpy pyaudio
```

### 4) Run

```bash
python3 jarvis_ear.py
```

### 5) Update launcher commands for Ubuntu

In `trigger_system()` you may want:
- Terminal: `gnome-terminal` (instead of `konsole`)
- Antigravity app command depending on install method

---

## Windows (PowerShell)

### 1) Install Python

- Install Python 3.10+ from python.org.
- During install, enable **Add Python to PATH**.

### 2) Create and activate virtual environment

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3) Install dependencies

```powershell
python -m pip install --upgrade pip
pip install numpy pyaudio
```

If `pyaudio` fails to build, install Microsoft C++ Build Tools or use a prebuilt wheel.

### 4) Update trigger commands for Windows

Edit `trigger_system()` in `jarvis_ear.py` with Windows commands, e.g.:
- Browser: `start firefox https://github.com https://www.notion.so`
- Terminal: `start wt` (Windows Terminal) or `start cmd`
- Antigravity app command as installed on your system

### 5) Run

```powershell
python jarvis_ear.py
```

---

## macOS (zsh)

### 1) Install system tools

- Install Python 3 with Homebrew (if needed):

```bash
brew install python portaudio
```

### 2) Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install --upgrade pip
pip install numpy pyaudio
```

### 4) Update trigger commands for macOS

Edit `trigger_system()` in `jarvis_ear.py` and use macOS launch style, e.g.:
- Browser tabs: `open -a Firefox https://github.com https://www.notion.so`
- Terminal: `open -a Terminal`
- Antigravity desktop app command/path based on your installation

### 5) Run

```bash
python3 jarvis_ear.py
```

---

## Tuning clap detection

In `jarvis_ear.py`, adjust:

- `THRESHOLD`: raise to reduce false triggers, lower if claps are missed.
- `CLAP_WINDOW`: max time between clap 1 and clap 2.
- `CALIBRATION_SECONDS`: calibration duration.

---

## Troubleshooting

### ALSA warnings on Linux

You may see ALSA warnings (PCM/channel map) on some systems. If the script still starts and listens, these can be benign.

### Script triggers too easily

- Increase `THRESHOLD`.
- Reduce background noise during calibration.
- Use a better microphone input device.

### Script does not trigger

- Lower `THRESHOLD` slightly.
- Clap closer to the mic.
- Verify microphone permissions and selected input device.

### `pyaudio` installation issues

Install PortAudio development packages first (see OS steps), then reinstall `pyaudio`.

---

## Run summary

After setup, every run is simply:

```bash
python3 jarvis_ear.py
```

(Windows: `python jarvis_ear.py`)
