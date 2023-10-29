#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
import os
import xml.etree.ElementTree as ET

application = Flask(__name__)
application.config['UPLOAD_FOLDER'] = 'uploads'
Bootstrap(app)

if not os.path.exists(application.config['UPLOAD_FOLDER']):
    os.makedirs(application.config['UPLOAD_FOLDER'])

@application.route('/', methods=['GET'])
def upload():
    return render_template('upload.html')

@application.route('/results', methods=['POST'])
def results():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(application.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        try:
            statistics = get_eaf_statistics(file_path)
            return render_template('results.html', statistics=statistics)
        except ET.ParseError:
            error = "The uploaded file is not a valid .eaf XML file."
            return render_template('upload.html', error=error)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'eaf'

def get_eaf_statistics(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    annotations = root.findall('.//ANNOTATION')
    num_annotations = len(annotations)
    return {
        'num_annotations': num_annotations,
    }

if __name__ == '__main__':
    application.run(debug=True)
