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
            # Create a session to handle cookies and bypass Cloudflare 403 on Render
            session = requests.Session()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.tikwm.com/',
                'Origin': 'https://www.tikwm.com',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            # Step 1: Visit homepage first to get valid session cookies (bypasses Cloudflare block)
            session.get('https://www.tikwm.com/', headers=headers, timeout=15)
            
            # Step 2: Make the API request using the same session
            api_url = f"https://www.tikwm.com/api/?url={url}"
            response = session.get(api_url, headers=headers, timeout=20)
            
            if response.status_code != 200:
                return render_template('index.html', error=f"API Server Error: Status code {response.status_code}")
                
            res_json = response.json()
            
            if res_json.get('code') == 0:
                video_data = res_json.get('data', {})
                video_url = video_data.get('play') or video_data.get('hdplay')
                video_id = video_data.get('id', 'tiktok_video')
                
                if not video_url:
                    return render_template('index.html', error="Download link not found in API response.")
                
                video_response = session.get(video_url, headers=headers, timeout=20)
                filename = f"{video_id}.mp4"
                file_path = os.path.join(DOWNLOAD_FOLDER, filename)
                
                with open(file_path, 'wb') as f:
                    f.write(video_response.content)
                    
                return render_template('index.html', success=True, filename=filename)
            else:
                return render_template('index.html', error=f"API Error: {res_json.get('msg', 'Could not fetch video.')}")
                
        except Exception as e:
            return render_template('index.html', error=f"Error: {str(e)}")
            
    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
