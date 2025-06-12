from django.shortcuts import render
from .utils import extract_text_from_pdf, extract_text_from_ppt, summarize_text

def upload_and_summarize(request):
    summary = ""
    if request.method == "POST" and request.FILES.get("document"):
        uploaded_file = request.FILES["document"]
        file_type = uploaded_file.name.lower()

        if file_type.endswith(".pdf"):
            text = extract_text_from_pdf(uploaded_file)
        elif file_type.endswith(".ppt") or file_type.endswith(".pptx"):
            text = extract_text_from_ppt(uploaded_file)
        else:
            summary = "Unsupported file format. Please upload PDF or PPT only."
            return render(request, "summarizer/upload.html", {"summary": summary})

        summary = summarize_text(text)

    return render(request, "summarizer/upload.html", {"summary": summary})
