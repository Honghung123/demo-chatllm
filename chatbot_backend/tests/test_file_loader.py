# Unit test cho file_loader và file_parser

import os
import sys
import pytest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.files import file_loader, file_pre_processing

DATA_DIR = "data/documents"

def get_sample_path(fileName):
    # Đảm bảo có file mẫu phù hợp trong thư mục test 
    fpath = os.path.join(DATA_DIR, fileName)
    if not os.path.exists(fpath):
        pytest.skip(f"File {fileName} không tồn tại, bỏ qua test.")
    return fpath

def test_load_pdf():
    fpath = get_sample_path("git-cheat-sheet.pdf")
    content = file_loader.load_pdf(fpath)
    assert content is not None and len(content) > 0

def test_load_docx():
    fpath = get_sample_path("History of Java.docx")
    content = file_loader.load_docx(fpath)
    assert content is not None and len(content) > 0

def test_load_pptx():
    fpath = get_sample_path("oops-java.pptx")
    content = file_loader.load_pptx(fpath)
    assert content is not None and len(content) > 0

def test_chunk_text():
    text = "A" * 1000
    chunks = file_pre_processing.chunk_text(text, chunk_size=200, overlap=50)
    # Số chunk phải lớn hơn 1, các chunk không rỗng, overlap đúng
    assert len(chunks) > 1
    assert all(len(chunk) > 0 for chunk in chunks)
    # Kiểm tra overlap
    if len(chunks) > 1:
        assert chunks[0][-50:] == chunks[1][:50]

if __name__ == "__main__":
    
    pytest.main(sys.argv)