from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)
RECEIVED_FOLDER = 'decrypted'
os.makedirs(RECEIVED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    files = os.listdir(RECEIVED_FOLDER)
    return render_template('received.html', files=files)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(RECEIVED_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(port=5001, debug=True)
