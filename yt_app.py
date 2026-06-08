import imageio_ffmpeg
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
import os
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)
from flask import Flask, request, jsonify, send_file
import yt_dlp


app = Flask(__name__)

DOWNLOAD_FOLDER = "./downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return send_file("index.html")

@app.route("/info", methods=["POST"])
def get_video():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'Please enter the URL'}), 400
    
    try:
        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(url, download=False)

        return jsonify({
            'title': info.get('title'),
            'thumbnail': info.get('thumbnail'),
            'duration': info.get('duration_string'),
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route("/download", methods=["POST"])
def download_video():
    data = request.get_json()
    url = data.get('url')
    quality = data.get('quality', '720')

    if quality == 'mp3':
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }]
        }
    else:
        ydl_opts = {
            'format': f'bestvideo[height<={quality}][vcodec^=avc]+bestaudio/best',
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',   
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return send_file(filename, as_attachment=True)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
if __name__ == "__main__":
    app.run(debug=True, port=5000)
