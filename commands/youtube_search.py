from typing import Callable, Any

from discord.abc import Messageable
from discord.channel import VocalGuildChannel

from database import Database
from commands.play import on_play
from guild_queue import add_to_queue
from voice import generate_sounds_from_yt_dlp_info
from youtube import yt_search_and_extract_yt_dlp_info, yt_music_search_and_extract_yt_dlp_info


async def on_search_in_youtube(author_name: str, query: str, guild_id: int, voice_channel: VocalGuildChannel,
                               channel: Messageable, database: Database, on_search: Callable[[str], Any]):
    database.register_user_interaction(author_name, "youtube")
    await on_search(f":clock10: Buscando `{query}` en YouTube...")
    yt_dlp_info = yt_search_and_extract_yt_dlp_info(query)
    if yt_dlp_info is not None:
        async for sound in generate_sounds_from_yt_dlp_info(channel, yt_dlp_info):
            await add_to_queue(guild_id, voice_channel, channel, sound)
    else:
        await channel.send(":no_entry_sign: No se ha encontrado ningún contenido.")


async def on_search_in_youtube_music(author_name: str, guild_id: int, voice_channel: VocalGuildChannel,
                                     channel: Messageable, database: Database, query: str,
                                     on_search: Callable[[str], Any]):
    await on_search(f":clock10: Buscando `{query}` en YouTube Music...")
    database.register_user_interaction(author_name, "ytmusic")
    if "#" not in query:
        query += "#songs"
    result_url = [yt_music_search_and_extract_yt_dlp_info(query).get('url')]
    if result_url is not None:
        await on_play(
            sounds=result_url,
            author_name=author_name,
            guild_id=guild_id,
            database=database,
            voice_channel=voice_channel,
            text_channel=channel
        )
    else:
        await channel.send(":no_entry_sign: No se ha encontrado ningún contenido.")
