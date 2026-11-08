import os
from flask import Flask, render_template, request, send_from_directory
import requests

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
            # Using Cobalt API / alternative public loader which works smoothly on cloud servers
            api_url = "https://co.wuk.sh/api/json"
            payload = {
                "url": url,
                "vQuality": "max"
            }
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
            
            response = requests.post(api_url, json=payload, headers=headers, timeout=20)
            data = response.json()
            
            if data.get('status') == 'stream' or data.get('status') == 'redirect':
                video_url = data.get('url')
                video_id = "tiktok_video"
                
                video_response = requests.get(video_url, headers=headers, timeout=20)
                filename = f"{video_id}.mp4"
                file_path = os.path.join(DOWNLOAD_FOLDER, filename)
                
                with open(file_path, 'wb') as f:
                    f.write(video_response.content)
                    
                return render_template('index.html', success=True, filename=filename)
            else:
                return render_template('index.html', error="Download failed: Could not fetch video from this link. Try another one.")
                
        except Exception as e:
            return render_template('index.html', error=f"Download failed: {str(e)}")
            
    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
