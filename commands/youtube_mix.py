from typing import Callable, Any

from discord.abc import Messageable
from discord.channel import VocalGuildChannel
from ytmusicapi import YTMusic

from bd import Database
from commands.play import on_play
from youtube import (is_youtube_url, extract_yt_dlp_info, yt_music_search_and_extract_yt_dlp_info,
                     yt_search_and_extract_yt_dlp_info)


async def on_youtube_mix(arg: str, author_name: str, guild_id: int, voice_channel: VocalGuildChannel,
                         channel: Messageable, database: Database, on_message: Callable[[str], Any]):
    database.register_user_interaction(author_name, "youtubemix")
    if arg.startswith("http://") or arg.startswith("https://"):
        if is_youtube_url(arg):
            yt_dlp_info = extract_yt_dlp_info(arg)
        else:
            await on_message(f":no_entry_sign: Solo se puede crear un mix de un vídeo de YouTube.")
            return
    else:
        yt_dlp_info = yt_search_and_extract_yt_dlp_info(arg)
    if yt_dlp_info is not None and yt_dlp_info.get('id') is not None:
        title = yt_dlp_info.get('title')
        video_id = yt_dlp_info.get('id')
        url = f"https://www.youtube.com/watch?v={video_id}&list=RD{video_id}"
        sounds = [url]
        await on_message(f":twisted_rightwards_arrows: Añadiendo el mix de `{title}`...")
        await on_play(
            sounds=sounds,
            author_name=author_name,
            guild_id=guild_id,
            database=database,
            voice_channel=voice_channel,
            text_channel=channel
        )
    else:
        await on_message(":no_entry_sign: No se ha encontrado ningún contenido.")


async def on_youtube_music_mix(arg: str, author_name: str, guild_id: int, voice_channel: VocalGuildChannel,
                               channel: Messageable, database: Database, yt_music: YTMusic, on_message: Callable[[str], Any]):
    database.register_user_interaction(author_name, "youtubemusicmix")
    if arg.startswith("http://") or arg.startswith("https://"):
        if is_youtube_url(arg):
            yt_dlp_info = extract_yt_dlp_info(arg)
        else:
            await on_message(f":no_entry_sign: Solo se puede crear un mix de un vídeo de YouTube.")
            return
    else:
        yt_music_search_query = arg.rsplit("#", 1)[0] + "#songs"
        yt_dlp_info = yt_music_search_and_extract_yt_dlp_info(yt_music_search_query)
    if yt_dlp_info is not None and yt_dlp_info.get('id') is not None:
        title = yt_dlp_info.get('title')
        video_id = yt_dlp_info.get('id')
        radio_tracks = yt_music.get_watch_playlist(videoId=video_id, radio=True).get("tracks")
        sounds = list(map(lambda track: f"https://music.youtube.com/watch?v={track.get('videoId')}", radio_tracks))
        await on_message(f":twisted_rightwards_arrows: Añadiendo el mix de `{title}`...")
        await on_play(
            sounds=sounds,
            author_name=author_name,
            guild_id=guild_id,
            database=database,
            voice_channel=voice_channel,
            text_channel=channel
        )
    else:
        await on_message(":no_entry_sign: No se ha encontrado ningún contenido.")
