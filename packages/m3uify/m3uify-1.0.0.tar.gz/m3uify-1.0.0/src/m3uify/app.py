import sys
import json
import os
import curses
import subprocess
import spotipy
from spotipy.oauth2 import SpotifyOAuth

CONFIG_FILE = os.path.expanduser("~/.m3uify_config.json")
TOKEN_FILE = os.path.expanduser("~/.m3uify_token.json")
SCOPES = "playlist-read-private playlist-read-collaborative"


# -------------------------------
# CONFIG SYSTEM
# -------------------------------
def save_config(client_id, client_secret):
    config = {
        "SPOTIFY_CLIENT_ID": client_id,
        "SPOTIFY_CLIENT_SECRET": client_secret
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

    print("✅ Credentials saved.")
    print("Run: m3uify")
    sys.exit(0)


def load_config():
    if not os.path.exists(CONFIG_FILE):
        print("❌ No config found!")
        print("Run: m3uify -config CLIENT_ID CLIENT_SECRET")
        sys.exit(1)

    with open(CONFIG_FILE) as f:
        config = json.load(f)

    return config["SPOTIFY_CLIENT_ID"], config["SPOTIFY_CLIENT_SECRET"]


# -------------------------------
# SPOTIFY AUTH
# -------------------------------
def get_spotify_client():
    client_id, client_secret = load_config()

    oauth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://127.0.0.1:8080/callback",
        scope=SCOPES,
        cache_path=TOKEN_FILE
    )

    token = oauth.get_access_token(as_dict=False)
    return spotipy.Spotify(auth=token)


# -------------------------------
# FETCH PLAYLISTS
# -------------------------------
def fetch_playlists(sp):
    playlists = []
    results = sp.current_user_playlists()

    while results:
        for item in results["items"]:
            playlists.append({
                "name": item["name"],
                "id": item["id"]
            })
        results = sp.next(results) if results["next"] else None

    return playlists


# -------------------------------
# SAFE TEXT TRUNCATION
# -------------------------------
def safe_text(text, width):
    if width <= 10:
        return text[:width - 1]
    if len(text) >= width - 4:
        return text[:width - 7] + "..."
    return text


# -------------------------------
# CURSES: PLAYLIST SELECTOR
# -------------------------------
def playlist_menu(stdscr, playlists):
    curses.curs_set(0)

    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)    # header
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # selected
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)   # normal

    selected = 0

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(0, 0, safe_text("Select a playlist:", width))
        stdscr.attroff(curses.color_pair(1))

        max_items = height - 3
        if max_items < 1:
            max_items = 1

        start_idx = max(0, selected - max_items + 1)
        end_idx = min(len(playlists), start_idx + max_items)

        row = 2
        for i in range(start_idx, end_idx):
            name = safe_text(playlists[i]["name"], width)

            if i == selected:
                stdscr.attron(curses.color_pair(2) | curses.A_REVERSE)
                stdscr.addstr(row, 2, "> " + name)
                stdscr.attroff(curses.color_pair(2) | curses.A_REVERSE)
            else:
                stdscr.attron(curses.color_pair(3))
                stdscr.addstr(row, 2, "  " + name)
                stdscr.attroff(curses.color_pair(3))

            row += 1

        key = stdscr.getch()

        if key == curses.KEY_UP and selected > 0:
            selected -= 1
        elif key == curses.KEY_DOWN and selected < len(playlists) - 1:
            selected += 1
        elif key in (10, 13):  # ENTER
            return playlists[selected]


# -------------------------------
# CURSES: ACTION SELECTOR
# -------------------------------
def action_menu(stdscr):
    curses.curs_set(0)

    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)

    options = ["Create M3U", "Download Songs", "Both", "Cancel"]
    selected = 0

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(0, 0, safe_text("Choose an action:", width))
        stdscr.attroff(curses.color_pair(1))

        for i, option in enumerate(options):
            if i == selected:
                stdscr.attron(curses.color_pair(2) | curses.A_REVERSE)
                stdscr.addstr(i + 2, 2, "> " + option)
                stdscr.attroff(curses.color_pair(2) | curses.A_REVERSE)
            else:
                stdscr.attron(curses.color_pair(3))
                stdscr.addstr(i + 2, 2, "  " + option)
                stdscr.attroff(curses.color_pair(3))

        key = stdscr.getch()

        if key == curses.KEY_UP and selected > 0:
            selected -= 1
        elif key == curses.KEY_DOWN and selected < len(options) - 1:
            selected += 1
        elif key in (10, 13):
            return options[selected]


# -------------------------------
# CREATE M3U FILE
# -------------------------------
def create_m3u(sp, playlist_id, playlist_name):
    playlist = sp.playlist(playlist_id)
    filename = playlist_name.replace("/", "_").replace("\\", "_") + ".m3u"

    tracks = []
    results = playlist["tracks"]

    while results:
        for item in results["items"]:
            if item["track"]:
                tracks.append(item["track"])
        results = sp.next(results) if results["next"] else None

    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")
        for track in tracks:
            title = track["name"]
            artists = ", ".join(a["name"] for a in track["artists"])
            f.write(f"{artists} - {title}\n")

    print(f"✅ M3U saved: {filename}")


# -------------------------------
# DOWNLOAD SONGS VIA SPOTDL
# -------------------------------
def download_songs(sp, playlist_id, playlist_name):
    folder = playlist_name.replace("/", "_").replace("\\", "_")

    if not os.path.exists(folder):
        os.makedirs(folder)

    print(f"🎧 Saving songs into: {folder}")

    tracks = []
    results = sp.playlist_tracks(playlist_id)

    while results:
        for item in results["items"]:
            if item["track"]:
                tracks.append(item["track"])
        results = sp.next(results) if results["next"] else None

    for track in tracks:
        title = track["name"]
        artists = ", ".join(a["name"] for a in track["artists"])
        query = f"{artists} - {title}"

        print(f"  ↳ Downloading: {query}")

        subprocess.run([
            "spotdl",
            "download",
            query,
            "--output", folder,
            "--format", "mp3"
        ])

    print("🎉 Downloads complete!")


# -------------------------------
# MAIN ENTRYPOINT FOR CLI
# -------------------------------
def run():
    # CONFIG MODE
    if len(sys.argv) >= 2 and sys.argv[1] == "-config":
        if len(sys.argv) != 4:
            print("Usage: m3uify -config CLIENT_ID CLIENT_SECRET")
            sys.exit(1)
        save_config(sys.argv[2], sys.argv[3])

    # URL MODE
    if len(sys.argv) == 2:
        sp = get_spotify_client()
        playlist_url = sys.argv[1]
        playlist = sp.playlist(playlist_url)
        create_m3u(sp, playlist["id"], playlist["name"])
        sys.exit(0)

    # INTERACTIVE MODE
    sp = get_spotify_client()
    playlists = fetch_playlists(sp)

    if not playlists:
        print("❌ No playlists found!")
        sys.exit(1)

    selected = curses.wrapper(playlist_menu, playlists)
    action = curses.wrapper(action_menu)

    pid = selected["id"]
    pname = selected["name"]

    if action == "Create M3U":
        create_m3u(sp, pid, pname)

    elif action == "Download Songs":
        download_songs(sp, pid, pname)

    elif action == "Both":
        create_m3u(sp, pid, pname)
        download_songs(sp, pid, pname)

    else:
        print("Cancelled.")
