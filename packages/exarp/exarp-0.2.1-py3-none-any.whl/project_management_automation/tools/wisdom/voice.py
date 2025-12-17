"""
Voice synthesis module for Trusted Advisor System.

Supports multiple TTS backends:
- ElevenLabs (high quality, API key required, $5/mo)
- edge-tts (Microsoft voices, free, offline-capable)
- pyttsx3 (system voices, free, fully offline)

Usage:
    from project_management_automation.tools.wisdom.voice import (
        synthesize_advisor_quote,
        generate_podcast_audio,
        list_available_voices,
    )

    # Generate audio from advisor consultation
    audio_path = synthesize_advisor_quote(
        text="Your quote here",
        advisor="bofh",
        output_path="advisor_quote.mp3"
    )
"""

import asyncio
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, Optional

# Backend type
TTSBackend = Literal["elevenlabs", "edge-tts", "pyttsx3", "auto"]

# Voice mappings for different advisors
ADVISOR_VOICES = {
    "elevenlabs": {
        # ElevenLabs voice IDs - map advisors to appropriate voices
        "bofh": {"voice_id": "ErXwobaYiN019PkySvjV", "name": "Antoni"},  # Confident male
        "stoic": {"voice_id": "VR6AewLTigWG4xSOukaG", "name": "Arnold"},  # Deep, authoritative
        "zen": {"voice_id": "pNInz6obpgDQGcFmaJgB", "name": "Adam"},  # Calm, measured
        "trickster": {"voice_id": "TxGEqnHWrfWFTfGW9XjX", "name": "Josh"},  # Energetic
        "perfectionist": {"voice_id": "yoZ06aMxZJJ28mfd3POQ", "name": "Sam"},  # Precise
        "mystic": {"voice_id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella"},  # Ethereal female
        "sage": {"voice_id": "onwK4e9ZLuTAKqWW03F9", "name": "Daniel"},  # Wise elder
        "warrior": {"voice_id": "N2lVS1w4EtoT3dr4eOWO", "name": "Callum"},  # Strong, direct
        # Hebrew advisors - use multilingual voices
        "rebbe": {"voice_id": "onwK4e9ZLuTAKqWW03F9", "name": "Daniel"},  # Wise, rabbinical
        "tzaddik": {"voice_id": "pNInz6obpgDQGcFmaJgB", "name": "Adam"},  # Righteous one
        "chacham": {"voice_id": "VR6AewLTigWG4xSOukaG", "name": "Arnold"},  # Sage, deep wisdom
        "default": {"voice_id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel"},  # Default
    },
    "edge-tts": {
        # Microsoft Edge TTS voices
        "bofh": "en-US-GuyNeural",
        "stoic": "en-GB-RyanNeural",
        "zen": "en-US-ChristopherNeural",
        "trickster": "en-AU-WilliamNeural",
        "perfectionist": "en-US-EricNeural",
        "mystic": "en-US-AriaNeural",
        "sage": "en-GB-ThomasNeural",
        "warrior": "en-US-DavisNeural",
        # Hebrew advisors - Hebrew (Israel) voices
        "rebbe": "he-IL-AvriNeural",  # Hebrew male - wise rabbi
        "tzaddik": "he-IL-AvriNeural",  # Hebrew male - righteous
        "chacham": "he-IL-AvriNeural",  # Hebrew male - sage
        "hebrew": "he-IL-AvriNeural",  # Generic Hebrew male
        "hebrew_f": "he-IL-HilaNeural",  # Hebrew female
        "default": "en-US-JennyNeural",
    },
    "pyttsx3": {
        # System voices - just rate adjustments per advisor style
        "bofh": {"rate": 180},  # Fast, impatient
        "stoic": {"rate": 140},  # Slow, deliberate
        "zen": {"rate": 120},  # Very calm
        "trickster": {"rate": 200},  # Energetic
        "perfectionist": {"rate": 160},  # Measured
        "mystic": {"rate": 130},  # Ethereal
        "sage": {"rate": 135},  # Wise
        "warrior": {"rate": 170},  # Direct
        # Hebrew advisors - slower, reverent pace
        "rebbe": {"rate": 125},  # Thoughtful, teaching
        "tzaddik": {"rate": 120},  # Calm, righteous
        "chacham": {"rate": 130},  # Measured wisdom
        "default": {"rate": 150},
    },
}

# Hebrew-specific voice settings
HEBREW_VOICES = {
    "edge-tts": {
        "male": "he-IL-AvriNeural",
        "female": "he-IL-HilaNeural",
    },
    "note": "Hebrew TTS support via Microsoft Edge voices. For best results, use edge-tts backend.",
}


def get_available_backend() -> Optional[TTSBackend]:
    """Detect which TTS backend is available."""
    # Check ElevenLabs
    if os.getenv("ELEVENLABS_API_KEY"):
        try:
            import elevenlabs

            return "elevenlabs"
        except ImportError:
            pass

    # Check edge-tts
    try:
        result = subprocess.run(["edge-tts", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return "edge-tts"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Check pyttsx3
    try:
        import pyttsx3

        return "pyttsx3"
    except ImportError:
        pass

    return None


def list_available_voices(backend: TTSBackend = "auto") -> dict[str, Any]:
    """List available voices for the specified backend."""
    if backend == "auto":
        backend = get_available_backend()
        if not backend:
            return {"error": "No TTS backend available", "backends_checked": ["elevenlabs", "edge-tts", "pyttsx3"]}

    result = {
        "backend": backend,
        "advisor_voices": {},
    }

    if backend == "elevenlabs":
        result["advisor_voices"] = ADVISOR_VOICES["elevenlabs"]
        result["note"] = "Set ELEVENLABS_API_KEY env var. pip install elevenlabs"

    elif backend == "edge-tts":
        result["advisor_voices"] = ADVISOR_VOICES["edge-tts"]
        result["note"] = "pip install edge-tts. Free Microsoft voices."

    elif backend == "pyttsx3":
        result["advisor_voices"] = ADVISOR_VOICES["pyttsx3"]
        result["note"] = "pip install pyttsx3. Uses system voices."

    return result


def _synthesize_elevenlabs(
    text: str,
    voice_id: str,
    output_path: Path,
    model_id: str = "eleven_multilingual_v2",
) -> Path:
    """Synthesize using ElevenLabs API."""
    from elevenlabs.client import ElevenLabs

    client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

    audio = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id=model_id,
        output_format="mp3_44100_128",
    )

    # Write audio to file
    with open(output_path, "wb") as f:
        for chunk in audio:
            f.write(chunk)

    return output_path


async def _synthesize_edge_tts_async(
    text: str,
    voice: str,
    output_path: Path,
) -> Path:
    """Synthesize using edge-tts (async)."""
    import edge_tts

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))
    return output_path


def _synthesize_edge_tts(
    text: str,
    voice: str,
    output_path: Path,
) -> Path:
    """Synthesize using edge-tts (sync wrapper)."""
    # Try async first
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Already in async context, use subprocess fallback
            result = subprocess.run(
                ["edge-tts", "--voice", voice, "--text", text, "--write-media", str(output_path)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                raise RuntimeError(f"edge-tts failed: {result.stderr}")
            return output_path
        else:
            return loop.run_until_complete(_synthesize_edge_tts_async(text, voice, output_path))
    except RuntimeError:
        # No event loop, create one
        return asyncio.run(_synthesize_edge_tts_async(text, voice, output_path))


def _synthesize_pyttsx3(
    text: str,
    rate: int,
    output_path: Path,
) -> Path:
    """Synthesize using pyttsx3 (system voices)."""
    import pyttsx3

    engine = pyttsx3.init()
    engine.setProperty("rate", rate)

    # pyttsx3 saves as wav, we may need to convert
    wav_path = output_path.with_suffix(".wav")
    engine.save_to_file(text, str(wav_path))
    engine.runAndWait()

    # If mp3 requested, try to convert
    if output_path.suffix.lower() == ".mp3":
        try:
            subprocess.run(["ffmpeg", "-i", str(wav_path), "-y", str(output_path)], capture_output=True, timeout=30)
            wav_path.unlink()  # Remove wav after conversion
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # ffmpeg not available, return wav
            return wav_path

    return output_path


def synthesize_advisor_quote(
    text: str,
    advisor: str = "default",
    output_path: Optional[str] = None,
    backend: TTSBackend = "auto",
) -> dict[str, Any]:
    """
    Synthesize an advisor quote to audio.

    Args:
        text: The quote text to synthesize
        advisor: Advisor ID (bofh, stoic, zen, etc.)
        output_path: Output file path (default: auto-generated)
        backend: TTS backend to use (auto, elevenlabs, edge-tts, pyttsx3)

    Returns:
        Dict with audio_path, backend_used, duration_estimate, etc.
    """
    # Auto-detect backend if needed
    if backend == "auto":
        backend = get_available_backend()
        if not backend:
            return {
                "success": False,
                "error": "No TTS backend available. Install one of: elevenlabs, edge-tts, pyttsx3",
            }

    # Generate output path if not provided
    if output_path is None:
        from ...utils import find_project_root

        project_root = find_project_root()
        audio_dir = project_root / ".exarp" / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = audio_dir / f"advisor_{advisor}_{timestamp}.mp3"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if backend == "elevenlabs":
            voice_info = ADVISOR_VOICES["elevenlabs"].get(advisor, ADVISOR_VOICES["elevenlabs"]["default"])
            _synthesize_elevenlabs(text, voice_info["voice_id"], output_path)

        elif backend == "edge-tts":
            voice = ADVISOR_VOICES["edge-tts"].get(advisor, ADVISOR_VOICES["edge-tts"]["default"])
            _synthesize_edge_tts(text, voice, output_path)

        elif backend == "pyttsx3":
            voice_settings = ADVISOR_VOICES["pyttsx3"].get(advisor, ADVISOR_VOICES["pyttsx3"]["default"])
            _synthesize_pyttsx3(text, voice_settings["rate"], output_path)

        # Estimate duration (rough: ~150 words per minute)
        word_count = len(text.split())
        duration_estimate = word_count / 150 * 60  # seconds

        return {
            "success": True,
            "audio_path": str(output_path),
            "backend": backend,
            "advisor": advisor,
            "text_length": len(text),
            "word_count": word_count,
            "duration_estimate_seconds": round(duration_estimate, 1),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "backend": backend,
            "advisor": advisor,
        }


def generate_podcast_audio(
    consultations: list[dict[str, Any]],
    output_path: Optional[str] = None,
    backend: TTSBackend = "auto",
    include_intro: bool = True,
    include_transitions: bool = True,
) -> dict[str, Any]:
    """
    Generate a podcast-style audio file from advisor consultations.

    Args:
        consultations: List of consultation dicts (from export_for_podcast)
        output_path: Output file path
        backend: TTS backend to use
        include_intro: Add intro narration
        include_transitions: Add transitions between segments

    Returns:
        Dict with audio_path, total_duration, segments_generated, etc.
    """
    if backend == "auto":
        backend = get_available_backend()
        if not backend:
            return {
                "success": False,
                "error": "No TTS backend available",
            }

    # Generate output path
    if output_path is None:
        from ...utils import find_project_root

        project_root = find_project_root()
        audio_dir = project_root / ".exarp" / "podcasts"
        audio_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = audio_dir / f"advisor_podcast_{timestamp}.mp3"
    else:
        output_path = Path(output_path)

    # Generate individual segments
    segments = []
    temp_dir = Path(output_path).parent / "temp_segments"
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Intro
        if include_intro:
            intro_text = "Welcome to the Exarp Advisor Podcast. Today's episode features wisdom from your trusted project advisors."
            intro_result = synthesize_advisor_quote(
                intro_text,
                advisor="sage",
                output_path=str(temp_dir / "00_intro.mp3"),
                backend=backend,
            )
            if intro_result.get("success"):
                segments.append(intro_result["audio_path"])

        # Process each consultation
        for i, consultation in enumerate(consultations):
            advisor = consultation.get("advisor", "default")
            quote = consultation.get("quote", "")
            consultation.get("context", "")
            metric = consultation.get("metric", "")

            # Build segment text
            segment_parts = []
            if include_transitions and metric:
                segment_parts.append(f"On {metric}:")
            segment_parts.append(quote)

            segment_text = " ".join(segment_parts)

            result = synthesize_advisor_quote(
                segment_text,
                advisor=advisor,
                output_path=str(temp_dir / f"{i + 1:02d}_{advisor}.mp3"),
                backend=backend,
            )

            if result.get("success"):
                segments.append(result["audio_path"])

        # Combine segments using ffmpeg if available
        if len(segments) > 1:
            try:
                # Create file list for ffmpeg
                list_file = temp_dir / "segments.txt"
                with open(list_file, "w") as f:
                    for seg in segments:
                        f.write(f"file '{seg}'\n")

                subprocess.run(
                    [
                        "ffmpeg",
                        "-f",
                        "concat",
                        "-safe",
                        "0",
                        "-i",
                        str(list_file),
                        "-c",
                        "copy",
                        "-y",
                        str(output_path),
                    ],
                    capture_output=True,
                    timeout=120,
                )

                # Cleanup temp files
                for seg in segments:
                    Path(seg).unlink(missing_ok=True)
                list_file.unlink(missing_ok=True)
                temp_dir.rmdir()

            except (FileNotFoundError, subprocess.TimeoutExpired):
                # ffmpeg not available, just return first segment
                import shutil

                shutil.copy(segments[0], output_path)

        elif len(segments) == 1:
            import shutil

            shutil.copy(segments[0], output_path)

        return {
            "success": True,
            "audio_path": str(output_path),
            "backend": backend,
            "segments_generated": len(segments),
            "consultations_processed": len(consultations),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "backend": backend,
        }


def check_tts_backends() -> dict[str, Any]:
    """Check which TTS backends are available and configured."""
    result = {
        "available_backends": [],
        "recommended": None,
        "details": {},
    }

    # Check ElevenLabs
    if os.getenv("ELEVENLABS_API_KEY"):
        try:
            import elevenlabs

            result["available_backends"].append("elevenlabs")
            result["details"]["elevenlabs"] = {
                "status": "configured",
                "quality": "excellent",
                "cost": "$5/month (free tier: 10k chars/month)",
            }
        except ImportError:
            result["details"]["elevenlabs"] = {
                "status": "api_key_set_but_not_installed",
                "install": "pip install elevenlabs",
            }
    else:
        result["details"]["elevenlabs"] = {
            "status": "not_configured",
            "setup": "Set ELEVENLABS_API_KEY env var, pip install elevenlabs",
        }

    # Check edge-tts
    try:
        subprocess.run(["edge-tts", "--version"], capture_output=True, timeout=5)
        result["available_backends"].append("edge-tts")
        result["details"]["edge-tts"] = {
            "status": "available",
            "quality": "good",
            "cost": "free",
        }
    except (FileNotFoundError, subprocess.TimeoutExpired):
        result["details"]["edge-tts"] = {
            "status": "not_installed",
            "install": "pip install edge-tts",
        }

    # Check pyttsx3
    try:
        import pyttsx3

        result["available_backends"].append("pyttsx3")
        result["details"]["pyttsx3"] = {
            "status": "available",
            "quality": "basic",
            "cost": "free (offline)",
        }
    except ImportError:
        result["details"]["pyttsx3"] = {
            "status": "not_installed",
            "install": "pip install pyttsx3",
        }

    # Set recommendation
    if "elevenlabs" in result["available_backends"]:
        result["recommended"] = "elevenlabs"
    elif "edge-tts" in result["available_backends"]:
        result["recommended"] = "edge-tts"
    elif "pyttsx3" in result["available_backends"]:
        result["recommended"] = "pyttsx3"

    return result
