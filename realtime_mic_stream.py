# realtime_mic_stream_final.py
import asyncio
import json
import struct
import time
import pyaudio
import requests
import numpy as np
import websockets

FASTAPI_URL = "http://localhost:8000/get_token"
token = requests.get(FASTAPI_URL).json().get("token")
if not token:
    raise RuntimeError("Failed to get token from backend")

WS_URL = f"wss://streaming.assemblyai.com/v3/ws?sample_rate=16000&token={token}"

# --- Audio config ---
INPUT_RATE = 48000        # what ALSA usually gives you
TARGET_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK_MS = 100
CHUNK = int(INPUT_RATE * CHUNK_MS / 1000)  # 4800 frames = 100 ms at 48 kHz

# --- Resampler: 48 kHz → 16 kHz int16 ---
def resample_int16(data_bytes, input_rate=48000, target_rate=16000):
    data = np.frombuffer(data_bytes, dtype=np.int16).astype(np.float32)
    if input_rate != target_rate:
        ratio = input_rate / target_rate
        new_len = int(len(data) / ratio)
        data = np.interp(
            np.linspace(0, len(data), new_len, endpoint=False),
            np.arange(len(data)),
            data,
        )
    return data.astype(np.int16).tobytes()

async def main():
    print("🔑 Token:", token[:30], "...")
    async with websockets.connect(WS_URL) as ws:
        print("✅ Connected to AssemblyAI Realtime v3")

        # --- Select a valid mic automatically ---
        pa = pyaudio.PyAudio()
        device_index = None
        for i in range(pa.get_device_count()):
            info = pa.get_device_info_by_index(i)
            if info.get("maxInputChannels", 0) > 0:
                device_index = i
                break
        if device_index is None:
            raise RuntimeError("❌ No input devices found")

        print(f"🎙 Using device #{device_index}: {pa.get_device_info_by_index(device_index)['name']}")

        stream = pa.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=INPUT_RATE,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=CHUNK,
        )
        print("🎧 Speak now...")

        async def sender():
            while True:
                data = stream.read(CHUNK, exception_on_overflow=False)
                resampled = resample_int16(data, INPUT_RATE, TARGET_RATE)
                await ws.send(resampled)
                await asyncio.sleep(CHUNK_MS / 1000.0)

        async def receiver():
            async for msg in ws:
                data = json.loads(msg)
                if data.get("type") == "Turn" and data.get("end_of_turn"):
                    text = data.get("transcript", "").strip()
                    if text:
                        print("📝", text)

        await asyncio.gather(sender(), receiver())

if __name__ == "__main__":
    asyncio.run(main())
