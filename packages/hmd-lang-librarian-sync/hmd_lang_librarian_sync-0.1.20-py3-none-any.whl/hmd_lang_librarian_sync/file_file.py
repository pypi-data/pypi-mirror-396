

from hmd_meta_types import Relationship, Noun, Entity
from hmd_lang_librarian_sync.file import File
from hmd_lang_librarian_sync.file import File
from datetime import datetime
from typing import List, Dict, Any

class FileFile(Relationship):

    _entity_def = \
        {'name': 'file_file', 'namespace': 'hmd_lang_librarian_sync', 'metatype': 'relationship', 'ref_from': 'hmd_lang_librarian_sync.file', 'ref_to': 'hmd_lang_librarian_sync.file', 'attributes': {'source_name': {'type': 'string', 'description': 'The name of the configured source the file_file is attached to'}}}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def entity_definition():
        return FileFile._entity_def

    @staticmethod
    def get_namespace_name():
        return Entity.get_namespace_name(FileFile._entity_def)


    @staticmethod
    def ref_from_type():
        return File

    @staticmethod
    def ref_to_type():
        return File

    
        
    @property
    def source_name(self) -> str:
        return self._getter("source_name")

    @source_name.setter
    def source_name(self, value: str) -> None:
        self._setter("source_name", value)
    

    