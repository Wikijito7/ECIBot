import random
from typing import Callable, Any

from discord.abc import Messageable
from discord.channel import VocalGuildChannel

from bd import Database
from commands.play import on_play
from youtube import extract_yt_dlp_info


async def on_confetti(number_of_songs: int, author_name: str, guild_id: int, voice_channel: VocalGuildChannel,
                      channel: Messageable, database: Database, on_search: Callable[[str], Any]):
    await on_search(f":confetti_ball: Escuchando Confetti en horas de trabajo...")
    database.register_user_interaction(author_name, "confetti")
    yt_dlp_info = extract_yt_dlp_info("https://www.youtube.com/channel/UCyFr9xzU_lw9cDA69T0EmGg")
    if yt_dlp_info is not None:
        songs = yt_dlp_info.get('entries')
        if number_of_songs < len(songs):
            songs = random.sample(yt_dlp_info.get('entries'), number_of_songs)
        songs = list(map(lambda song: song.get('url'), songs))
        await on_play(
            sounds=songs,
            author_name=author_name,
            guild_id=guild_id,
            database=database,
            voice_channel=voice_channel,
            text_channel=channel
        )
