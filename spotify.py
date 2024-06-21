"""Stores Spotify class."""
import spotipy

from helpers import remove_extras, normalize_title
from scores import titles_classics


class Spotify:
    """Stores all user data for the home page."""
    total_albums = 0
    eligible_albums = []

    def __init__(self, token):
        """Authorize through Spotify."""
        self.sp = spotipy.Spotify(auth=token)

    def get_eligible_albums(self):
        """Retrieve all albums saved by the user that potentially have a score."""
        self.eligible_albums = []

        saved_albums = []
        # compile every album saved by user into list
        offset = 0
        while True:
            temp = self.sp.current_user_saved_albums(limit=50, offset=offset)['items']
            if len(temp) == 0:
                break
            offset += len(temp)
            saved_albums.extend(temp)

        # get total number of albums in library
        self.total_albums = len(saved_albums)

        for i in saved_albums:
            release_year = int((i['album']['release_date'])[0:4])
            title = i['album']['name']
            title = normalize_title(title, 'library')
            artist = (' & '.join(artist['name'] for artist in i['album']['artists'])).lower()
            score = -1
            link = i['album']['external_urls']['spotify']

            normalized = remove_extras(artist + ' - ' + title)
            if release_year >= 2010 and i['album']['album_type'] == 'album':
                # potentially has fantano score
                self.eligible_albums.append(list((normalized, score, link)))
            elif normalized in titles_classics:
                # is a scored classic album
                self.eligible_albums.append(list((normalized, score, link)))

    def song_to_album(self, song):
        """Retrieve album from song."""
        album = song['track']['album']
        title = normalize_title(album['name'], 'library')
        artist = (' & '.join(artist['name'] for artist in album['artists'])).lower()
        link = album['external_urls']['spotify']
        release_year = int(album['release_date'][0:4])
        score = -1
        normalized = remove_extras(artist + ' - ' + title)
        return (normalized, score, link, release_year, album['album_type'])

    def get_elligible_albums_from_liked_songs(self):
        """Retrieve all albums from user's saved songs."""
        self.eligible_albums = []
        
        saved_albums = []
        # compile every album in 'liked songs' into list
        offset = 0
        while True:
            temp = self.sp.current_user_saved_tracks(limit=50, offset=offset)['items']
            if len(temp) == 0:
                break
            offset += len(temp)
            saved_albums.extend(map(self.song_to_album, temp))
        
        # trim duplicates
        saved_albums = list(dict.fromkeys(saved_albums))
        
        # get total number of albums in liked songs
        self.total_albums = len(saved_albums)
        
        for i in saved_albums:
            (normalized, score, link, release_year, album_type) = i
            # check elligibility
            if release_year >= 2010 and album_type == 'album':
                # potentially has fantano score
                self.eligible_albums.append(list((normalized, score, link)))
            elif normalized in titles_classics:
                # is a scored classic album
                self.eligible_albums.append(list((normalized, score, link)))