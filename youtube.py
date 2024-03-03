import yt_dlp

yt_dlp_formats = 'bestaudio/251/250/249/233/234/hls-audio-128000-Audio/m4a/worstaudio/worst'
yt_dlp_extractors = yt_dlp.extractor.gen_extractors()

def extract_yt_dlp_info(url):
    try: 
        ydl_opts = {
            'format': yt_dlp_formats,
            'extract_flat': True, # Don't try to obtain information from nested content (very slow in long playlists)
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    except Exception:
        return None


def yt_search_and_extract_yt_dlp_info(search_query):
    try:
        ydl_opts = {
            'format': yt_dlp_formats,
            'extract_flat': True, # Don't try to obtain information from nested content (very slow in long playlists)
            'noplaylist': True, # Ensure playlists are discarded
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(f"ytsearch:{search_query}", download=False).get('entries')[0] # Return first result

    except Exception:
        return None


def yt_music_search_and_get_first_result_url(search_query):
    try:
        ydl_opts = {
            'format': yt_dlp_formats,
            'extract_flat': True, # Don't try to obtain information from nested content (very slow in long playlists)
            'noplaylist': True, # We only want one video when searching
            'playlist_items': '1', # Only get first item in lists
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(f"https://music.youtube.com/search?q={search_query}", download=False).get('entries')[0].get('url')

    except Exception:
        return None


def is_suitable_for_yt_dlp(url):
    for extractor in yt_dlp_extractors:
        if extractor.suitable(url) and extractor.IE_NAME != 'generic':
            return True
    return False
