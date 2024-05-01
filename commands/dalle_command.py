from typing import Callable, Any

from discord.abc import Messageable

from bd import Database
from dalle import generate_images, DalleImages
from threads import launch


async def on_dalle(channel: Messageable, author_name: str, text: str, database: Database,
                   on_generate: Callable[[str], Any], dalle_listener: Callable[[DalleImages], Any]):
    database.register_user_interaction(author_name, "dalle")
    await on_generate(":clock10: Generando imagen. Puede tardar varios minutos...")
    launch(lambda: generate_images(text, dalle_listener, channel))
