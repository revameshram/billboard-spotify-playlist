from bs4 import BeautifulSoup
import requests
import datetime as d
from datetime import timedelta
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

# Crendentials

load_dotenv()

CLIENT_ID=os.getenv("CLIENT_ID")
CLIENT_SECRET=os.getenv("CLIENT_SECRET")


REDIRECTED_URI="http://127.0.0.1:8888/callback"

# date-input
date= input( "what year you would like to travel to in YYY-MM-DD format: ")

try:
    today = d.datetime.strptime(date,"%Y-%m-%d")
except:
    print("INVALID DATE FORMAT.")
    
# check day   
if today.weekday()!=5:
    days_to_substract=(today.weekday() + 2)%7
    today-=timedelta(days=days_to_substract)


header={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"}
url=f"https://www.billboard.com/charts/hot-100/{today.strftime('%Y-%m-%d')}"

# gets billboard info 
response=requests.get(url=url,headers=header)
contents=response.text

if response.status_code != 200:
    print(f"❌ Failed to fetch Billboard chart for {date}. Status code: {response.status_code}")
    exit()

#gets songs list 
soup=BeautifulSoup(contents,"html.parser")
song_rows = soup.find_all("li", class_="o-chart-results-list__item")

songs = []
for row in song_rows:
    title_tag = row.find("h3", id="title-of-a-story")
    artist_tag = title_tag.find_next("span") if title_tag else None
    if title_tag and artist_tag:
        title = title_tag.get_text(strip=True)
        artist = artist_tag.get_text(strip=True)
        songs.append((title, artist))
        

if not songs:
    print("❌ No songs found. Billboard layout may have changed.")
    exit()

#creates spotify object 
sp=spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECTED_URI,
    scope="playlist-modify-private"
))

name=sp.current_user()['id']
billboard_playlist = sp.user_playlist_create(user=name, name=f"My billboard Playlist : {today.strftime('%Y-%m-%d')}", public=False)
playlist_id=billboard_playlist["id"]

# add songs into my account
track_uris = []

for title, artist in songs:
    query = f"track:{title} artist:{artist}"
    result = sp.search(q=query, type="track", limit=1)
    tracks = result["tracks"]["items"]
    if tracks:
        uri = tracks[0]["uri"]
        track_uris.append(uri)

# Add to playlist (Spotify allows 100 at once)
sp.playlist_add_items(playlist_id=playlist_id, items=track_uris)
print("✅ Songs added to your playlist!")
