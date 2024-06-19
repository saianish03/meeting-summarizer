from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import os
from summarize import generate_summary
import markdown 
from queue import Queue
from threading import Thread

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'upload'
app.config['SECRET_KEY'] = 'supersecretkey'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/record')
def record_audio():
    return render_template('record.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            print(type(file.filename))
            return {"status": True}, 200
            
    elif 'audio' in request.files:
        audio = request.files['audio']
        if audio.filename != '':
            filename = os.path.join(app.config['UPLOAD_FOLDER'], audio.filename)
            audio.save(filename)
            print(type(audio.filename))
            return {"status": True}, 200

    return 'Error uploading file'


@app.route('/summary/<filename>')
def show_summary_page(filename):
    summary_markdown, audio_url = summary(filename)
    return render_template('summary.html', summary=summary_markdown, audio_url=audio_url)

def generate_summary_worker(file_path, queue):
    summary_text = generate_summary(file_path)
    queue.put(summary_text)

def summary(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    summary_queue = Queue()
    thread = Thread(target=generate_summary_worker, args=(file_path, summary_queue))
    thread.start()
    thread.join()
    summary_text = summary_queue.get()
    summary_markdown = markdown.markdown(summary_text)
    audio_url = url_for('uploaded_file', filename=filename)
    print("rendering template now...")
    return summary_markdown, audio_url


@app.route('/upload/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)