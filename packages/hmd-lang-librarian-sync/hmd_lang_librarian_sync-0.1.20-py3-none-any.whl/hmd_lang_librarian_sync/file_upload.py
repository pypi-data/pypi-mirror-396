

from hmd_meta_types import Relationship, Noun, Entity

from datetime import datetime
from typing import List, Dict, Any

class FileUpload(Noun):

    _entity_def = \
        {'name': 'file_upload', 'namespace': 'hmd_lang_librarian_sync', 'metatype': 'noun', 'attributes': {'upload_status': {'type': 'enum', 'enum_def': ['pending', 'uploading', 'canceled', 'complete_success', 'complete_failed'], 'description': 'The current status of the file upload'}, 'librarian_put_timestamp': {'type': 'epoch', 'description': 'Timestamp of when the librarian put was called'}, 'librarian_close_timestamp': {'type': 'epoch', 'description': 'Timestamp of when the librarian close was called'}, 'upload_info': {'type': 'mapping', 'description': '(DEPRECATED) Mapping of upload_id to upload_specs for the file'}, 'file_checksum': {'type': 'string', 'description': 'Checksum of the file being uploaded'}, 'file_checksum_algorithm': {'type': 'string', 'description': 'Algorithm used to calculate the checksum of the file being uploaded'}, 'file_size': {'type': 'integer', 'description': 'Size of the file being uploaded'}, 'content_item_path': {'type': 'string', 'description': 'Path to the content item being uploaded'}, 'content_item_id': {'type': 'string', 'description': 'ID of the content item being uploaded'}, 'total_parts': {'type': 'integer', 'description': 'Total number of parts the file is divided into for upload'}, 'uploaded_parts': {'type': 'integer', 'description': 'Number of parts that have been successfully uploaded'}, 'parts_skipped': {'type': 'integer', 'description': 'Number of parts that were skipped during upload'}}}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def entity_definition():
        return FileUpload._entity_def

    @staticmethod
    def get_namespace_name():
        return Entity.get_namespace_name(FileUpload._entity_def)


    

    
        
    @property
    def upload_status(self) -> str:
        return self._getter("upload_status")

    @upload_status.setter
    def upload_status(self, value: str) -> None:
        self._setter("upload_status", value)
    
        
    @property
    def librarian_put_timestamp(self) -> Any:
        return self._getter("librarian_put_timestamp")

    @librarian_put_timestamp.setter
    def librarian_put_timestamp(self, value: Any) -> None:
        self._setter("librarian_put_timestamp", value)
    
        
    @property
    def librarian_close_timestamp(self) -> Any:
        return self._getter("librarian_close_timestamp")

    @librarian_close_timestamp.setter
    def librarian_close_timestamp(self, value: Any) -> None:
        self._setter("librarian_close_timestamp", value)
    
        
    @property
    def upload_info(self) -> Dict:
        return self._getter("upload_info")

    @upload_info.setter
    def upload_info(self, value: Dict) -> None:
        self._setter("upload_info", value)
    
        
    @property
    def file_checksum(self) -> str:
        return self._getter("file_checksum")

    @file_checksum.setter
    def file_checksum(self, value: str) -> None:
        self._setter("file_checksum", value)
    
        
    @property
    def file_checksum_algorithm(self) -> str:
        return self._getter("file_checksum_algorithm")

    @file_checksum_algorithm.setter
    def file_checksum_algorithm(self, value: str) -> None:
        self._setter("file_checksum_algorithm", value)
    
        
    @property
    def file_size(self) -> int:
        return self._getter("file_size")

    @file_size.setter
    def file_size(self, value: int) -> None:
        self._setter("file_size", value)
    
        
    @property
    def content_item_path(self) -> str:
        return self._getter("content_item_path")

    @content_item_path.setter
    def content_item_path(self, value: str) -> None:
        self._setter("content_item_path", value)
    
        
    @property
    def content_item_id(self) -> str:
        return self._getter("content_item_id")

    @content_item_id.setter
    def content_item_id(self, value: str) -> None:
        self._setter("content_item_id", value)
    
        
    @property
    def total_parts(self) -> int:
        return self._getter("total_parts")

    @total_parts.setter
    def total_parts(self, value: int) -> None:
        self._setter("total_parts", value)
    
        
    @property
    def uploaded_parts(self) -> int:
        return self._getter("uploaded_parts")

    @uploaded_parts.setter
    def uploaded_parts(self, value: int) -> None:
        self._setter("uploaded_parts", value)
    
        
    @property
    def parts_skipped(self) -> int:
        return self._getter("parts_skipped")

    @parts_skipped.setter
    def parts_skipped(self, value: int) -> None:
        self._setter("parts_skipped", value)
    

    
        
    def get_to_file_to_upload_hmd_lang_librarian_sync(self):
        return self.to_rels["hmd_lang_librarian_sync.file_to_upload"]
    
    