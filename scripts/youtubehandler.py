import youtube_dl
import requests
import re
import os
from . import utils


# ------------------------------- #
# functions
"""
TODO:
1. find link to video
2. create array of videos
3. download array of videos as SONGS
4. save into folder!
5. nodejs is cool :D
"""


# finding a list of possible videos from youtube!
def search(prompt: str, limit: int = 5):
    """Query youtube for a series of potential songs"""
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "ignoreerrors": True,
        "simulate": True,
        "skip_download": True,
        "max_downloads": 5,
        "playliststart": 1,
        "playlistend": 5,
        "extract_flat": "in_playlist",
        "preferredcodec": "mp3",
        "preferredquality": "192",
        "no_warnings": True,
    }

    # searhc for the video
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        results = ydl.extract_info(f"ytsearch: {prompt}", download=False)["entries"]

    # get a list of urls
    BASE = "https://www.youtube.com/watch?v="
    # print(results)
    return f'{utils.remove_illegal_file_chars(str(prompt))}|{BASE + results[0]["url"]}'
