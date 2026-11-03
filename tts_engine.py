import sounddevice as sd
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
import io
import soundfile as sf
import config
import time

class TTSEngine:
    def __init__(self):
        self.client = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)
        self.voice_id = config.ELEVENLABS_VOICE_ID
        self.model_id = getattr(config, "ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
        self.device_index = self._find_device_index(getattr(config, "AUDIO_OUTPUT_DEVICE_NAME", "CABLE Input"))

    def _find_device_index(self, device_name_substr):
        devices = sd.query_devices()
        for idx, dev in enumerate(devices):
            if device_name_substr.lower() in dev['name'].lower() and dev['max_output_channels'] > 0:
                return idx
        return None

    def speak(self, text: str):
        if not text:
            return

        try:
            start_time = time.time()
            print(f"[TTS Engine] Gerando áudio humanizado ({self.model_id})...")
            
            # Usando VoiceSettings para eliminar o tom robótico e dar cadência humana
            audio_generator = self.client.text_to_speech.convert(
                voice_id=self.voice_id,
                text=text,
                model_id=self.model_id,
                voice_settings=VoiceSettings(
                    stability=0.42,         # Menor estabilidade = mais modulação natural e expressiva (menos robótico)
                    similarity_boost=0.80,  # Alta fidelidade ao timbre original
                    style=0.20,             # Adiciona expressividade sem criar ruído
                    use_speaker_boost=True
                )
            )
            
            audio_bytes = b"".join(audio_generator)
            data, samplerate = sf.read(io.BytesIO(audio_bytes))
            
            print(f"[TTS Engine] Áudio gerado em {round(time.time() - start_time, 2)}s. Reproduzindo...")
            sd.play(data, samplerate, device=self.device_index)
            sd.wait()
            print(f"[TTS Engine] Reprodução finalizada.")
        except Exception as e:
            print(f"[TTS Engine Error]: {e}")