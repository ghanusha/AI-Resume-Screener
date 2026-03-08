import PyPDF2
import docx2txt
import os

def extract_text(file_path):
    """
    Extracts text from a given PDF or DOCX file.
    """
    if not os.path.exists(file_path):
        return ""

    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()
    
    text = ""

    try:
        if file_extension == ".pdf":
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        elif file_extension == ".docx":
            text = docx2txt.process(file_path)
        else:
            return "" # Unsupported format
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return ""
        
    return text
