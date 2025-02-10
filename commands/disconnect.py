from typing import Callable, Any

from discord import Guild, VoiceClient

from database import Database
from guild_queue import get_guild_queue
from voice import stop_and_disconnect


async def on_disconnect(guild: Guild, author_name: str, database: Database, on_message: Callable[[str], Any]):
    if guild is not None:
        voice_client = guild.voice_client
        if isinstance(voice_client, VoiceClient):
            database.register_user_interaction(author_name, "disconnect")
            guild_queue = get_guild_queue(guild.id)
            if guild_queue is not None:
                guild_queue.clear_sound_queue()
            await stop_and_disconnect(voice_client)
            await on_message(":robot: Desconectando...")
    else:
        await on_message("No estás conectado a un servidor :angry:")
