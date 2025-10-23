from flask import Flask, request, render_template, redirect
import requests
import yt_dlp

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search")
def search():
    query = request.args.get("q", "")
    results = []

    if query:
        # ----- Images via Google Custom Search API -----
        API_KEY = "YOUR_GOOGLE_API_KEY"
        CX = "YOUR_CUSTOM_SEARCH_ENGINE_ID"
        img_url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={CX}&searchType=image&key={API_KEY}"
        try:
            r = requests.get(img_url).json()
            for item in r.get("items", []):
                results.append({"title": item["title"], "url": item["link"], "type": "image"})
        except:
            pass

        # ----- YouTube videos via yt_dlp -----
        ydl_opts = {'quiet': True, 'skip_download': True, 'extract_flat': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch5:{query}", download=False)
                for video in info['entries']:
                    results.append({"title": video['title'], "url": video['webpage_url'], "type": "video"})
            except:
                pass

    return render_template("index.html", results=results, query=query)

@app.route("/download")
def download():
    url = request.args.get("url")
    q = request.args.get("quality", "360")
    t = request.args.get("type", "video")

    ydl_opts = {'quiet': True}

    if t == "mp3":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': q
            }]
        })
    else:
        ydl_opts.update({'format': f'bestvideo[height<={q}]+bestaudio/best'})

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        file_url = info_dict['url']

    return redirect(file_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
