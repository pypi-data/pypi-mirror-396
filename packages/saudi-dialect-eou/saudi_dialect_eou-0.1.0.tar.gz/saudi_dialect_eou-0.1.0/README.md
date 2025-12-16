# Arabic End-of-Utterance Plugin for LiveKit Agents

This plugin provides Arabic end-of-utterance (EOU) detection for LiveKit Agents, optimized for Saudi Arabic dialect.

## Installation

```bash
pip install saudi-dialect-eou
```

## Usage

```python
from livekit.agents import AgentSession
from saudi_dialect_eou import ArabicEOUModel
from livekit.plugins import deepgram, silero

session = AgentSession(
    turn_detection=ArabicEOUModel(),
    vad=silero.VAD.load(),
    stt=deepgram.STT(language="ar"),
    # ... other plugins
)
```

## Download Model Files

Before running your agent, download the model files:

```bash
python your_agent.py download-files
```

## Configuration

```python
ArabicEOUModel(
    model_path="hams-ai/arabic-turn-detector",  # HuggingFace model path
    unlikely_threshold=0.3,  # Threshold for incomplete detection
    device="cuda",  # or "cpu"
)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_path` | str | `"hams-ai/arabic-turn-detector"` | HuggingFace model path |
| `unlikely_threshold` | float | `0.3` | Probability below which user is still speaking |
| `device` | str | `None` | Device for inference (auto-detected if None) |

## How It Works

The model takes conversation context with `[SEP]` tokens and predicts:
- **1 (complete)**: User has finished speaking → Agent should respond
- **0 (incomplete)**: User is still speaking → Wait for more input

## License

Apache-2.0
