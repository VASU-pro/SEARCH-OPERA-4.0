from flask import Flask, request, render_template, redirect
import requests
import yt_dlp

app = Flask(__name__)

MAX_RESULTS = 50  # limit for both images and videos

# ----------------------------
# Home Page
# ----------------------------
@app.route("/")
def home():
    return render_template("index.html")

# ----------------------------
# Search YouTube Videos
# ----------------------------
@app.route("/search_videos")
def search_videos():
    query = request.args.get("q", "")
    videos = []

    if query:
        ydl_opts = {'quiet': True, 'skip_download': True, 'extract_flat': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch{MAX_RESULTS}:{query}", download=False)
                for video in info['entries']:
                    videos.append({"title": video['title'], "url": video['webpage_url']})
            except:
                pass

    return render_template("index.html", videos=videos, video_query=query)

# ----------------------------
# Search Google Images
# ----------------------------
@app.route("/search_images")
def search_images():
    query = request.args.get("q", "")
    images = []

    if query:
        # Google Custom Search API - image search
        API_KEY = "YOUR_GOOGLE_API_KEY"
        CX = "YOUR_CUSTOM_SEARCH_ENGINE_ID"

        url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={CX}&searchType=image&num={MAX_RESULTS}&key={API_KEY}"
        try:
            resp = requests.get(url).json()
            for item in resp.get("items", []):
                img = {
                    "title": item["title"],
                    "url": item["link"],
                    "sizes": {},  # small/medium/large
                    "similar": item.get("image", {}).get("contextLink")  # optional
                }

                # Add size links if available
                if "image" in item and "thumbnailLink" in item["image"]:
                    img["sizes"]["Small"] = item["image"]["thumbnailLink"]
                    img["sizes"]["Medium"] = item["link"]  # default main image
                    img["sizes"]["Large"] = item["link"]

                # Add similar images search (using contextLink as placeholder)
                if "image" in item and "contextLink" in item["image"]:
                    img["similar"] = query  # placeholder, normally would extract similar query

                images.append(img)
        except:
            pass

    return render_template("index.html", images=images, image_query=query)

# ----------------------------
# Download Route for YouTube
# ----------------------------
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

