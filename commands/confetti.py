import random
from typing import Callable, Any

from discord.abc import Messageable
from discord.channel import VocalGuildChannel

from database import Database
from commands.play import on_play
from youtube import extract_yt_dlp_info


# These songs are incorrectly tagged as Confetti songs in YT Music
NOT_CONFETTI_SONGS = ['94ruVm4lK6s', '6k7rxay1MOc', 'MFU1vjivNAs', 'r9n_ssGCtl0', 'zneFDkhteTw',
                      'MRnn1i-DH4Q', 'F_Y5meRFsts', 'ktdiMQPhBgE', '3Kvz6ExY8OU']


async def on_confetti(number_of_songs: int, author_name: str, guild_id: int,
                      voice_channel: VocalGuildChannel,
                      channel: Messageable, database: Database, on_search: Callable[[str], Any]):
    await on_search(f":confetti_ball: Escuchando Confetti en horas de trabajo...")
    database.register_user_interaction(author_name, "confetti")
    yt_dlp_info = extract_yt_dlp_info(
        url="https://music.youtube.com/playlist?list=OLAK5uy_nX7fhyH24rCKS9pZ2baLnIIwc-q5yyCcY",
        retrieve_full_playlist=True
    )
    if yt_dlp_info is not None:
        entries = yt_dlp_info.get('entries')
        real_confetti_entries = [entry for entry in entries if entry.get('id') not in NOT_CONFETTI_SONGS]
        picked_confetti_entries = random.sample(real_confetti_entries, min(number_of_songs, len(real_confetti_entries)))
        song_urls = list(map(lambda entry: entry.get('url'), picked_confetti_entries))
        await on_play(
            sounds=song_urls,
            author_name=author_name,
            guild_id=guild_id,
            database=database,
            voice_channel=voice_channel,
            text_channel=channel
        )
