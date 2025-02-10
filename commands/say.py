from typing import Callable, Any

from discord import Member, Guild
from discord.abc import Messageable
from discord.channel import VocalGuildChannel

from database import Database
from threads import launch
from tts import generate_tts


async def on_tts(text: str, author: Member, guild: Guild, voice_channel: VocalGuildChannel, channel: Messageable,
                 database: Database, tts_listener: Callable[[int, VocalGuildChannel, Messageable, str], Any],
                 on_generate: Callable[[str], Any]):
    await on_generate(":tools::snail: Generando mensaje tts...")
    database.register_user_interaction(author.name, "tts")
    launch(lambda: generate_tts(text, guild.id, voice_channel, channel, tts_listener))
