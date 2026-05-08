---
name: voxtral-tts-api
description: >
  Text-to-speech via Mistral Voxtral TTS API. Generate natural, emotionally
  expressive speech in 9 languages. Supports voice cloning from 3s audio samples,
  preset voices, streaming, and cross-lingual synthesis. Use when you need to
  generate speech, narrate content, create voice messages, or build voice agents.
metadata:
  category: productivity
  author: ManniTheRaccoon
  version: "1.0"
  api_docs: https://docs.mistral.ai/capabilities/audio/text_to_speech
compatibility: Requires curl, jq. API key via MISTRAL_API_KEY env var.
---

# Voxtral TTS 🎙️

Text-to-speech via Mistral's Voxtral TTS API. 4B parameter model, 70ms latency, $0.016/1k chars.

## Setup

```bash
export MISTRAL_API_KEY="your-key"
# or
cat ~/.openclaw/secrets/mistral.key
```

## Quick Start

```bash
# Generate speech with a preset voice
curl -s "https://api.mistral.ai/v1/audio/speech" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Hello, this is a test.",
    "voice_id": "<voice-id>",
    "response_format": "mp3"
  }' | jq -r '.audio_data' | base64 -d > output.mp3

# Clone a voice from a 3-5 second sample
REF_AUDIO=$(base64 -w0 reference.wav)
curl -s "https://api.mistral.ai/v1/audio/speech" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"input\": \"Speaking with a cloned voice.\",
    \"ref_audio\": \"$REF_AUDIO\",
    \"response_format\": \"mp3\"
  }" | jq -r '.audio_data' | base64 -d > cloned.mp3
```

## API Reference

### Generate Speech

`POST https://api.mistral.ai/v1/audio/speech`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `input` | string | ✅ | Text to speak |
| `voice_id` | string | | Preset or saved voice ID |
| `ref_audio` | string | | Base64-encoded audio for zero-shot voice cloning (3-25s) |
| `response_format` | string | | `mp3` (default), `wav`, `pcm`, `flac`, `opus` |
| `model` | string | | Model override (default: voxtral-tts) |
| `stream` | bool | | Enable SSE streaming (default: false) |

**Auth:** `Authorization: Bearer $MISTRAL_API_KEY`

**Response (non-streaming):**
```json
{"audio_data": "<base64-encoded-audio>"}
```

**Response (streaming):** SSE events:
```
event: speech.audio.delta
data: {"audio_data": "<base64-chunk>", "type": "speech.audio.delta"}

event: speech.audio.done
data: {"type": "speech.audio.done", "usage": {"prompt_tokens": 42, ...}}
```

**Note:** Either `voice_id` or `ref_audio` should be provided. If neither is given, a default voice is used.

### Voice Management

**List voices:**
```bash
curl -s "https://api.mistral.ai/v1/audio/voices?limit=50" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" | jq '.items[] | {id, name, gender, languages}'
```

**Create a saved voice** (from audio sample):
```bash
SAMPLE=$(base64 -w0 my-voice.wav)
curl -s -X POST "https://api.mistral.ai/v1/audio/voices" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"My Custom Voice\",
    \"sample_audio\": \"$SAMPLE\",
    \"sample_filename\": \"my-voice.wav\",
    \"gender\": \"male\",
    \"languages\": [\"en\", \"de\"]
  }" | jq '{id, name}'
```

**Update voice metadata:**
```bash
curl -s -X PATCH "https://api.mistral.ai/v1/audio/voices/<voice-id>" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name", "tags": ["narrator", "warm"]}'
```

**Delete voice:**
```bash
curl -s -X DELETE "https://api.mistral.ai/v1/audio/voices/<voice-id>" \
  -H "Authorization: Bearer $MISTRAL_API_KEY"
```

## Languages

9 languages supported natively:

| Language | Code | Dialects |
|---|---|---|
| English | en | American, British |
| French | fr | French |
| German | de | German |
| Spanish | es | Spanish |
| Dutch | nl | Dutch |
| Portuguese | pt | Portuguese |
| Italian | it | Italian |
| Hindi | hi | Hindi |
| Arabic | ar | Arabic |

## Features

### Voice Cloning
Pass `ref_audio` (base64, 3-25 seconds) for zero-shot voice cloning. Captures accent, rhythm, intonation, pauses, and emotional patterns. No pre-registration needed.

### Cross-Lingual Synthesis
The model handles cross-lingual voice adaptation: a French voice prompt with German text produces natural German speech with a French accent. Useful for translation pipelines.

### Streaming
Set `stream: true` for SSE streaming. Useful for real-time voice agents. Events: `speech.audio.delta` (audio chunks) and `speech.audio.done` (completion + usage).

### Long Text
The model natively generates up to 2 minutes of audio. The API handles longer text automatically with smart interleaving.

## Pricing

$0.016 per 1,000 characters. A typical 500-character message costs ~$0.008.

## Use Cases

| Use Case | How |
|---|---|
| Voice messages in chat | Generate mp3, send via message tool |
| Narrate content | Feed article/summary text, save as audio |
| Voice agent | Stream with `stream: true`, pipe to audio output |
| Storytelling | Use `ref_audio` for character voices |
| Accessibility | Convert any text response to speech |
| Multilingual support | Pass text in any supported language |

## Shell Helper

```bash
# One-liner: text to mp3 file
voxtral() {
  curl -s "https://api.mistral.ai/v1/audio/speech" \
    -H "Authorization: Bearer $MISTRAL_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"input\": \"$1\", \"voice_id\": \"${2:-}\", \"response_format\": \"mp3\"}" \
    | jq -r '.audio_data' | base64 -d > "${3:-output.mp3}"
  echo "Saved: ${3:-output.mp3}"
}

# Usage:
# voxtral "Hallo Welt!" "voice-id" "hallo.mp3"
# voxtral "Quick test"  # uses default voice, saves to output.mp3
```

## Comparison

| Feature | Voxtral TTS | ElevenLabs | OpenAI TTS |
|---|---|---|---|
| Price/1k chars | $0.016 | $0.18 (v2) | $0.015 |
| Latency (TTFA) | 70ms | ~100ms | ~200ms |
| Voice Cloning | ✅ (3s) | ✅ (30s) | ❌ |
| Languages | 9 | 29 | 57 |
| Streaming | ✅ | ✅ | ✅ |
| Open Weights | ✅ (CC BY NC) | ❌ | ❌ |
| Self-Hostable | ✅ (~3GB RAM) | ❌ | ❌ |

---
*v1.0 -- Voxtral TTS API skill. ManniTheRaccoon 2026-03-30.* 🎙️
