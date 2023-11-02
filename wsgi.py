import os
import xml.etree.ElementTree as ET
from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

application = Flask(__name__)
application.config['UPLOAD_FOLDER'] = 'uploads'
Bootstrap(application)

if not os.path.exists(application.config['UPLOAD_FOLDER']):
    os.makedirs(application.config['UPLOAD_FOLDER'])

ALLOWED_EXTENSIONS = {'eaf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_eaf_statistics(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    annotations = root.findall('.//ANNOTATION')
    num_annotations = len(annotations)
    return {'num_annotations': num_annotations}

def transform_eaf(file_path):
    # Sample transformation: Here, I'm just parsing the file and saving it without changes.
    # You can add your transformation logic here.
    tree = ET.parse(file_path)
    transformed_path = os.path.join(application.config['UPLOAD_FOLDER'], 'annotated_' + os.path.basename(file_path))
    tree.write(transformed_path)
    return transformed_path

@application.route('/', methods=['GET'])
def upload():
    return render_template('upload.html')

@application.route('/results', methods=['POST'])
def results():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return render_template('upload.html', error='No selected file')

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(application.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        try:
            statistics = get_eaf_statistics(file_path)
            
            # Example transformation (adjust as needed)
            transformed_file_path = transform_eaf(file_path)
            transformed_filename = os.path.basename(transformed_file_path)
            
            return render_template('results.html', 
                                   statistics=statistics,
                                   download_filename=transformed_filename)
        except ET.ParseError:
            error = "The uploaded file is not a valid .eaf XML file."
            return render_template('upload.html', error=error)

    return render_template('upload.html', error='Invalid file extension')

@application.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(application.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    application.run(debug=True)
