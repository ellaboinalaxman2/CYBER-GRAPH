from typing import Optional, List, Dict, Any, TypeVar, Generic
from datetime import datetime
from pymongo.collection import Collection
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from ..config.connection import mongodb_connection

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations"""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self._collection: Optional[Collection] = None
    
    @property
    def collection(self) -> Collection:
        """Get collection, connect if not connected"""
        if self._collection is None:
            self._collection = mongodb_connection.get_collection(self.collection_name)
        return self._collection
    
    def create(self, document: Dict[str, Any]) -> InsertOneResult:
        """Create a new document"""
        return self.collection.insert_one(document)
    
    def create_many(self, documents: List[Dict[str, Any]]) -> Any:
        """Create multiple documents"""
        return self.collection.insert_many(documents)
    
    def find_by_id(self, document_id: str, id_field: str = "_id") -> Optional[Dict[str, Any]]:
        """Find document by ID"""
        return self.collection.find_one({id_field: document_id})
    
    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find one document matching query"""
        return self.collection.find_one(query)
    
    def find(self, query: Dict[str, Any], limit: Optional[int] = None, 
             skip: Optional[int] = None, sort: Optional[List[tuple]] = None) -> List[Dict[str, Any]]:
        """Find documents matching query"""
        cursor = self.collection.find(query)
        
        if sort:
            cursor = cursor.sort(sort)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
            
        return list(cursor)
    
    def update_by_id(self, document_id: str, update_data: Dict[str, Any], 
                     id_field: str = "_id") -> UpdateResult:
        """Update document by ID"""
        # Add updated_at timestamp
        update_data['updated_at'] = datetime.utcnow()
        return self.collection.update_one(
            {id_field: document_id},
            {'$set': update_data}
        )
    
    def update_many(self, query: Dict[str, Any], update_data: Dict[str, Any]) -> UpdateResult:
        """Update multiple documents"""
        update_data['updated_at'] = datetime.utcnow()
        return self.collection.update_many(
            query,
            {'$set': update_data}
        )
    
    def delete_by_id(self, document_id: str, id_field: str = "_id") -> DeleteResult:
        """Delete document by ID"""
        return self.collection.delete_one({id_field: document_id})
    
    def delete_many(self, query: Dict[str, Any]) -> DeleteResult:
        """Delete multiple documents"""
        return self.collection.delete_many(query)
    
    def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """Count documents matching query"""
        return self.collection.count_documents(query or {})
    
    def exists(self, query: Dict[str, Any]) -> bool:
        """Check if document exists"""
        return self.collection.find_one(query) is not None
    
    def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run aggregation pipeline"""
        return list(self.collection.aggregate(pipeline))
    
    def distinct(self, field: str, query: Optional[Dict[str, Any]] = None) -> List[Any]:
        """Get distinct values for a field"""
        return self.collection.distinct(field, query or {})