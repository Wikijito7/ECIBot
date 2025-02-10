from typing import Callable, Any

from discord import Guild, VoiceClient

from database import Database


async def on_stop(guild: Guild, author_name: str, database: Database, on_message: Callable[[str], Any]):
    if guild is not None:
        voice_client = guild.voice_client
        if isinstance(voice_client, VoiceClient):
            database.register_user_interaction(author_name, "stop")
            voice_client.stop()
            await on_message(":stop_button: Sonido parado.")
    else:
        await on_message("No estás conectado a un servidor :angry:")
