from datetime import datetime
import uuid
from common.file.file_loader import load_file
from common.file.file_metadata_manager import add_metadata, get_list_file_names_by_user_and_role, load_metadata, update_metadata, get_list_personal_files, get_list_system_files
from common.file.file_pre_processing import preprocess_text
from common.search.document import Document
from common.search.vector_db import chroma_db

# add_metadata(
#     file_name="Monthly Sales Report.pdf", 
#     extension="pdf", 
#     original_name="Monthly Sales Report.pdf", 
#     username="admin",
#     timestamp=datetime.now().isoformat(),
#     roles=["sales", "admin"]
# )

# print("Total documents in ChromaDB:", len(chroma_db.get_all_documents()))
# chroma_db.clear_collection()

# content = load_file(f'Marketing Campaign Plan.pdf')
# chunks = preprocess_text(content)
# print(f"number of chunks: {len(chunks)}")
# docs = []
# for i, chunk in enumerate(chunks):
#     doc = Document(
#         id=uuid.uuid4(),
#         content=chunk,
#         metadata={
#             "filename": "Marketing Campaign Plan.pdf",
#         }
#     )
#     docs.append(doc)
# doc_ids = chroma_db.add_documents(docs)

# list_files = get_list_file_names_by_user_and_role("admin", "admin")
# print(f"List of files': {list_files}")
# file_names = chroma_db.search_relative_documents(query="digital marketing", n_results=10, filenames=list_files)
# print(f"Search results: {file_names}")
