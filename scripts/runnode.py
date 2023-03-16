import subprocess
from . import youtubehandler, utils

import os
from typing import List
import time


# ------------------------------- #
# script

SCRIPT = """const ytdl = require("ytdl-core");
const fs = require("fs");
const ytsa = require('youtube-search-api');

// ----------------------------------------------
// using https://github.com/damonwonghv/youtube-search-api
// ----------------------------------------------

// find how to insert link to download
// or LINKS to download
const args = process.argv;
const BASEYT = "https://www.youtube.com/watch?v=";

// download all the songs using ytdl
async function download_audio(link, title, download_path) {
    // generate path

    // console.log(`LOG|${link}`)
    var path = download_path + "/" + title + ".mp3";
    // create stream object
    let stream = ytdl(link, {
        filter: "audioonly",
        quality: "highestaudio",
    });

    // download
    console.log(`START|${title}`);
    stream.pipe(fs.createWriteStream(path));
    // stream.on('progress', (chunkLength, downloaded, total) => {
    //     const percent = downloaded / total;
    //     console.log(`UPDATE|${title}|${(percent * 100).toFixed(2)}%`);
    //     // new Promise((resolve) => { setTimeout(() => {}, 100); });
    // });
    stream.on('finish', () => {
        console.log(`FINISHED|${title}`);
    });
}


// ----------------------------------------------
// download songs -- in batches of 5

var path = args[1];
for (var index = 2; index < args.length; index++) {
    try{
        // grab the link
        let link = args[index];
        console.log(index, link);
        let results = ytsa.GetListByKeyword(link, false, 1);
        results.then(function (results) {
            // console.log(results);
            if(results["items"].length == 0) {
                console.log(`ERROR|${link}|No results found`);
                return;
            }
            let vID = BASEYT + results["items"][0].id;
            // download the song
            download_audio(vID, link, path);
        });
    } catch (e) {
        console.log(e);
    }
}"""

# ------------------------------- #
# function


def download_songs(songs: List[str], path: str = "assets"):
    """Download songs from youtube"""
    # check if path exists
    if not os.path.exists(path):
        os.mkdir(path)

    # get links for videos -- to collect songs
    print("=== collecting data from youtube ===")
    custom_vars = [path] + \
        [utils.remove_illegal_file_chars(str(name)) for name in songs]

    # print(custom_vars)
    print("=== start downloading ===")
    command = ["node", "-e", SCRIPT] + custom_vars

    # =============================== #
    # call a process to run the node script and pipe console output to seprate thread
    process = subprocess.Popen(command)

    # wait for the process to finish
    process.wait()

    # get the return code
    rc = process.poll()

    # generate a list of paths to downloaded files
    return [os.path.join(path, x + ".mp3") for x in custom_vars]


def save_paths_to_file(paths: List[str], file_path: str):
    """Save a list of paths to a file"""
    with open(file_path, "w") as f:
        f.write("\n".join(paths))
