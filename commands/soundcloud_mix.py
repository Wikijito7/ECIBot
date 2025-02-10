from typing import Callable, Any

from discord.abc import Messageable
from discord.channel import VocalGuildChannel
from yt_dlp.extractor.soundcloud import SoundcloudIE

from bd import Database
from commands.play import on_play
from youtube import extract_yt_dlp_info, soundcloud_search_and_extract_yt_dlp_info


async def on_soundcloud_mix(arg: str, author_name: str, guild_id: int, voice_channel: VocalGuildChannel,
                               channel: Messageable, database: Database, on_message: Callable[[str], Any]):
    database.register_user_interaction(author_name, "soundcloudmix")
    if arg.startswith("http://") or arg.startswith("https://"):
        if SoundcloudIE.suitable(arg):
            yt_dlp_info = extract_yt_dlp_info(arg)
        else:
            await on_message(f":no_entry_sign: Solo se puede crear un mix de una canción de Soundcloud.")
            return
    else:
        yt_dlp_info = soundcloud_search_and_extract_yt_dlp_info(arg)
    if yt_dlp_info is not None and yt_dlp_info.get('id') is not None:
        title = yt_dlp_info.get('title')
        song_id = yt_dlp_info.get('id')
        url = f"https://soundcloud.com/discover/sets/track-stations:{song_id}"
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
