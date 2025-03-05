from flask import Flask, render_template, request, redirect, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random

# 🔑 Spotify API 인증 정보 (본인의 정보 입력 필요)
SPOTIPY_CLIENT_ID = "a8d532369a5042129f6db399e92d6d9d"
SPOTIPY_CLIENT_SECRET = "a75e9fe5038048f398b9fa6486f6dc49"
SPOTIPY_REDIRECT_URI = "http://localhost:8888/callback"

# 🎶 Spotify API 인증 (사용자 인증 필요 - OAuth 사용)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="playlist-modify-public playlist-modify-private"
))

app = Flask(__name__)

# 🎭 기분별 키워드 (Rock, Alternative Rock, Metal)
mood_keywords = {
    "기분 좋아!": {"Rock": ["happy rock", "feel-good rock"], 
                   "Alternative Rock": ["upbeat alternative", "happy indie"], 
                   "Metal": ["melodic metal", "power metal"]},
    "짜증 나!": {"Rock": ["angry rock", "hard rock"], 
                 "Alternative Rock": ["grunge", "angsty alternative"], 
                 "Metal": ["aggressive metal", "thrash metal"]},
    "우울해…": {"Rock": ["melancholic rock", "sad rock"], 
                "Alternative Rock": ["emo rock", "sad indie"], 
                "Metal": ["doom metal", "gothic metal"]},
    "에너지가 넘쳐!": {"Rock": ["high-energy rock", "punk rock"], 
                      "Alternative Rock": ["fast-paced alternative", "dance rock"], 
                      "Metal": ["speed metal", "progressive metal"]},
    "고독해…": {"Rock": ["atmospheric rock", "dark rock"], 
               "Alternative Rock": ["dream pop", "moody alternative"], 
               "Metal": ["black metal", "ambient metal"]}
}

def get_playlist_by_mood_and_genre(mood, genre):
    """사용자의 기분과 장르 선택에 맞는 노래 추천"""
    if mood not in mood_keywords or genre not in ["Rock", "Alternative Rock", "Metal"]:
        return None, None

    search_query = random.choice(mood_keywords[mood][genre])  # 랜덤 키워드 선택
    results = sp.search(q=search_query, limit=5, type='track')  # 노래 검색 (5곡)

    playlist = []
    song_uris = []
    
    for track in results['tracks']['items']:
        song_name = track['name']
        artist = track['artists'][0]['name']
        spotify_url = track['external_urls']['spotify']
        song_uri = track['uri']  # 노래 URI 가져오기
        song_uris.append(song_uri)
        playlist.append({"name": song_name, "artist": artist, "url": spotify_url})

    return playlist, song_uris

def create_spotify_playlist(username, playlist_name, song_uris):
    """Spotify 계정에 새로운 플레이리스트를 생성하고 노래 추가"""
    playlist = sp.user_playlist_create(user=username, name=playlist_name, public=True)
    playlist_id = playlist['id']
    sp.playlist_add_items(playlist_id, song_uris)
    return playlist['external_urls']['spotify']

@app.route("/", methods=["GET", "POST"])
def home():
    playlist = []
    spotify_link = None

    if request.method == "POST":
        user_mood = request.form.get("mood")
        user_genre = request.form.get("genre")
        
        playlist, song_uris = get_playlist_by_mood_and_genre(user_mood, user_genre)

        if request.form.get("create_playlist") and playlist:
            user_info = sp.current_user()
            username = user_info['id']
            playlist_name = f"{user_mood} - {user_genre} Playlist"
            spotify_link = create_spotify_playlist(username, playlist_name, song_uris)

    return render_template("index.html", playlist=playlist, spotify_link=spotify_link)

if __name__ == "__main__":
    app.run(debug=True)
