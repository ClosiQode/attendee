import logging
import shutil
import threading
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LocalFileUploader:
    def __init__(self, destination_dir, filename):
        self.destination_dir = Path(destination_dir)
        self.filename = filename
        self._upload_thread = None

    def upload_file(self, file_path: str, callback=None):
        self._upload_thread = threading.Thread(target=self._upload_worker, args=(file_path, callback), daemon=True)
        self._upload_thread.start()

    def _upload_worker(self, file_path: str, callback=None):
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            self.destination_dir.mkdir(parents=True, exist_ok=True)
            destination = self.destination_dir / self.filename
            shutil.copy2(str(file_path), str(destination))

            logger.info(f"Successfully copied {file_path} to {destination}")

            if callback:
                callback(True)

        except Exception as e:
            logger.error(f"Upload error: {e}")
            if callback:
                callback(False)

    def wait_for_upload(self):
        if self._upload_thread and self._upload_thread.is_alive():
            self._upload_thread.join()

    def delete_file(self, file_path: str):
        file_path = Path(file_path)
        if file_path.exists():
            file_path.unlink()
