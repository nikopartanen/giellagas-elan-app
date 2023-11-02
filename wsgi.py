import os
import xml.etree.ElementTree as ET
from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
Bootstrap(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

ALLOWED_EXTENSIONS = {'eaf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_eaf_statistics(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    annotations = root.findall('.//ANNOTATION')
    num_annotations = len(annotations)
    return {'num_annotations': num_annotations}

@app.route('/', methods=['GET'])
def upload():
    return render_template('upload.html')

@app.route('/results', methods=['POST'])
def results():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return render_template('upload.html', error='No selected file')

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        try:
            statistics = get_eaf_statistics(file_path)
            return render_template('results.html', statistics=statistics)
        except ET.ParseError:
            error = "The uploaded file is not a valid .eaf XML file."
            return render_template('upload.html', error=error)

    return render_template('upload.html', error='Invalid file extension')

if __name__ == '__main__':
    app.run(debug=True)
