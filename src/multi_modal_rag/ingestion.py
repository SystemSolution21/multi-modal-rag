import tkinter as tk
from tkinter import filedialog
import os
from markitdown import MarkItDown

def select_files():
    """Opens a native OS file dialog for the user to select multimodal files."""
    root = tk.Tk()
    root.withdraw() # Hide the main tk window
    
    # Try to open in the multi_modal_rag/documents directory if it exists
    initial_dir = os.path.join(os.getcwd(), 'documents')
    if not os.path.exists(initial_dir):
        initial_dir = os.getcwd()

    file_paths = filedialog.askopenfilenames(
        title="Select Documents and Media",
        initialdir=initial_dir,
        filetypes=[
            ("All Supported Files", "*.docx *.xlsx *.pptx *.pdf *.png *.jpg *.jpeg *.mp3 *.wav *.mp4 *.txt"),
            ("Word Documents", "*.docx"),
            ("Excel Spreadsheets", "*.xlsx"),
            ("PowerPoint Presentations", "*.pptx"),
            ("PDF Documents", "*.pdf"),
            ("Images", "*.png *.jpg *.jpeg"),
            ("Audio", "*.mp3 *.wav"),
            ("Video", "*.mp4"),
            ("Text Files", "*.txt"),
            ("All files", "*.*")
        ]
    )
    return list(file_paths)


def process_files(file_paths):
    """
    Processes the selected files.
    - Uses MarkItDown for Office and PDF files to extract clean Markdown.
    - Returns media files (images, audio, video) as-is for native Processing.
    
    Returns a list of dictionaries containing file metadata and extracted content (if any).
    """
    md = MarkItDown()
    processed_items = []
    
    office_pdf_exts = {'.docx', '.xlsx', '.pptx', '.pdf', '.txt'}
    media_exts = {'.png', '.jpg', '.jpeg', '.mp3', '.wav', '.mp4'}
    
    for path in file_paths:
        ext = os.path.splitext(path)[1].lower()
        
        file_item = {
            "path": path,
            "filename": os.path.basename(path),
            "type": "unknown",
            "content": None
        }
        
        if ext in office_pdf_exts:
            try:
                print(f"Extracting text from {file_item['filename']} via MarkItDown...")
                result = md.convert(path)
                file_item["content"] = result.text_content
                file_item["type"] = "text_document"
            except Exception as e:
                print(f"Error extracting {path}: {e}")
                
        elif ext in media_exts:
            file_item["type"] = "media"
            # We don't extract content for media, the GenAI API will handle the file directly
            
        processed_items.append(file_item)
        
    return processed_items

if __name__ == "__main__":
    print("Please select files...")
    files = select_files()
    print(f"Selected {len(files)} files.")
    
    items = process_files(files)
    for item in items:
        if item["type"] == "text_document":
            preview = item["content"][:100].replace('\n', ' ') if item["content"] else "None"
            print(f"- [Text] {item['filename']}: {preview}...")
        else:
            print(f"- [Media] {item['filename']}")
