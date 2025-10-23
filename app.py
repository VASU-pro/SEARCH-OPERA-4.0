from flask import Flask, request, render_template, redirect
import os
import requests
import yt_dlp

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    results = []

    if not query:
        return render_template("index.html", results=[], query=query)

    # --- IMAGE SEARCH (optional, works only if API keys are set) ---
    API_KEY = os.getenv("GOOGLE_API_KEY")
    CX = os.getenv("GOOGLE_CX")
    if API_KEY and CX:
        try:
            api_url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={CX}&searchType=image&key={API_KEY}"
            r = requests.get(api_url).json()
            for item in r.get("items", []):
                results.append({
                    "title": item.get("title", "Image"),
                    "url": item.get("link"),
                    "type": "image"
                })
        except:
            pass

    # --- YOUTUBE VIDEO SEARCH ---
    ydl_opts = {"quiet": True, "skip_download": True, "extract_flat": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch5:{query}", download=False)
            for entry in info.get("entries", []):
                results.append({
                    "title": entry.get("title", "Video"),
                    "url": entry.get("webpage_url"),
                    "type": "video"
                })
        except:
            pass

    return render_template("index.html", results=results, query=query)


@app.route("/download")
def download():
    url = request.args.get("url")
    quality = request.args.get("quality", "360")
    filetype = request.args.get("type", "video")

    ydl_opts = {"quiet": True}

    # --- Audio formats ---
    if filetype == "mp3":
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": quality
            }]
        })
    else:
        ydl_opts.update({"format": f"bestvideo[height<={quality}]+bestaudio/best"})

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        download_url = info.get("url")

    return redirect(download_url)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

