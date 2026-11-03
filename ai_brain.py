import time
import random
from google import genai
from google.genai import types
import config

class AIBrain:
    def __init__(self):
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.system_instruction = config.SYSTEM_PROMPT
        self.model_name = 'gemini-3.5-flash-lite'
        self.backup_models = ['gemini-flash-lite-latest', 'gemini-3.5-flash']
        
        # Frases de reserva naturais de streamer
        self.fallback_responses = [
            "Opa, deu uma travadinha aqui na live, mas tô de volta!",
            "Eita, repete aí no chat que perdi essa!",
            "Tô de olho em vocês aqui no chat, tamo junto!",
            "Deu uma oscilada na conexão aqui, fala aí de novo!"
        ]

    def generate_response(self, user_name: str, message: str) -> str:
        clean_message = message.strip()
        if not clean_message:
            return ""

        prompt = f"O espectador '{user_name}' disse no chat: '{clean_message}'"
        return self._call_gemini(prompt)

    def generate_gift_thanks(self, user_name: str, gift_name: str, count: int) -> str:
        prompt = f"O espectador '{user_name}' acabou de mandar {count}x o presente '{gift_name}' na live. Agradeça de forma natural e animada!"
        response = self._call_gemini(prompt)
        
        if not response:
            return f"Valeu demais pelo presente, {user_name}! Tamo junto!"
        return response

    def _call_gemini(self, prompt: str) -> str:
        models_to_try = [self.model_name] + self.backup_models
        for model in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_instruction,
                        temperature=0.7,
                        max_output_tokens=60
                    )
                )
                if response.text and response.text.strip():
                    return response.text.strip()
            except Exception as e:
                print(f"[AI Brain Aviso]: Modelo {model} indisponível ({e}). Tentando backup...")
                continue
        
        return ""