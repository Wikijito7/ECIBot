from discord.abc import Messageable
from discord.channel import VocalGuildChannel

from database import Database
from guild_queue import add_to_queue
from voice import generate_sounds


async def on_play(sounds: list[str], author_name: str, guild_id: int, database: Database,
                  voice_channel: VocalGuildChannel, text_channel: Messageable):
    async for sound in generate_sounds(text_channel, *sounds):
        database.register_user_interaction_play_sound(author_name, sound)
        await add_to_queue(guild_id, voice_channel, text_channel, sound)
