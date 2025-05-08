from flask import Flask, render_template, request, jsonify
import yt_dlp
import os
from threading import Thread
import tempfile

app = Flask(__name__)

progress_data = {"status": "idle", "progress": 0, "message": ""}

def download_video(url):
    # Use temp directory for Render deployment
    if os.environ.get('RENDER'):
        download_path = tempfile.gettempdir()
    else:
        download_path = os.path.join(os.path.expanduser("~"), "Downloads")
    # video_path = ""

    def progress_hook(d):
        # nonlocal video_path
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                percent = int(downloaded * 100 / total)
                progress_data["progress"] = percent
                progress_data["status"] = "downloading"
        elif d['status'] == 'finished':
            # video_path = os.path.join(download_path)
            progress_data["progress"] = 100
            progress_data["status"] = "completed"
            progress_data["message"] = f"✅ Download completed! Video saved to: {download_path}"

    ydl_opts = {
        'format': 'bestvideo[height<=1080]+bestaudio/best[ext=m4a]/best',
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
        'noplaylist': True,
        'quiet': False,  # Make sure to set it to False to see the process output
        'no_warnings': True,
        'nocheckcertificate': True  # Add this line for HTTPS support
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError:
        progress_data["status"] = "error"
        progress_data["message"] = "❌ Invalid URL or unsupported video format."
    except Exception as e:
        progress_data["status"] = "error"
        progress_data["message"] = f"❌ Error: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'URL cannot be empty.'})
    
    # Reset progress
    progress_data.update({"status": "starting", "progress": 0, "message": "⏬ Starting download..."})

    # Run download in a separate thread to avoid blocking
    Thread(target=download_video, args=(url,)).start()

    return jsonify({'status': 'started', 'message': 'Download started'})

@app.route('/progress')
def progress():
    return jsonify(progress_data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
