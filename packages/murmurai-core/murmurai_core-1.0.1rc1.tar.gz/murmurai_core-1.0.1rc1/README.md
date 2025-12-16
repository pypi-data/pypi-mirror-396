<h1 align="center">MurmurAI</h1>

<p align="center">
  <strong>Modern speech recognition with word-level timestamps and speaker diarization</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/murmurai-core/">
    <img src="https://img.shields.io/pypi/v/murmurai-core?style=flat-square&color=00D9FF" alt="PyPI">
  </a>
  <a href="https://github.com/namastexlabs/murmurai/actions/workflows/ci.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/namastexlabs/murmurai/ci.yml?style=flat-square" alt="CI">
  </a>
  <img src="https://img.shields.io/badge/python-3.10--3.13-blue?style=flat-square" alt="Python">
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-BSD--2--Clause-green?style=flat-square" alt="License">
  </a>
</p>

---

MurmurAI is a fork of [WhisperX](https://github.com/m-bain/whisperX) with modern dependency support:

- **PyTorch 2.6+** compatibility (weights_only patches)
- **Pyannote 4.x** support (token parameter migration)
- **Torchaudio 2.9+** compatibility (audio backend fixes)
- **Python 3.10-3.13** tested

## Features

- **Word-level timestamps** via phoneme alignment
- **Speaker diarization** with pyannote.audio
- **Batch inference** for 70x realtime transcription
- **VAD preprocessing** (pyannote or silero)
- **Multiple output formats**: SRT, VTT, TXT, TSV, JSON

## Installation

```bash
pip install murmurai-core
```

Or with uv:

```bash
uv add murmurai-core
```

## Quick Start

### Python API

```python
import murmurai

# Load model
model = murmurai.load_model("large-v3-turbo", device="cuda", compute_type="float16")

# Transcribe
audio = murmurai.load_audio("audio.mp3")
result = model.transcribe(audio, batch_size=16)

# Align (word-level timestamps)
model_a, metadata = murmurai.load_align_model(language_code=result["language"], device="cuda")
result = murmurai.align(result["segments"], model_a, metadata, audio, device="cuda")

# Diarization (speaker labels)
from pyannote.audio import Pipeline
diarize_model = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token="YOUR_HF_TOKEN")
diarize_segments = diarize_model(audio)
result = murmurai.assign_word_speakers(diarize_segments, result)
```

### CLI

```bash
murmurai-core audio.mp3 --model large-v3-turbo --diarize --hf_token YOUR_TOKEN
```

## Requirements

- **NVIDIA GPU** with CUDA support (or CPU mode)
- **HuggingFace token** for diarization models

Accept the license at [pyannote/speaker-diarization-3.1](https://hf.co/pyannote/speaker-diarization-3.1) before using diarization.

## Migration from WhisperX

```python
# Before
import whisperx

# After
import murmurai  # drop-in replacement
```

All APIs are identical. Just change the import.

## Credits

MurmurAI builds on the excellent work of:

- [WhisperX](https://github.com/m-bain/whisperX) by Max Bain
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Faster Whisper](https://github.com/guillaumekln/faster-whisper)
- [Pyannote](https://github.com/pyannote/pyannote-audio)

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/namastexlabs">Namastex Labs</a>
</p>
