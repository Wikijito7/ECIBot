import yt_dlp

DOWNLOAD_FORMATS = '251/250/249/http-950/m4a/worst'

def extract_yt_dlp_info(url):
    try: 
        ydl_opts = {
            'extractaudio': True,
            'format': DOWNLOAD_FORMATS,
            'extract_flat': True, # Don't try to obtain information from nested content (very slow in long playlists)
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    except Exception:
        return None


def yt_search_and_extract_yt_dlp_info(search_query):
    try:
        ydl_opts = {
            'extractaudio': True,
            'format': DOWNLOAD_FORMATS,
            'extract_flat': True, # Don't try to obtain information from nested content (very slow in long playlists)
            'noplaylist': True, # Ensure playlists are discarded
            'playlist_count': 1 # Only get one result
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(f"ytsearch:{search_query}", download=False).get('entries')[0] # Return first result

    except Exception:
        return None


def is_suitable_for_yt_dlp(url):
    extractors = yt_dlp.extractor.gen_extractors()
    for e in extractors:
        if e.suitable(url) and e.IE_NAME != 'generic':
            return True
    return False