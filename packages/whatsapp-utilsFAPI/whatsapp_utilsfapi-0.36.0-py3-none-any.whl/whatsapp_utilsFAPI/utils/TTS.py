import logging
import os
from typing import Optional

import azure.cognitiveservices.speech as speechsdk

logger = logging.getLogger(__name__)


class TextToSpeechError(Exception):
    """Custom exception for text-to-speech errors."""
    pass


def text_to_arabic_speech(text: str, output_filename: str, sys_conf: dict) -> Optional[str]:
    """
    Convert Arabic text to MP3 audio using Azure TTS.
    
    Args:
        text: Arabic text to synthesize
        output_filename: Output file path
        sys_conf: System configuration dictionary
        
    Returns:
        Full path to generated MP3 file, or None if failed
        
    Raises:
        TextToSpeechError: If TTS conversion fails
    """
    logger.info("Starting TTS conversion")
    
    try:
        # Validate input
        if not text or not text.strip():
            logger.warning("Empty text provided for TTS")
            return None

        # Configuration
        speech_config = speechsdk.SpeechConfig(
            subscription=sys_conf["AZURE_SPEECH_KEY"],
            region=sys_conf["AZURE_SPEECH_REGION"]
        )

        # Choose Arabic voice and set output format
        speech_config.speech_synthesis_voice_name = "ar-SA-ZariyahNeural"
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz128KBitRateMonoMp3
        )
        
        audio_config = speechsdk.audio.AudioOutputConfig(
            filename=output_filename
        )

        # Create synthesizer
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config
        )

        # Synthesize
        result = synthesizer.speak_text_async(text).get()

        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logger.info("Audio saved successfully: %s", output_filename)
            return output_filename
        else:
            error_details = ""
            if result.cancellation_details:
                error_details = (
                    f"Reason: {result.cancellation_details.reason}, "
                    f"Details: {result.cancellation_details.error_details}"
                )
            error_msg = f"Speech synthesis failed: {result.reason}. {error_details}"
            logger.error(error_msg)
            raise TextToSpeechError(error_msg)

    except Exception as e:
        logger.error("TTS conversion failed: %s", str(e))
        raise TextToSpeechError(f"TTS conversion failed: {str(e)}") from e