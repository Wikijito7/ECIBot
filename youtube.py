import youtube_dl
import os

yt_base_url = "./yt/"


def check_base_dir():
    if not os.path.exists(yt_base_url):
        os.makedirs(yt_base_url)


async def get_youtube_video(url, listener):
    check_base_dir()
    print(url)
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