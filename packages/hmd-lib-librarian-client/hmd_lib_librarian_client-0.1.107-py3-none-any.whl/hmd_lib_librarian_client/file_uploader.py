import os
import sys
import traceback
from queue import Queue
from threading import Thread, Event
from time import sleep
from typing import Callable, Any, Dict, List

from requests import put


class UploadFailedException(Exception):
    def __init__(self, formatted_exception: str):
        self._formatted_exception = formatted_exception

    def __str__(self):
        return self._formatted_exception


class ByteUploader:
    def __init__(
        self,
        file_descriptor: int,
        upload_url: str,
        part_size: int,
        part_number: int,
        starting_position: int,
        change_event: Event,
        mime_type: str = None,
        number_of_tries: int = 3,
        seconds_between_retries: int = 30,
        checksum: Dict = None,
        skipped: bool = False,
        etag: str = None,
    ):
        self._number_of_tries = number_of_tries
        self._upload_url = upload_url
        self._file_descriptor = file_descriptor
        self._number_of_bytes = part_size
        self._part_number = part_number
        self._starting_position = starting_position
        self._mime_type = mime_type
        self._change_event = change_event
        self._seconds_between_retries = seconds_between_retries
        self._checksum = checksum
        self._skipped = skipped
        self._etag = etag

        self._last_exception = None
        self._number_of_bytes_left = self._number_of_bytes
        self._has_failed = False
        self._stop_thread = False
        self._tries_so_far = 0

    @property
    def has_failed(self):
        return self._has_failed

    @property
    def etag(self):
        return self._etag

    @property
    def part_number(self):
        return self._part_number

    @property
    def last_exception(self):
        return self._last_exception

    def get_status(self):
        return {
            "part_number": self._part_number,
            "bytes_uploaded": self._number_of_bytes - self._number_of_bytes_left,
            "bytes_total": self._number_of_bytes,
            "etag": self._etag,
            "tries": self._tries_so_far,
            "skipped": self._skipped,
        }

    def stop_thread(self):
        self._stop_thread = True

    def start_upload(self):
        if self._skipped:
            self._number_of_bytes_left = 0
            self._change_event.set()
            return
        while self._tries_so_far < self._number_of_tries and not self._stop_thread:
            self._tries_so_far += 1

            self._number_of_bytes_left = self._number_of_bytes
            try:
                # Use os.pread() for thread-safe, position-independent read
                # This works on Linux, Mac, and Windows (Python 3.5+)
                data = os.pread(
                    self._file_descriptor,
                    self._number_of_bytes,
                    self._starting_position,
                )

                put_args = {
                    "url": self._upload_url,
                    "data": data,
                    "timeout": 30,
                }
                if self._mime_type:
                    put_args["headers"] = {"Content-Type": self._mime_type}
                if "headers" in put_args and self._checksum:
                    put_args["headers"].update(
                        {
                            f'x-amz-checksum-{self._checksum["algorithm"].lower()}': str(
                                self._checksum["value"]
                            ),
                            "x-amz-sdk-checksum-algorithm": self._checksum["algorithm"],
                        }
                    )
                response = put(**put_args)
                response.raise_for_status()
                self._number_of_bytes_left = 0
                self._etag = response.headers["ETag"]
                self._change_event.set()
                break
            except Exception as ex:
                print(str(ex))
                traceback.print_exc(file=sys.stdout)
                self._change_event.set()

                self._last_exception = ex
                if self._tries_so_far < self._number_of_tries:
                    # Sleep in small intervals to allow quick cancellation
                    for _ in range(self._seconds_between_retries):
                        if self._stop_thread:
                            break
                        sleep(1)

        if self._tries_so_far >= self._number_of_tries:
            self._has_failed = True
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self._change_event.set()


class ByteUploaderThread(Thread):
    def __init__(self, a_queue: Queue):
        super().__init__(daemon=True)
        self.a_queue = a_queue

    def run(self):
        while not self.a_queue.empty():
            uploader = self.a_queue.get()
            try:
                uploader.start_upload()
            except UploadFailedException as ex:
                pass
            self.a_queue.task_done()


def upload(
    filename: str,
    upload_specs: List[Dict[str, Any]],
    number_of_threads: int = 2,
    status_callback: Callable = None,
    number_of_tries: int = 3,
    seconds_between_retries: int = 30,
    checksum: Dict = None,
):
    queue = Queue()
    uploaders = []
    starting_position = 0
    change_event = Event()

    # Open file and get file descriptor for thread-safe parallel reads
    fd = os.open(filename, os.O_RDONLY)
    try:
        for data in upload_specs:
            uploader = ByteUploader(
                file_descriptor=fd,
                upload_url=data["upload_url"],
                part_size=data["part_size"],
                part_number=data["part_number"],
                starting_position=starting_position,
                mime_type=data["mime_type"] if len(upload_specs) == 1 else None,
                number_of_tries=number_of_tries,
                change_event=change_event,
                seconds_between_retries=seconds_between_retries,
                checksum=checksum,
                skipped=data.get("uploaded", False),
                etag=data.get("etag"),
            )
            queue.put(uploader)
            uploaders.append(uploader)
            starting_position += data["part_size"]
        threads = []
        for _ in range(min(number_of_threads, queue.qsize())):
            thread = ByteUploaderThread(queue)
            thread.start()
            threads.append(thread)

        def _prep_callback():
            parts = [up.get_status() for up in uploaders]
            data = {
                "total_parts": len(parts),
                "skipped_parts": sum(1 for part in parts if part["skipped"]),
                "parts_complete": sum(
                    1 for part in parts if part["bytes_uploaded"] == part["bytes_total"]
                ),
                "total_bytes": sum(part["bytes_total"] for part in parts),
                "bytes_complete": sum(part["bytes_uploaded"] for part in parts),
                "parts": parts,
            }
            data["parts_percent"] = float(data["parts_complete"]) / data["total_parts"]
            data["bytes_percent"] = float(data["bytes_complete"]) / data["total_bytes"]

            return data

        if status_callback:
            status_callback(_prep_callback())
        while any(t.is_alive() for t in threads):
            change_event.wait()
            change_event.clear()
            if any(ul.has_failed for ul in uploaders):
                for ul in uploaders:
                    ul.stop_thread()
                break
            if status_callback:
                status_callback(_prep_callback())
            # seems to get
            sleep(5)

        if status_callback:
            status_callback(_prep_callback())
        for ul in [ul for ul in uploaders if ul.has_failed]:
            raise ul.last_exception

        return [ul.get_status() for ul in uploaders]
    finally:
        # Always close the file descriptor
        os.close(fd)
