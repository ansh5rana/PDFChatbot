from flask import Flask, request, render_template, jsonify, Response
from werkzeug.utils import secure_filename
from pdf_processor import processQuery

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        filename = secure_filename(file.filename)
        file.save(filename)
        
        question = request.form['question']
        response = processQuery(filename, question)

        return render_template('template.html', response=response)

    return render_template('template.html')

if __name__ == '__main__':
    app.run()