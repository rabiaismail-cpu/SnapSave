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
            # Using a reliable public TikTok API endpoint to bypass IP blocking
            api_url = f"https://tikwm.com/api/?url={url}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(api_url, headers=headers)
            data = response.json()
            
            if data.get('code') == 0:
                video_url = data['data']['play']
                video_id = data['data']['id']
                
                # Download video file locally
                video_response = requests.get(video_url, headers=headers)
                filename = f"{video_id}.mp4"
                file_path = os.path.join(DOWNLOAD_FOLDER, filename)
                
                with open(file_path, 'wb') as f:
                    f.write(video_response.content)
                    
                return render_template('index.html', success=True, filename=filename)
            else:
                return render_template('index.html', error="Download failed: Invalid TikTok link or video is private.")
                
        except Exception as e:
            return render_template('index.html', error=f"Download failed: Server connection error.")
            
    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
