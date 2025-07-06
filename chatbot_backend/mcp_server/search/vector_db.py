import chromadb
from typing import List, Dict, Optional, Union
import uuid

from search.document import Document

class ChromaManager:
    def __init__(self, collection_name: str = "my_documents", persist_directory: str = "data/vector_db"):
        """
        Initialize ChromaDB client and collection
        
        Args:
            collection_name: Name of the collection to store documents
            persist_directory: Directory to persist the database
        """
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection_name = collection_name
        
        # Create or get collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except:
            self.collection = self.client.create_collection(name=collection_name)
    
    def add_document(self, document: Document) -> str:
        """
        Add a single document to the collection
        
        Args:
            document: Document object to add (uses document.id as the ChromaDB ID)
            
        Returns:
            str: Document ID
        """
        doc_id = str(document.id)
        
        self.collection.add(
            documents=[document.content],
            metadatas=[document.metadata],
            ids=[doc_id]
        )
        
        return doc_id
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """
        Add multiple documents to the collection
        
        Args:
            documents: List of Document objects to add (uses each document.id as ChromaDB ID)
            
        Returns:
            List[str]: List of document IDs
        """
        doc_ids = [str(doc.id) for doc in documents]
        contents = [doc.content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        self.collection.add(
            documents=contents,
            metadatas=metadatas,
            ids=doc_ids
        )
        
        return doc_ids
    
    def get_document(self, doc_id: Union[str, uuid.UUID]) -> Optional[Document]:
        """
        Get a document by ID
        
        Args:
            doc_id: Document ID (can be string or UUID)
            
        Returns:
            Document object or None if not found
        """
        try:
            doc_id_str = str(doc_id)
            result = self.collection.get(ids=[doc_id_str])
            if result['documents']:
                return Document(
                    id=uuid.UUID(doc_id_str),
                    content=result['documents'][0],
                    metadata=result['metadatas'][0]
                )
            return None
        except Exception as e:
            print(f"Error getting document {doc_id}: {e}")
            return None
    
    def get_documents(self, doc_ids: List[Union[str, uuid.UUID]]) -> List[Document]:
        """
        Get multiple documents by IDs
        
        Args:
            doc_ids: List of document IDs (can be strings or UUIDs)
            
        Returns:
            List of Document objects
        """
        try:
            doc_ids_str = [str(doc_id) for doc_id in doc_ids]
            result = self.collection.get(ids=doc_ids_str)
            documents = []
            for i, content in enumerate(result['documents']):
                documents.append(Document(
                    id=uuid.UUID(result['ids'][i]),
                    content=content,
                    metadata=result['metadatas'][i]
                ))
            return documents
        except Exception as e:
            print(f"Error getting documents: {e}")
            return []
    
    def update_document(self, document: Document) -> bool:
        """
        Update a document (uses document.id to identify which document to update)
        
        Args:
            document: Document object with updated content and metadata
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            doc_id = str(document.id)
            self.collection.update(
                ids=[doc_id],
                documents=[document.content],
                metadatas=[document.metadata]
            )
            return True
        except Exception as e:
            print(f"Error updating document {document.id}: {e}")
            return False
    
    def delete_document(self, doc_id: Union[str, uuid.UUID]) -> bool:
        """
        Delete a document by ID
        
        Args:
            doc_id: Document ID to delete (can be string or UUID)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            doc_id_str = str(doc_id)
            self.collection.delete(ids=[doc_id_str])
            return True
        except Exception as e:
            print(f"Error deleting document {doc_id}: {e}")
            return False
    
    def delete_documents(self, doc_ids: List[Union[str, uuid.UUID]]) -> bool:
        """
        Delete multiple documents by IDs
        
        Args:
            doc_ids: List of document IDs to delete (can be strings or UUIDs)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            doc_ids_str = [str(doc_id) for doc_id in doc_ids]
            self.collection.delete(ids=doc_ids_str)
            return True
        except Exception as e:
            print(f"Error deleting documents: {e}")
            return False
    
    def search_relative_documents(self, query: str, n_results: int = 10, filenames: list = []) -> List[str]:
        """
        Search for documents similar to the query
        
        Args:
            query: Search query string
            n_results: Number of results to return
            filenames: Optional list of filenames to filter results
            
        Returns:
            List of dictionaries containing document info and similarity scores
        """
        try:

            where = {}
            if filenames:
                where['filename'] = {'$in': filenames}
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
            
            search_results = []
            for i, doc_id in enumerate(results['ids'][0]):
                # Check if the distance is within the threshold (1.2)
                if results['distances'][0][i] <= 1.2:
                    search_results.append({
                        'id': doc_id,
                        'document': Document(
                            id=uuid.UUID(doc_id),
                            content=results['documents'][0][i],
                            metadata=results['metadatas'][0][i]
                        ),
                        'distance': results['distances'][0][i]
                    })
            
            # Just for debugging, you can uncomment the following lines to print results
            # for result in search_results:
            #     print(f"Document ID: {result['id']}, Content: {result['document']}..., Distance: {result['distance']:.4f}")

            list_filenames = [doc['document'].metadata.get('filename', '') for doc in search_results]
            list_filenames = list(dict.fromkeys(f for f in list_filenames if f.strip())) # Remove duplicates and empty strings
            return list_filenames
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []

    def get_all_documents(self) -> List[Dict]:
        """
        Get all documents in the collection
        
        Returns:
            List of dictionaries with document IDs and Document objects
        """
        try:
            result = self.collection.get()
            documents = []
            for i, doc_id in enumerate(result['ids']):
                documents.append({
                    'id': doc_id,
                    'document': Document(
                        id=uuid.UUID(doc_id),
                        content=result['documents'][i],
                        metadata=result['metadatas'][i]
                    )
                })
            return documents
        except Exception as e:
            print(f"Error getting all documents: {e}")
            return []
    
    def filter_documents(self, filenames: list = []) -> List[Dict]:
        """
        Filter documents by metadata
        
        Args:
            where: Metadata filter conditions
            
        Returns:
            List of dictionaries with filtered documents
        """
        try:
            where = {}
            if filenames:
                where['filename'] = {'$in': filenames}
            result = self.collection.get(where=where)
            documents = []
            for i, doc_id in enumerate(result['ids']):
                documents.append({
                    'id': doc_id,
                    'document': Document(
                        id=uuid.UUID(doc_id),
                        content=result['documents'][i],
                        metadata=result['metadatas'][i]
                    )
                })
            return documents
        except Exception as e:
            print(f"Error filtering documents: {e}")
            return []
    
    def clear_collection(self) -> bool:
        """
        Clear all documents from the collection
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get all document IDs and delete them
            all_docs = self.collection.get()
            if all_docs['ids']:
                self.collection.delete(ids=all_docs['ids'])
            return True
        except Exception as e:
            print(f"Error clearing collection: {e}")
            return False 