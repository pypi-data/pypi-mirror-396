
import logging
from typing import Optional
import azure.cognitiveservices.speech as speechsdk

logger = logging.getLogger(__name__)


class SpeechToTextError(Exception):
    """Custom exception for speech-to-text errors."""
    pass


def transcribe_audio(file_path: str, sys_conf: dict) -> str:
    """
    Transcribe audio file to text using Azure Speech Services.
    
    Args:
        file_path: Path to audio file
        sys_conf: System configuration dictionary
        
    Returns:
        Transcribed text
        
    Raises:
        SpeechToTextError: If transcription fails
        FileNotFoundError: If audio file doesn't exist
    """
    try:
        speech_key = sys_conf['AZURE_SPEECH_KEY']
        service_region = sys_conf['AZURE_SPEECH_REGION']

        speech_config = speechsdk.SpeechConfig(
            subscription=speech_key, 
            region=service_region
        )
        speech_config.speech_recognition_language = "ar-EG"

        audio_input = speechsdk.AudioConfig(filename=file_path)
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, 
            audio_config=audio_input
        )

        result = recognizer.recognize_once_async().get()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            logger.info("Transcription completed: %s", result.text)
            return result.text

        elif result.reason == speechsdk.ResultReason.NoMatch:
            error_msg = f"No speech recognized: {result.no_match_details}"
            logger.warning(error_msg)
            raise SpeechToTextError(error_msg)

        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            error_msg = f"Speech recognition canceled: {cancellation.reason}"
            logger.error(error_msg)
            raise SpeechToTextError(error_msg)
            
    except FileNotFoundError:
        logger.error("Audio file not found: %s", file_path)
        raise
    except Exception as e:
        logger.error("Speech-to-text conversion failed: %s", str(e))
        raise SpeechToTextError(f"Transcription failed: {str(e)}")
