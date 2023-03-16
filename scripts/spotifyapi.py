import subprocess
import requests
import json
import base64

buf = json.load(open("secret", "r"))
PRELOAD_BUF = buf

# important data
UID = buf["UID"]
CID = buf["CLIENTID"]
CSECRET = buf["CLIENTSECRET"]
REFRESHTOKEN = buf["REFRESHTOKEN"]
ACCESSTOKEN = buf["ACCESSTOKEN"]

# constants
SCOPE = "playlist-modify-private,playlist-modify-public,playlist-read-private,playlist-read-collaborative,user-read-email"
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer " + ACCESSTOKEN,
}
REDIRECT = "https://localhost"


# ------------------------------- #
# classes


class Playlist:
    def __init__(self, link: str):
        """Load data from given spotify link"""
        data = get_playlist_data_raw(link)

        # playlist general
        self.name = data["name"]
        self.description = data["description"]
        self.link = data["external_urls"]["spotify"]
        self.id = data["id"]
        # stats
        self.collaborative = data["collaborative"]
        self.followers = data["followers"]["total"]
        # content
        self.tracks = data["tracks"]["items"]
        self.songs = [Song(x["track"]) for x in self.tracks]

    def __str__(self):
        """Return string representation of playlist"""
        return f"{self.name} ({self.followers} followers)"

    def add_songs(self, songs: list):
        """Add songs to playlist"""
        base = f"https://api.spotify.com/v1/playlists/{self.id}/tracks?uris={'%2C'.join([x.uri.replace(':', '%3A') for x in songs])}"
        res = requests.post(base, headers=HEADERS)
        if res.status_code != 201:
            refresh_token_validity()
            res = requests.post(base, headers=HEADERS)
        return res.json()

    def get_songs(self):
        """Return list of Song objects"""
        return self.songs


class Song:
    def __init__(self, link: str):  # or dict
        """Get data about song"""
        if type(link) == dict:
            data = link
        else:
            data = get_song_data_raw(link)

        # song general
        self.name = data["name"]
        self.link = data["external_urls"]["spotify"]
        self.uri = data["uri"]
        # artists
        self.artists = data["artists"]
        self.artist_names = [artist["name"] for artist in self.artists]
        # album
        self.album = data["album"]["name"]
        self.album_link = data["album"]["external_urls"]["spotify"]
        self.album_cover = data["album"]["images"][0]["url"]
        # stats
        self.popularity = data["popularity"]
        self.duration = data["duration_ms"] / 1000
        self.explicit = data["explicit"]
        # track features -- the stats of power
        self.features = self.get_song_features()
        self.danceability = self.features["danceability"]
        self.energy = self.features["energy"]
        self.key = self.features["key"]
        self.loudness = self.features["loudness"]
        self.mode = self.features["mode"]
        self.speechiness = self.features["speechiness"]
        self.acousticness = self.features["acousticness"]
        self.instrumentalness = self.features["instrumentalness"]
        self.liveness = self.features["liveness"]
        self.valence = self.features["valence"]
        self.tempo = self.features["tempo"]
        self.time_signature = self.features["time_signature"]

    def get_song_features(self):
        """Get the song features"""
        target = "https://api.spotify.com/v1/audio-features/" + self.get_song_uri_id()
        res = requests.get(target, headers=HEADERS)
        if res.status_code > 300:
            refresh_token_validity()
            res = requests.get(target, headers=HEADERS)
        return res.json()

    def get_song_uri_id(self):
        """Return the uri id of the song"""
        return self.uri.split(":")[-1]

    def __str__(self):
        """Return string representation of song"""
        return f"{self.name} by {', '.join(self.artist_names)}"


class Recommendation:
    """
    VALID arguments:
    - seed_artists (artist uri id | seprated by ,) -- to be added
    - seed_genres (genre name | seprated by)
    - seed_tracks (track uri id | seprated by ,)
    - limit (int)
    - market (str) (country code)
    - min_acousticness (float)
    - max_acousticness (float)
    - min_danceability (float)
    - max_danceability (float)
    - min_duration_ms (int)
    - max_duration_ms (int)
    - min_energy (float)
    - max_energy (float)
    - min_instrumentalness (float)
    - max_instrumentalness (float)
    - min_key (int)
    - max_key (int)
    - min_liveness (float)
    - max_liveness (float)
    - min_loudness (float)
    - max_loudness (float)
    - min_mode (int)
    - max_mode (int)
    - min_popularity (int)
    - max_popularity (int)
    - min_speechiness (float)
    - max_speechiness (float)
    - min_tempo (float)
    - max_tempo (float)
    - min_time_signature (int)
    - max_time_signature (int)
    - min_valence (float)
    - max_valence (float)

    """

    ENDPOINT = "https://api.spotify.com/v1/recommendations?"

    def __init__(
        self,
        limit: int = 10,
        market: str = "US",
        seed_artists: str = "_",
        seed_genres: str = "_",
        seed_tracks: str = "_",
        min_acousticness: float = "_",
        max_acousticness: float = "_",
        min_danceability: float = "_",
        min_duration_ms: int = "_",
        **kwargs,
    ):
        # private
        self._collected = False
        self.args = {
            "limit": limit,
            "market": market,
            "seed_artists": seed_artists,
            "seed_genres": seed_genres,
            "seed_tracks": seed_tracks,
            "min_acousticness": min_acousticness,
            "max_acousticness": max_acousticness,
            "min_danceability": min_danceability,
            "min_duration_ms": min_duration_ms,
        }
        for a, v in kwargs.items():
            self.args[a] = v

        # public
        self.recommendations = []

    def get_config_aspect_str(self, aspect: str, value: str):
        """Return the aspect string"""
        return f"{aspect}={value}"

    def generate_config_string(self):
        """Generate search configuration string"""
        return f"{self.ENDPOINT}" + "&".join(
            [
                self.get_config_aspect_str(aspect, value)
                for aspect, value in self.args.items()
                if value != "_"
            ]
        )

    def get_recommendations(self):
        """Get recommendations from spotify"""
        if self._collected:
            return self.recommendations
        self._collected = True
        # get data
        res = requests.get(self.generate_config_string(), headers=HEADERS)
        if res.status_code != 200:
            refresh_token_validity()
            res = requests.get(self.generate_config_string(), headers=HEADERS)
        # parse)
        self.recommendations = []
        result = res.json()
        tracks = result["tracks"]
        for track in tracks:
            # print(track["href"])
            self.recommendations.append(Song(track["href"]))
        return self.get_recommendations()

    @classmethod
    def generate_seed_song_array(cls, songs: list):
        """Generate seed song array"""
        return ",".join([song.get_song_uri_id() for song in songs])


# ------------------------------- #
# functions


def refresh_token_validity():
    """Checks if the token is valid."""
    global HEADERS
    print("Refreshing TOKEN")
    url = "https://accounts.spotify.com/api/token"
    message = f"{CID}:{CSECRET}"
    message_bytes = message.encode("ascii")
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode("ascii")
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESHTOKEN,
    }
    headers = {
        "Accept": "application/json",
        "Authorization": f"Basic {base64_message}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    res = requests.post(url, data=data, headers=headers)
    # print(res.json())
    # save data in file
    new_data = {
        "UID": UID,
        "CLIENTID": CID,
        "CLIENTSECRET": CSECRET,
        # "REFRESHTOKEN": res.json()['refresh_token'],
        "REFRESHTOKEN": REFRESHTOKEN,
        "ACCESSTOKEN": res.json()["access_token"],
    }
    # reset variables
    global ACCESSTOKEN
    ACCESSTOKEN = new_data["ACCESSTOKEN"]
    with open("secret", "w") as f:
        json.dump(new_data, f, indent=4)
    HEADERS["Authorization"] = f"Bearer {ACCESSTOKEN}"
    print("Token Refreshed")


def get_playlist_data_raw(link: str) -> dict:
    """Returns the data of the given playlist."""
    ll = "https://api.spotify.com/v1/playlists/"
    if len(link.split("?")) > 1:
        ll += link.split("?")[0].split("/")[-1]
    else:
        ll = link
    res = requests.get(ll, headers=HEADERS)
    if res.status_code != 200:
        refresh_token_validity()
        res = requests.get(ll, headers=HEADERS)
    return res.json()


def get_song_data_raw(link: str) -> dict:
    """Returns the data of the given song."""
    ll = "https://api.spotify.com/v1/tracks/"
    if len(link.split("?")) > 1:
        ll += link.split("?")[0].split("/")[-1]
    else:
        ll = link
    # have the track link
    # print(ll)
    res = requests.get(ll, headers=HEADERS)
    if res.status_code != 200:
        refresh_token_validity()
        res = requests.get(ll, headers=HEADERS)
    # got the data
    return res.json()


def create_playlist(name: str, des: str, public: bool = True):
    """Creates a playlist with the given name."""
    route = f"https://api.spotify.com/v1/users/{UID}/playlists"
    # post data to spotify url
    data = {"name": name, "description": des, "public": public}
    res = requests.post(route, data=json.dumps(data), headers=HEADERS)
    if res.status_code > 300:
        refresh_token_validity()
        res = requests.post(route, data=json.dumps(data), headers=HEADERS)
    pid = res.json()["id"]
    return Playlist("https://api.spotify.com/v1/playlists/" + pid)
