# AudioPod Python SDK

Official Python SDK for [AudioPod AI](https://audiopod.ai) - Professional Audio Processing powered by AI.

[![PyPI version](https://badge.fury.io/py/audiopod.svg)](https://pypi.org/project/audiopod/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install audiopod
```

## Quick Start

```python
from audiopod import AudioPod

# Initialize client
client = AudioPod(api_key="ap_your_api_key")

# Separate audio into 6 stems
result = client.stems.separate(
    url="https://youtube.com/watch?v=VIDEO_ID",
    mode="six"
)

# Download stems
for stem, url in result["download_urls"].items():
    print(f"{stem}: {url}")
```

## Stem Separation

Extract individual audio components from mixed recordings.

### Available Modes

| Mode | Stems | Output |
|------|-------|--------|
| `single` | 1 | Specified stem only (vocals, drums, bass, guitar, piano, other) |
| `two` | 2 | Vocals + Instrumental |
| `four` | 4 | Vocals, Drums, Bass, Other |
| `six` | 6 | Vocals, Drums, Bass, Guitar, Piano, Other |
| `producer` | 8 | + Kick, Snare, Hihat |
| `studio` | 12 | Full production toolkit |
| `mastering` | 16 | Maximum detail |

### Examples

```python
from audiopod import AudioPod

client = AudioPod(api_key="ap_your_api_key")

# Six-stem separation from YouTube
job = client.stems.extract(
    url="https://youtube.com/watch?v=VIDEO_ID",
    mode="six"
)
print(f"Job ID: {job['id']}")

# Wait for completion
result = client.stems.wait_for_completion(job["id"])
print(result["download_urls"])

# Or use the convenience method (extract + wait)
result = client.stems.separate(
    url="https://youtube.com/watch?v=VIDEO_ID",
    mode="six"
)

# From local file
result = client.stems.separate(
    file="./song.mp3",
    mode="four"
)

# Extract only vocals
result = client.stems.separate(
    url="https://youtube.com/watch?v=VIDEO_ID",
    mode="single",
    stem="vocals"
)

# Get available modes
modes = client.stems.modes()
for m in modes["modes"]:
    print(f"{m['mode']}: {m['description']}")
```

## API Wallet

Check balance and manage your wallet.

```python
# Check balance
balance = client.wallet.balance()
print(f"Balance: {balance['balance_usd']}")

# Estimate cost
estimate = client.wallet.estimate("stem_extraction", duration_seconds=180)
print(f"Estimated cost: {estimate['cost_usd']}")

# Get usage history
usage = client.wallet.usage()
for log in usage["logs"]:
    print(f"{log['service_type']}: {log['amount_usd']}")
```

## Other Services

```python
# Transcription
job = client.transcription.create(url="https://...")
result = client.transcription.wait_for_completion(job["id"])

# Voice cloning
voice = client.voice.clone(file="./sample.wav", name="My Voice")

# Music generation
song = client.music.generate(prompt="upbeat electronic dance music")

# Noise reduction
clean = client.denoiser.denoise(file="./noisy.wav")

# Speaker diarization
speakers = client.speaker.diarize(url="https://...")
```

## Error Handling

```python
from audiopod import AudioPod, InsufficientBalanceError, AuthenticationError

try:
    client = AudioPod(api_key="ap_...")
    result = client.stems.separate(url="...", mode="six")
except AuthenticationError:
    print("Invalid API key")
except InsufficientBalanceError as e:
    print(f"Need more credits. Required: {e.required_cents} cents")
```

## Environment Variables

```bash
export AUDIOPOD_API_KEY="ap_your_api_key"
```

```python
# Client reads from env automatically
client = AudioPod()
```

## Documentation

- [API Documentation](https://docs.audiopod.ai)
- [API Reference](https://docs.audiopod.ai/api-reference/stem-splitter)
- [Get API Key](https://www.audiopod.ai/dashboard/account/api-keys)

## License

MIT License - see [LICENSE](LICENSE) for details.
