import asyncio
import random
from ai_brain import AIBrain
from tts_engine import TTSEngine
from tiktok_listener import TikTokListener

chat_queue = asyncio.Queue()

ai = AIBrain()
tts = TTSEngine()

async def process_queue():
    while True:
        # Se acumular muitas mensagens, descarta comentários velhos para não dar lag, mas PRESERVA todos os presentes
        if chat_queue.qsize() > 3:
            temp_items = []
            while not chat_queue.empty():
                try:
                    item = chat_queue.get_nowait()
                    chat_queue.task_done()
                    temp_items.append(item)
                except asyncio.QueueEmpty:
                    break
            
            gifts = [it for it in temp_items if it[0] == "gift"]
            comments = [it for it in temp_items if it[0] == "comment"]
            
            # Prioriza presentes na fila e deixa apenas o comentário mais recente
            for g in gifts:
                await chat_queue.put(g)
            if comments:
                await chat_queue.put(comments[-1])

        item_type, data = await chat_queue.get()
        
        if item_type == "comment":
            user_name, comment = data
            print(f"\n[Processando Chat] Novo comentário de {user_name}: '{comment}'")
            response_text = await asyncio.to_thread(ai.generate_response, user_name, comment)
            if not response_text:
                response_text = random.choice(ai.fallback_responses)
        
        elif item_type == "gift":
            user_name, gift_name, count = data
            print(f"\n[Processando Presente] {user_name} enviou {count}x {gift_name}!")
            response_text = await asyncio.to_thread(ai.generate_gift_thanks, user_name, gift_name, count)

        if response_text:
            print(f"[Stickman]: {response_text}")
            await asyncio.to_thread(tts.speak, response_text)

        chat_queue.task_done()
        await asyncio.sleep(0.2)

async def on_comment_received(user: str, comment: str):
    await chat_queue.put(("comment", (user, comment)))

async def on_gift_received(user: str, gift_name: str, count: int):
    await chat_queue.put(("gift", (user, gift_name, count)))

async def main():
    asyncio.create_task(process_queue())
    listener = TikTokListener(on_comment_received, on_gift_received)
    await listener.start()

if __name__ == "__main__":
    print("=== INICIANDO SISTEMA VTUBER 24/7 (COM SUPORTE A PRESENTES) ===")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Sistema] Encerrado pelo usuário.")