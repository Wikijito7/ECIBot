import yt_dlp
import os

yt_base_url = "./yt/"
MAX_VIDEO_DURATION = 86400 # in seconds, 6 minutes atm
MAX_VIDEO_SIZE = 800 * 1024 * 1024 # in bytes

def check_base_dir():
    if not os.path.exists(yt_base_url):
        os.makedirs(yt_base_url)


def clear_yt():
    check_base_dir()
    for file in os.listdir(yt_base_url):
        os.remove(os.path.join(yt_base_url, file))


def get_video_info(url):
    try: 
        ydl_opts = {
            'outtmpl':f'{yt_base_url}%(title)s.%(ext)s',
            'extractaudio': True,
            'format': '249/250/251/http-950/m4a/worst',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '92',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    except Exception:
        return None

def get_youtube_dlp_video(url, listener):
    check_base_dir()
    print(f"youtube: get_youtube_video >> {url}")
    ydl_opts = {
        'outtmpl':f'{yt_base_url}%(title)s.%(ext)s',
        'extractaudio': True,
        'format': '249/250/251/http-950/m4a/worst',
        'progress_hooks': [listener],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
