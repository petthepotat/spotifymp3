import subprocess
import sys
import os

import PIL
from PIL import Image, ImageDraw, ImageOps, ImageFilter, ImageStat

from typing import List, Tuple

"""

ffmpeg options:
    -i: input file
    -c:v: video codec
    -c:a: audio codec
    -b:a: audio bitrate
    -b:v: video bitrate
    -ar: audio sample rate
    
    -ss: start time
    -t: duration
    -to: end time

    -filter:a: audio filter
    -filter:v: video filter

    -pix_fmt: pixel format

    -loop 1: loop the input once

    # joining audio tracks together
    -f concat "filename"

# special option
    concat

    -safe 0: allow unsafe filenames
    -i "filename"
    -c copy: copy the streams
"""

FFMPEGPATH = "ffmpeg"

# video
TARGET_IMG = None
TIMEDURATIONARG = "-t"
LOOPARG = "-loop"
LOOPDEF = "1"
PIXELFORMATARG = "-pix_fmt"
PIXELFORMATDEF = "yuv420p"
VIDEOCODECARG = "-c:v"
VIDEOCODECDEF = "libx264"


# audio
SILENCE = ".blob/silence.mp3"
AUDIOCODEC = "-codec:a libmp3lame"
AUDIOQUALITY = "-qscale:a 2"
CONCATFILE = '-f concat -i ".blob/concat.txt"'

# ------------------------------- #
# functions


def generate_image(image_file, target_path: str = ".blob/result.jpg"):
    """Generate an image file"""
    # create a new image
    back = Image.new("RGBA", (1920, 1080), (0, 0, 0))
    # open central image
    c_image = Image.open(image_file).convert("RGBA")
    # draw the background
    draw = ImageDraw.Draw(back)
    # literlaly manual grayscale maths
    # find average color value in image
    avg_color = tuple(map(int, ImageStat.Stat(c_image).mean))
    scol = tuple(map(int, ImageStat.Stat(c_image).stddev))
    # print(avg_color)

    colors = [
        (avg_color[0] - scol[0], avg_color[1] - scol[1], avg_color[2] - scol[2]),
        avg_color,
        (avg_color[0] + scol[0], avg_color[1] + scol[1], avg_color[2] + scol[2]),
    ]

    for i in range(1080):
        color = (
            int(colors[0][0] + (colors[2][0] - colors[0][0]) * i / 1080),
            int(colors[0][1] + (colors[2][1] - colors[0][1]) * i / 1080),
            int(colors[0][2] + (colors[2][2] - colors[0][2]) * i / 1080),
        )
        draw.line([(0, i), (1920, i)], fill=color)

    # draw a set of diagonal lines across the image
    slope = 1.0
    width = 10
    for i in range(0, 1080, width * 3):
        left = (0, i + width * 3)
        right = (i / slope, -width * 3)
        draw.line([left, right], fill=colors[1], width=width)
    for i in range(0, 1920, width * 3):
        left = (i, 1080 + width * 3)
        right = (1080 / slope + i, -width * 3)
        draw.line([left, right], fill=colors[1], width=width)

    # draw a rectangle that increases the luminence of a specific area
    tempback = back.convert("HSV")
    # h, s, v = tempback.split()
    # iterate through pixels in a certain area
    BORDER = 40
    for i in range(1080):
        for j in range(1920):
            # if pixel is in the area
            if (j > 1920 - BORDER or j < BORDER) or (i > 1080 - BORDER or i < BORDER):
                # increase luminence
                cval = tempback.getpixel((j, i))
                s = int(cval[1] * 0.6)
                tempback.putpixel((j, i), (cval[0], s if s < 255 else 255, cval[2]))

    back = tempback.convert("RGBA")

    # center image on gradient back
    bw, bh = back.size
    iw, ih = c_image.size
    offset = ((bw - iw) // 2, (bh - ih) // 2)
    # add shadow to image
    shadow = ImageOps.colorize(
        # the white = (255, 255, 255, 100) reduces alpha value
        ImageOps.invert(c_image.convert("L")),
        (0, 0, 0, 0),
        (255, 255, 255, 255),
    )
    # resize image ==> then scale to background
    # shadow = shadow.resize((1920, 1920), Image.ANTIALIAS)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=15))
    # steal alpha + reduce alpha
    # r, g, b, ash = shadow.convert("RGBA").split()
    # a = ash.point(lambda x: 100)
    # remerge
    # shadow = Image.merge("RGBA", (r, g, b, ash))

    shadow_offset = (bw - shadow.width) // 2 + 15, (bh - shadow.height) // 2 + 15
    back.paste(shadow, shadow_offset)
    # add image to background
    back.paste(c_image, offset)

    # save the image
    back = back.convert("RGB")
    back.save(target_path)
    return target_path


def generate_mp4(image_file, audio_files, output_file):
    audio_list_file = "audio_list.txt"

    with open(audio_list_file, "w") as f:
        for audio_file in audio_files:
            f.write("file '{}'\n".format(audio_file))
            f.write("file '{}'\n".format(SILENCE))

    if not os.path.exists(SILENCE):
        # create silence.wav
        subprocess.run(
            [
                "ffmpeg",
                "-f",
                "lavfi",
                "-i",
                "anullsrc=r=48000:cl=stereo",
                "-t",
                "3",
                SILENCE,
            ]
        )

    # concatenate audio files
    cmd = [
        "ffmpeg",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        audio_list_file,
        "-loop",
        "1",
        "-i",
        image_file,
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-pix_fmt",
        "yuv420p",
        "-shortest",
        output_file,
    ]
    subprocess.run(cmd)

    # remove audio_list_file and silence.wav
    os.remove(audio_list_file)
    # os.remove("silence.wav")


def generate_video_from_songs(image_file, audio_files, output_file):
    """Generate a video from a list of audio files"""
    path = generate_image(image_file)
    generate_mp4(path, audio_files, output_file)


# TODO: speeding up audio!

# ------------------------------- #
# testing

# generate_image(
#     # ".blob/image.jpg",
#     ".blob/image.jfif",
#     ".blob/temp.jpg",
# )

# generate_mp4(".blob/temp.jpg", ["assets/test.mp3", "assets/test.mp3"], "result.mp4")
# generate_video_from_songs(
#     ".blob/image.jfif", ["assets/test.mp3", "assets/test.mp3"], "result.mp4"
# )

generate_video_from_songs(
    input("Image path: "),
    open(input("Audio Concat File: "), "r").read().split("\n"),
    input("Output path: "),
)

"""
.blob/image.jfif
.blob/audio_concat.txt
result.mp4
"""
