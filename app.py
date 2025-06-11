from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz
import pptx
from io import BytesIO
from transformers import pipeline
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-domain access

# Load summarizer model once
summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "".join(page.get_text() for page in doc)

def extract_text_from_ppt(file):
    prs = pptx.Presentation(BytesIO(file.read()))
    text = ""
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text + " "
    return text

def summarize_text_locally(text):
    chunks = [ text[i:i+512] for i in range(0, len(text), 512) ]
    summaries = []
    for chunk in chunks:
        task = "summarize: " + chunk.strip().replace("\n", " ")
        result = summarizer(task, max_length=100, min_length=30, do_sample=False)
        summaries.append(result[0]['summary_text'])
    return "\n".join(summaries)

@app.route('/summarize', methods=['POST'])
def summarize():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    name = file.filename.lower()
    if not (name.endswith('.pdf') or name.endswith('.ppt') or name.endswith('.pptx')):
        return jsonify({'error': 'Unsupported file type'}), 400

    try:
        text = extract_text_from_pdf(file) if name.endswith('.pdf') else extract_text_from_ppt(file)
        summary = summarize_text_locally(text)
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
