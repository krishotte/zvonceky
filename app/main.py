import asyncio
import os
import numpy as np
from fastapi import FastAPI, Query, BackgroundTasks
import pygame

app = FastAPI(title="Santa Bells Server")

# Initialize pygame mixer
pygame.mixer.init(frequency=44100, size=-16, channels=1)

# Path to the bell sound file
BELLS_FILE = os.path.join(os.path.dirname(__file__), "christmas-bells-05.mp3")

def generate_bell_sound():
    """Generates a simple bell-like sound if the file is missing."""
    duration = 1.0  # seconds
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Mix of frequencies for a bell-like tone
    frequencies = [880, 1760, 2640]
    signal = np.zeros_like(t)
    for f in frequencies:
        signal += np.sin(2 * np.pi * f * t) * np.exp(-3 * t)
        
    # Normalize to 16-bit range
    signal = (signal / np.max(np.abs(signal)) * 32767).astype(np.int16)
    
    # Ensure signal matches mixer channels
    mixer_info = pygame.mixer.get_init()
    if mixer_info:
        actual_channels = mixer_info[2]
        if actual_channels > 1:
            # Reshape to (samples, channels) for stereo/multi-channel
            signal = np.repeat(signal[:, np.newaxis], actual_channels, axis=1)
            
    return pygame.sndarray.make_sound(signal)

async def play_sound_task(wait: int):
    """Task to play sound after an optional delay."""
    if wait > 0:
        await asyncio.sleep(wait)
    
    try:
        if os.path.exists(BELLS_FILE):
            pygame.mixer.music.load(BELLS_FILE)
            pygame.mixer.music.play()
        else:
            sound = generate_bell_sound()
            sound.play()
    except Exception as e:
        print(f"Failed to play sound in background: {e}")

async def play_gong_task(wait: int):
    """Task to play generated gong sound after an optional delay."""
    if wait > 0:
        await asyncio.sleep(wait)
    
    try:
        sound = generate_bell_sound()
        sound.play()
    except Exception as e:
        print(f"Failed to play gong sound in background: {e}")

@app.get("/bells")
async def play_bells(background_tasks: BackgroundTasks, wait: int = Query(default=0, ge=0)):
    """
    Schedule Santa Claus bells to play on the server.
    Optional 'wait' parameter specifies seconds to wait before playing.
    Returns immediately after scheduling.
    """
    background_tasks.add_task(play_sound_task, wait)
    return {"status": "success", "message": f"Sound scheduled to play in {wait}s"}

@app.get("/gong")
async def play_gong(background_tasks: BackgroundTasks, wait: int = Query(default=0, ge=0)):
    """
    Schedule a generated gong sound to play on the server.
    Optional 'wait' parameter specifies seconds to wait before playing.
    Returns immediately after scheduling.
    """
    background_tasks.add_task(play_gong_task, wait)
    return {"status": "success", "message": f"Gong scheduled to play in {wait}s"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
