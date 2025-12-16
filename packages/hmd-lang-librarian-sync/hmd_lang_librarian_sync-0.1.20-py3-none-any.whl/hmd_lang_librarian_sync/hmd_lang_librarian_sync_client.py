# The code in this file is generated automatically.
# DO NOT EDIT!
from hmd_graphql_client.hmd_base_client import BaseClient
from typing import List
from hmd_schema_loader.hmd_schema_loader import get_default_loader, get_schema_root


from .file import File
from .file_upload import FileUpload



from .file_file import FileFile


from .file_to_upload import FileToUpload

def get_client_loader():
    return get_default_loader("hmd_lang_librarian_sync")

def get_client_schema_root():
    return get_schema_root("hmd_lang_librarian_sync")

class HmdLangLibrarianSyncClient:
    def __init__(self, base_client: BaseClient):
        self._base_client = base_client

    # Generic upsert...
    def upsert(self, entity):
        return self._base_client.upsert_entity(entity)

    # Generic delete...
    def delete(self, entity):
        self._base_client.delete_entity(entity.get_namespace_name(), entity.identifier)

    # Nouns...

    # hmd_lang_librarian_sync_file
    def get_file_hmd_lang_librarian_sync(self, id_: str) -> File:
        return self._base_client.get_entity(File.get_namespace_name(), id_)

    def delete_file_hmd_lang_librarian_sync(self, id_: str) -> None:
        self._base_client.delete_entity(File.get_namespace_name(), id_)

    def upsert_file_hmd_lang_librarian_sync(self, entity: File) -> File:
        if not isinstance(entity, File):
            raise Exception("entity must be an instance of File")
        return self._base_client.upsert_entity(entity)

    
    def search_file_hmd_lang_librarian_sync(self, filter_: dict) -> List[File]:
        return self._base_client.search_entity(File.get_namespace_name(), filter_)

    # hmd_lang_librarian_sync_file_upload
    def get_file_upload_hmd_lang_librarian_sync(self, id_: str) -> FileUpload:
        return self._base_client.get_entity(FileUpload.get_namespace_name(), id_)

    def delete_file_upload_hmd_lang_librarian_sync(self, id_: str) -> None:
        self._base_client.delete_entity(FileUpload.get_namespace_name(), id_)

    def upsert_file_upload_hmd_lang_librarian_sync(self, entity: FileUpload) -> FileUpload:
        if not isinstance(entity, FileUpload):
            raise Exception("entity must be an instance of FileUpload")
        return self._base_client.upsert_entity(entity)

    
    def search_file_upload_hmd_lang_librarian_sync(self, filter_: dict) -> List[FileUpload]:
        return self._base_client.search_entity(FileUpload.get_namespace_name(), filter_)


    # Relationships...

    # hmd_lang_librarian_sync_file_file
    def delete_file_file_hmd_lang_librarian_sync(self, id_: str) -> None:
        self._base_client.delete_entity(FileFile.get_namespace_name(), id_)

    def upsert_file_file_hmd_lang_librarian_sync(self, entity: FileFile) -> FileFile:
        if not isinstance(entity, FileFile):
            raise Exception("entity must be an instance of FileFile")
        return self._base_client.upsert_entity(entity)

    def get_from_file_file_hmd_lang_librarian_sync(self, entity: File) -> List[FileFile]:
        if not isinstance(entity, File):
            raise Exception("entity must be an instance of File")
        return self._base_client.get_relationships_from(entity, FileFile.get_namespace_name())

    def get_to_file_file_hmd_lang_librarian_sync(self, entity: File) -> List[FileFile]:
        if not isinstance(entity, File):
            raise Exception("entity must be an instance of File")
        return self._base_client.get_relationships_to(entity, FileFile.get_namespace_name())



    # hmd_lang_librarian_sync_file_to_upload
    def delete_file_to_upload_hmd_lang_librarian_sync(self, id_: str) -> None:
        self._base_client.delete_entity(FileToUpload.get_namespace_name(), id_)

    def upsert_file_to_upload_hmd_lang_librarian_sync(self, entity: FileToUpload) -> FileToUpload:
        if not isinstance(entity, FileToUpload):
            raise Exception("entity must be an instance of FileToUpload")
        return self._base_client.upsert_entity(entity)

    def get_from_file_to_upload_hmd_lang_librarian_sync(self, entity: File) -> List[FileToUpload]:
        if not isinstance(entity, File):
            raise Exception("entity must be an instance of File")
        return self._base_client.get_relationships_from(entity, FileToUpload.get_namespace_name())

    def get_to_file_to_upload_hmd_lang_librarian_sync(self, entity: FileUpload) -> List[FileToUpload]:
        if not isinstance(entity, FileUpload):
            raise Exception("entity must be an instance of FileUpload")
        return self._base_client.get_relationships_to(entity, FileToUpload.get_namespace_name())


