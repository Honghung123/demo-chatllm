import uuid
from app.files.file_loader import load_file
from app.files.file_metadata_manager import add_metadata, get_list_file_names_by_user_and_role, load_metadata, update_metadata
from app.files.file_pre_processing import preprocess_text
from app.search.document import Document
from app.search.vector_db import ChromaManager

DATA_DIR = "data/documents"
METADATA_FILE_PATH = "data/metadata/file_metadata.json"
# content = load_file(f'{DATA_DIR}/python.pdf')
# chunks = preprocess_text(content)
# print(f"Content of 'python.pdf':\n")
# for i, chunk in enumerate(chunks):
#     print(f"Chunk {i+1}:\n{chunk}\n")

# add_metadata(
#     file_name="python.pdf", author="admin", roles=["developer", "data scientist"])

# update_metadata(
#     file_name="python.pdf",
#     author="user1",
#     roles=["developer", "data scientist"]
# )

# print(f'list files for user1 and role sales {get_list_file_names_by_user_and_role("admin", "admin")}')

chroma_db = ChromaManager(collection_name="my_documents", persist_directory="data/vector_store")
print("Total documents in ChromaDB:", len(chroma_db.get_all_documents()))

# # add python.pdf to ChromaDB
# content = load_file(f'{DATA_DIR}/python.pdf')
# add_metadata(file_name="python.pdf", author="admin", roles=["admin", "hr", "sales"])
# chunks = preprocess_text(content)
# docs = []
# for i, chunk in enumerate(chunks):
#     doc = Document(
#         id=uuid.uuid4(),
#         content=chunk,
#         metadata={
#             "filename": "python.pdf",
#         }
#     )
#     docs.append(doc)
# doc_ids = chroma_db.add_documents(docs)
# print(f"Added {len(doc_ids)} documents to ChromaDB.")

# # add History of Java.docx to ChromaDB
# content = load_file(f'{DATA_DIR}/History of Java.docx')
# add_metadata(file_name="History of Java.docx", author="admin", roles=["admin", "tech", "marketing"])
# chunks = preprocess_text(content)
# docs = []
# for i, chunk in enumerate(chunks):
#     doc = Document(
#         id=uuid.uuid4(),
#         content=chunk,
#         metadata={
#             "filename": "History of Java.docx",
#         }
#     )
#     docs.append(doc)
# doc_ids = chroma_db.add_documents(docs)


list_files = get_list_file_names_by_user_and_role("admin", "admin")
print(f"List of files for user1 and role hr: {list_files}")
docs = chroma_db.search_relative_documents(query="learning java programming", n_results=10, filenames=list_files)
print(f"Search results for 'learning java programming': {docs}")

