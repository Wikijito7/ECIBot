import logging as log
import traceback
from typing import Any

import yt_dlp
from yt_dlp.extractor.youtube import YoutubeIE

YT_DLP_FORMATS = 'bestaudio/251/250/249/233/234/hls-audio-128000-Audio/m4a/worstaudio/worst'
YT_DLP_EXTRACTORS = yt_dlp.extractor.gen_extractors()
MAX_PLAYLIST_ITEMS = 30


def extract_yt_dlp_info(url: str, retrieve_full_playlist: bool = False) -> Any:
    try: 
        ydl_opts = {
            'format': YT_DLP_FORMATS,
            'extract_flat': True,  # Don't try to obtain information from nested content (very slow in long playlists)
            'playlistend': None if retrieve_full_playlist else MAX_PLAYLIST_ITEMS + 1,  # Limit max playlists items by default to avoid excessive pagination and add one more to be able to check if list was too long and send message
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    except Exception:
        log.error("extract_yt_dlp_info >> Exception thrown when extracting info with yt-dlp.")
        traceback.print_exc()


def yt_search_and_extract_yt_dlp_info(search_query: str) -> Any:
    try:
        ydl_opts = {
            'format': YT_DLP_FORMATS,
            'extract_flat': True,  # Don't try to obtain information from nested content (very slow in long playlists)
            'noplaylist': True,  # Ensure playlists are discarded
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(f"ytsearch:{search_query}", download=False).get('entries')[0]

    except Exception:
        log.error("yt_search_and_extract_yt_dlp_info >> Exception thrown when extracting YouTube search info with yt-dlp.")
        traceback.print_exc()


def yt_music_search_and_extract_yt_dlp_info(search_query: str) -> Any:
    try:
        ydl_opts = {
            'format': YT_DLP_FORMATS,
            'extract_flat': True,  # Don't try to obtain information from nested content (very slow in long playlists)
            'noplaylist': True,  # We only want one video when searching
            'playlist_items': '1',  # Only get first item in lists
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(f"https://music.youtube.com/search?q={search_query}", download=False).get('entries')[0]

    except Exception:
        log.error("yt_music_search_and_get_first_result_url >> Exception thrown when extracting YouTube Music search info with yt-dlp.")
        traceback.print_exc()


def is_suitable_for_yt_dlp(url: str) -> bool:
    for extractor in YT_DLP_EXTRACTORS:
        if extractor.suitable(url) and extractor.IE_NAME != 'generic':
            return True
    return False


def is_youtube_url(url: str) -> bool:
    return YoutubeIE.suitable(url)
