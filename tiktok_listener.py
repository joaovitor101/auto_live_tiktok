from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, GiftEvent
import config

class TikTokListener:
    def __init__(self, on_comment_callback, on_gift_callback):
        self.client = TikTokLiveClient(unique_id=config.TIKTOK_USERNAME)
        self.on_comment_callback = on_comment_callback
        self.on_gift_callback = on_gift_callback

        @self.client.on(CommentEvent)
        async def on_comment(event: CommentEvent):
            user = event.user.nickname
            comment = event.comment
            print(f"[TikTok Chat] {user}: {comment}")
            await self.on_comment_callback(user, comment)

        @self.client.on(GiftEvent)
        async def on_gift(event: GiftEvent):
            # Filtra para reagir apenas quando a sequência de presentes terminar (ou presente único)
            if event.streaking:
                return  # Aguarda o término da sequência (combo) para não poluir o chat
                
            try:
                user = event.user.nickname if event.user else "Alguém"
                gift_name = getattr(event.gift, "name", None) or getattr(event.gift, "gift_name", "Presente")
                repeat_count = event.repeat_count or 1
                print(f"[TikTok Presente] {user} enviou {repeat_count}x {gift_name}!")
                await self.on_gift_callback(user, gift_name, repeat_count)
            except Exception as e:
                print(f"[Erro no evento de presente]: {e}")

    async def start(self):
        print(f"[TikTok Listener] Conectando à live de @{config.TIKTOK_USERNAME}...")
        await self.client.connect()