import youtube_dl
import os

yt_base_url = "./yt/"
MAX_VIDEO_DURATION = 360 # in seconds, 6 minutes atm


def check_base_dir():
    if not os.path.exists(yt_base_url):
        os.makedirs(yt_base_url)


def clear_yt():
    for file in os.listdir(yt_base_url):
        os.remove(os.path.join(yt_base_url, file))


def get_video_info(url):
    try: 
        ydl_opts = {
            'outtmpl':f'{yt_base_url}%(title)s.%(ext)s',
            'extractaudio': True,
            'format': 'worstaudio/140/17/36/22',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '92',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    except Exception:
        return None


def get_youtube_video(url, listener):
    check_base_dir()
    print(f"youtube: get_youtube_video >> {url}")
    ydl_opts = {
        'outtmpl':f'{yt_base_url}%(title)s.%(ext)s',
        'extractaudio': True,
        'format': 'worstaudio/140/17/36/22',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '92',
        }],
        'progress_hooks': [listener],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])