import pyaudio
import numpy as np
import time
import subprocess
import sys

# --- CONFIGURATION ---
THRESHOLD = 5000        # Sensitivity: Increase this if it's too sensitive
CLAP_WINDOW = 0.7       # Max time (seconds) between claps
CHUNK = 1024            # Size of audio buffer
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
TRIGGER_COOLDOWN = 4.0  # Seconds to ignore new clap sequences after a trigger
STARTUP_ARM_DELAY = 2.0  # Wait time before enabling detection after startup
CALIBRATION_SECONDS = 1.5
THRESHOLD_MULTIPLIER = 3.0
REARM_FACTOR = 0.6
MAX_DYNAMIC_THRESHOLD = 20000
SILENT_CHUNKS_TO_ARM = 8


def open_audio_stream(p):
    """Open the first working microphone input stream."""
    candidates = []

    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info.get("maxInputChannels", 0) > 0:
            candidates.append(info)

    # Prefer real hardware inputs before virtual/default aliases.
    def device_priority(info):
        name = str(info.get("name", "")).lower()
        if any(alias in name for alias in ["default", "sysdefault", "pipewire", "pulse"]):
            return 1
        return 0

    candidates.sort(key=device_priority)

    seen = set()
    for info in candidates:
        idx = int(info["index"])
        if idx in seen:
            continue
        seen.add(idx)

        name = info.get("name", f"device-{idx}")
        channels = max(1, min(CHANNELS, int(info.get("maxInputChannels", 1))))
        rate = int(info.get("defaultSampleRate", RATE))

        try:
            print(f"Trying input device: {name} (index={idx}, channels={channels}, rate={rate})")
            return p.open(
                format=FORMAT,
                channels=channels,
                rate=rate,
                input=True,
                input_device_index=idx,
                frames_per_buffer=CHUNK,
            )
        except Exception as exc:
            print(f"Failed to open {name}: {exc}")

    print("No working microphone input device could be opened.", file=sys.stderr)
    print("Available input devices:", file=sys.stderr)
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info.get("maxInputChannels", 0) > 0:
            print(
                f"  {i}: {info.get('name')} (inputs={info.get('maxInputChannels')}, rate={info.get('defaultSampleRate')})",
                file=sys.stderr,
            )
    raise RuntimeError("Unable to open any microphone input device")

def trigger_system():
    """Put your 'Iron Man' commands here!"""
    print(">>> ACCESS GRANTED. Initializing system...")
    # Open Antigravity app, and open websites as tabs in a single Firefox window.
    subprocess.Popen(["antigravity"])
    subprocess.Popen(["firefox", "https://github.com", "https://www.notion.so"])
    subprocess.Popen(["konsole"])


def calibrate_threshold(stream):
    """Measure ambient noise and compute a robust detection threshold."""
    print(f"Calibrating mic noise floor for {CALIBRATION_SECONDS:.1f}s... stay quiet.")
    rms_samples = []
    end_time = time.time() + CALIBRATION_SECONDS

    while time.time() < end_time:
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        rms = np.sqrt(np.mean(audio_data.astype(float) ** 2))
        rms_samples.append(rms)

    ambient_rms = float(np.percentile(rms_samples, 90)) if rms_samples else 0.0

    dynamic_threshold = max(
        float(THRESHOLD),
        min(ambient_rms * THRESHOLD_MULTIPLIER, float(MAX_DYNAMIC_THRESHOLD)),
    )

    print(f"Using threshold: {dynamic_threshold:.0f} (ambient: {ambient_rms:.0f}, base: {THRESHOLD})")
    return dynamic_threshold

def main():
    p = pyaudio.PyAudio()
    stream = open_audio_stream(p)
    active_threshold = calibrate_threshold(stream)

    last_clap_time = 0
    waiting_for_second = False
    clap_armed = True
    arm_time = time.time() + STARTUP_ARM_DELAY
    silent_chunks = 0
    ready_for_listen = False

    print("Systems Online. Listening for double-clap...")

    try:
        while True:
            # Read audio data from the microphone
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            
            # Calculate the volume (Root Mean Square)
            # $RMS = \sqrt{\frac{1}{n} \sum_{i=1}^{n} x_i^2}$
            rms = np.sqrt(np.mean(audio_data.astype(float)**2))

            current_time = time.time()

            # Grace period right after startup and after successful triggers.
            if current_time < arm_time:
                continue

            # Rearm only after audio level drops sufficiently.
            if not clap_armed and rms < (active_threshold * REARM_FACTOR):
                clap_armed = True

            # Only start detection after we observe a short silence period.
            if rms < (active_threshold * REARM_FACTOR):
                silent_chunks += 1
            else:
                silent_chunks = 0

            if silent_chunks >= SILENT_CHUNKS_TO_ARM:
                ready_for_listen = True

            if not ready_for_listen:
                continue

            if clap_armed and rms > active_threshold:
                clap_armed = False
                
                if not waiting_for_second:
                    # This is the first clap
                    waiting_for_second = True
                    last_clap_time = current_time
                    print("First clap detected...")
                    # Small sleep to prevent the same clap from being counted twice
                    time.sleep(0.2) 
                else:
                    # Check if second clap is within the valid time window
                    time_diff = current_time - last_clap_time
                    if 0.1 < time_diff < CLAP_WINDOW:
                        trigger_system()
                        print("Trigger executed once. Exiting...")
                        return
                    else:
                        # Reset if the second clap took too long
                        last_clap_time = current_time
            
            # Reset if the user clapped once but never did a second one
            if waiting_for_second and (time.time() - last_clap_time > CLAP_WINDOW):
                waiting_for_second = False

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()