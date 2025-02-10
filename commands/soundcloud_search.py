from typing import Callable, Any

from discord.abc import Messageable
from discord.channel import VocalGuildChannel

from bd import Database
from guild_queue import add_to_queue
from voice import generate_sounds_from_yt_dlp_info
from youtube import soundcloud_search_and_extract_yt_dlp_info


async def on_search_in_soundcloud(author_name: str, query: str, guild_id: int, voice_channel: VocalGuildChannel,
                               channel: Messageable, database: Database, on_search: Callable[[str], Any]):
    database.register_user_interaction(author_name, "soundcloud")
    await on_search(f":clock10: Buscando `{query}` en Soundcloud...")
    yt_dlp_info = soundcloud_search_and_extract_yt_dlp_info(query)
    if yt_dlp_info is not None:
        async for sound in generate_sounds_from_yt_dlp_info(channel, yt_dlp_info):
            await add_to_queue(guild_id, voice_channel, channel, sound)
    else:
        await channel.send(":no_entry_sign: No se ha encontrado ninguna canción.")
