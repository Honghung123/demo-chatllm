import uuid


"""
    Document class to represent a chunk of text
    with associated metadata : {filename: "file1.pdf"}
"""
class Document:
    def __init__(self, id:uuid, content:str, metadata:dict):
        self.id = id 
        self.content = content
        self.metadata = metadata

    def __repr__(self):
        return f"Document(id={self.id}, content={self.content[:30]}..., metadata={self.metadata})"