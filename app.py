from flask import Flask, render_template, request, send_file, session
from PyPDF2 import PdfReader, PdfWriter
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your secret key

# Function to merge PDF files
def merge_pdfs(file_names, output_filename):
    writer = PdfWriter()

    for file_name in file_names:
        reader = PdfReader(file_name)
        for page in reader.pages:
            writer.add_page(page)

    with open(output_filename, "wb") as output_pdf:
        writer.write(output_pdf)

# Function to split PDF file
def split_pdf(file_name, start_page, end_page, output_filename):
    reader = PdfReader(file_name)
    writer = PdfWriter()

    for i in range(start_page - 1, end_page):
        writer.add_page(reader.pages[i])

    with open(output_filename, "wb") as output_pdf:
        writer.write(output_pdf)

# Route to handle file upload form
@app.route("/")
def index():
    return render_template("file_upload.html")

# Route to process form submission
@app.route("/process", methods=["POST"])
def process():
    try:
        files = request.files.getlist('files')
        print(len(files))
        operation = request.form['operation']

        if operation == 'split':
            start_page = int(request.form['start'])
            end_page = int(request.form['end'])

            file_name = secure_filename(files[0].filename)
            files[0].save(file_name)

            output_filename = "split_output.pdf"
            split_pdf(file_name, start_page, end_page, output_filename)

            session['output_filename'] = output_filename

            # Clean up: Delete uploaded file after splitting
            os.remove(file_name)

            return render_template("download.html")

        elif operation == 'merge':
            file_names = []
            for file in files:
                file_name = secure_filename(file.filename)
                file.save(file_name)
                file_names.append(file_name)

            output_filename = "merged_output.pdf"
            merge_pdfs(file_names, output_filename)

            session['output_filename'] = output_filename

            # Clean up: Delete uploaded files after merging
            for file_name in file_names:
                os.remove(file_name)

            return render_template("download.html")

        else:
            return "Invalid operation selected."

    except Exception as e:
        return str(e)

# Route to download processed PDF file
@app.route("/download")
def download():
    try:
        output_filename = session.get('output_filename')
        return send_file(output_filename, as_attachment=True)
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(debug=True)
