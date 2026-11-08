import os
from flask import Flask, render_template, request, send_from_directory
import yt_dlp

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            return render_template('index.html', error="Please enter a valid TikTok URL.")
        
        try:
            # Advanced yt-dlp options for cloud servers
            ydl_opts = {
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(id)s.%(ext)s'),
                'format': 'best',
                'noplaylist': True,
                'socket_timeout': 30,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'referer': 'https://www.tiktok.com/',
                'extractor_args': {
                    'tiktok': {
                        'app_version': ['30.2.0'],
                        'manifest_app_version': ['30.2.0'],
                    }
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = f"{info.get('id')}.{info.get('ext')}"
                
            return render_template('index.html', success=True, filename=filename)
        except Exception as e:
            error_message = str(e)
            if "Unsupported URL" in error_message:
                error_message = "Invalid TikTok link. Please check the URL and try again."
            else:
                error_message = "TikTok is blocking cloud requests. Please try another video link."
            return render_template('index.html', error=f"Download failed: {error_message}")
            
    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
