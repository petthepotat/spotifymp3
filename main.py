from scripts import spotifyapi, runnode, utils
import os

# while loop for user input + downloading songs

# make assets if not exist
if not os.path.exists("assets"):
    os.mkdir("assets")

print("TODO TESTING WITH https://open.spotify.com/playlist/27IxCvarpXtiRYo1igg05O?si=f175c56ef5414495")


# loop for downloading songs
while True:
    link = input("Input a playlist link: ")
    if not link:
        break
    playlist = spotifyapi.Playlist(link)

    # download songs
    paths = runnode.download_songs(
        songs=playlist.get_songs(),
        path="assets/" + utils.remove_illegal_file_chars(playlist.name),
    )
    # done
    print("Done downloading songs!")
    print("--" * 20)
