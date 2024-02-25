import yt_dlp
import os

yt_base_url = "./yt/"
MAX_VIDEO_DURATION = 86400 # in seconds
MAX_VIDEO_SIZE = 800 * 1024 * 1024 # in bytes
DOWNLOAD_FORMATS = '251/250/249/http-950/m4a/worst'

def check_base_dir():
    if not os.path.exists(yt_base_url):
        os.makedirs(yt_base_url)


def clear_yt():
    check_base_dir()
    for file in os.listdir(yt_base_url):
        os.remove(os.path.join(yt_base_url, file))


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


def get_youtube_dlp_video(url, listener):
    check_base_dir()
    print(f"youtube: get_youtube_video >> {url}")
    ydl_opts = {
        'outtmpl':f'{yt_base_url}%(title)s.%(ext)s',
        'extractaudio': True,
        'format': DOWNLOAD_FORMATS,
        'progress_hooks': [listener],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
