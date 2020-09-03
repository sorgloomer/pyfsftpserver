import datetime
import logging
import mimetypes
import os
from typing import Optional, List

from fs import errors
from fs.info import Info
from fs.mode import Mode
from fs.path import dirname
from fs_gcsfs import GCSFS
from fs_gcsfs._gcsfs import GCSFile
from google.cloud.storage import Blob

logger = logging.getLogger(__name__)


DIR_BLOB_IMPOSTOR = object()


class PatchedGCSFS(GCSFS):
    def _is_dir_key(self, key: str):
        """ guesses if key was made by _path_to_dir_key """
        return key.endswith(self.DELIMITER)

    def _blobs_with_prefix_exist(self, prefix):
        """ finds a blob with a given prefix and returns a bool """
        response = self.bucket.list_blobs(prefix=prefix, delimiter=self.DELIMITER)
        for _ in response:
            return True
        return False

    def _is_pseudo_dir(self, key):
        """ returns if the key is a dir key, an """
        return self._is_dir_key(key) and self._blobs_with_prefix_exist(key)

    def _get_blob(self, key: str) -> Optional[Blob]:
        print(datetime.datetime.now(), "_get_blob", key)
        result = super()._get_blob(key)
        if not result and self._is_pseudo_dir(key):
            # Hack so that other parts of GCSFS get a truthy value. It works because GCSFS only checks if the returned
            # Optional[Blob] is None or not in case of directories
            # Well, there is one place where it doesn't use GCSFS._get_blob, in openbin, when checking the parent dir
            # it uses GCSFS.bucket.get_blob which bypasses our ugly hack here. So we have to override openbin too
            return DIR_BLOB_IMPOSTOR
        return result

    def getinfo(self, path: str, namespaces: Optional[List[str]] = None, check_parent_dir: bool = None) -> Info:
        if check_parent_dir is None:
            check_parent_dir = False
        return super().getinfo(path=path, namespaces=namespaces, check_parent_dir=check_parent_dir)

    def openbin(self, path: str, mode: str = "r", buffering: int = -1, **options) -> "GCSFile":
        # Have to override openbin because it checks if the parent dir exists using self.bucket.get_blob directly
        _mode = Mode(mode)
        _mode.validate_bin()
        self.check()
        _path = self.validatepath(path)
        _key = self._path_to_key(_path)

        def on_close(gcs_file):
            if _mode.create or _mode.writing:
                gcs_file.raw.seek(0)
                blob = self._get_blob(_key)
                if not blob:
                    blob = self.bucket.blob(_key)
                mime_type, encoding = mimetypes.guess_type(path)
                if encoding is not None:
                    mime_type = None
                blob.upload_from_file(gcs_file.raw, content_type=mime_type)
            gcs_file.raw.close()

        if _mode.create:
            try:
                info = self.getinfo(path)
            except errors.ResourceNotFound:
                pass
            else:
                if _mode.exclusive:
                    raise errors.FileExists(path)
                if info.is_dir:
                    raise errors.FileExpected(path)

            gcs_file = GCSFile.factory(path, _mode, on_close=on_close)

            if _mode.appending:
                blob = self._get_blob(_key)
                if blob:  # in case there is an existing blob in GCS, we download it and seek until the end of the stream
                    gcs_file.seek(0, os.SEEK_END)
                    blob.download_to_file(gcs_file.raw)

            return gcs_file

        if self.strict:
            info = self.getinfo(path)
            if info.is_dir:
                raise errors.FileExpected(path)

        gcs_file = GCSFile.factory(path, _mode, on_close=on_close)
        blob = self._get_blob(_key)
        if not blob:
            raise errors.ResourceNotFound(path)

        blob.download_to_file(gcs_file.raw)
        gcs_file.seek(0)
        return gcs_file
