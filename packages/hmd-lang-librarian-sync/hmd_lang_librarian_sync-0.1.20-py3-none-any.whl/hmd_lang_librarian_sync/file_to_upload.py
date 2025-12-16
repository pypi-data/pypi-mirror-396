

from hmd_meta_types import Relationship, Noun, Entity
from hmd_lang_librarian_sync.file import File
from hmd_lang_librarian_sync.file_upload import FileUpload
from datetime import datetime
from typing import List, Dict, Any

class FileToUpload(Relationship):

    _entity_def = \
        {'name': 'file_to_upload', 'namespace': 'hmd_lang_librarian_sync', 'metatype': 'relationship', 'ref_from': 'hmd_lang_librarian_sync.file', 'ref_to': 'hmd_lang_librarian_sync.file_upload', 'attributes': {}}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def entity_definition():
        return FileToUpload._entity_def

    @staticmethod
    def get_namespace_name():
        return Entity.get_namespace_name(FileToUpload._entity_def)


    @staticmethod
    def ref_from_type():
        return File

    @staticmethod
    def ref_to_type():
        return FileUpload

    

    