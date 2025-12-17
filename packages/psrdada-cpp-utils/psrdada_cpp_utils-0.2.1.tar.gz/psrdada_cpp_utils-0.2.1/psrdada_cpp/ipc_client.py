import asyncio
import posix_ipc
import mmap
import time
import contextlib
import logging
import functools

_LOG = logging.getLogger("psrdada_cpp.ipc_buffer_writer")
class IPCBufferClient:
    """A partially async client interface for IPC buffers. 
        It can connect, create, read and write from POSIX IPC buffers 
    """
    def __init__(self, shm_key: str):
        """Construct and IPCBufferClient instance

        Args:
            shm_key (str): The key to identify the IPC buffer
        """
        self._shm_key = shm_key
        self._sem_update_key = shm_key + "_update"
        self._sem_mutex_key = shm_key + "_mutex"
        self.mapfile: mmap.mmap | None = None
        self.connected = False
        self._owner: bool = False
        self._size = 0
        self.shm_memory: posix_ipc.SharedMemory | None = None
        self.sem_update: posix_ipc.Semaphore | None = None
        self.sem_mutex: posix_ipc.Semaphore | None = None
        self._last_update_count: int = 0

    def has_update(self):
        if self.sem_update is None:
            return False  
        val = self.sem_update.value 
        if self._last_update_count == val:
            return False
        else:
            self._last_update_count = val
            return True

    def create(self, size: int):
        """Creates a POSIX IPC buffer with an update and mutex semaphore

        Args:
            size (int): The size of the shared memory buffer in bytes
        """
        self._size = size
        flags = posix_ipc.O_CREAT | posix_ipc.O_EXCL
        self.shm_memory = posix_ipc.SharedMemory(self._shm_key, flags=flags, size=size)
        self.sem_update = posix_ipc.Semaphore(self._sem_update_key, flags=flags, initial_value=0)
        self.sem_mutex = posix_ipc.Semaphore(self._sem_mutex_key, flags=flags, initial_value=1)
        self.mapfile = mmap.mmap(self.shm_memory.fd, self.shm_memory.size, mmap.MAP_SHARED, mmap.PROT_WRITE)
        self.connected = True
        self._owner = True
        self._last_update_count = self.sem_update.value
        _LOG.info("Created IPC buffer '%s'", self._shm_key)

                    
    async def connect(self, retries: int = 5, delay: float = 0.5):
        """Try to connect to existing shared memory and semaphores.
        
        Args:
            retries: how many attempts before giving up
            delay: seconds to wait between attempts
        """
        if self.connected:
            raise RuntimeError("IPCBufferClient already connected")
        for attempt in range(1, retries + 1):
            try:
                self._connect_once()
                self.connected = True
                _LOG.info("Connected to IPC buffer '%s'", self._shm_key)
                return
            except posix_ipc.ExistentialError as e:
                if attempt == retries:
                    _LOG.error("Failed to open IPC buffer %s: %s (no retries left)", self._shm_key, e)
                    raise
                else:
                    _LOG.warning(
                        "Failed to open IPC buffer %s: %s (retry %d/%d)",
                        self._shm_key, e, attempt, retries)
                    await asyncio.sleep(delay)
        

    def _connect_once(self):
        """Try a single connection attempt, raise if fails."""
        with contextlib.ExitStack() as stack:
            shm = posix_ipc.SharedMemory(self._shm_key, flags=0)
            stack.callback(shm.close_fd)

            sem_update = posix_ipc.Semaphore(self._sem_update_key, flags=0)
            stack.callback(sem_update.close)

            sem_mutex = posix_ipc.Semaphore(self._sem_mutex_key, flags=0)
            stack.callback(sem_mutex.close)

            mapfile = mmap.mmap(
                shm.fd, shm.size, mmap.MAP_SHARED, mmap.PROT_WRITE
            )
            stack.callback(mapfile.close)
            # success → preserve resources
            self.shm_memory = shm
            self.sem_update = sem_update
            self._last_update_count = self.sem_update.value
            self.sem_mutex = sem_mutex
            self.mapfile = mapfile
            stack.pop_all()


    def write(self, data: bytes):
        if not self.connected:
            raise RuntimeError("IPCBufferClient not connected")

        self.sem_mutex.acquire()
        try:
            if len(data) > self.shm_memory.size:
                raise RuntimeError(
                    f"Data too large for buffer (need {len(data)}, have {self.shm_memory.size})")
            self.mapfile.seek(0)
            self.mapfile.write(data)
            self.mapfile.flush()
        finally:
            self.sem_mutex.release()
            self.sem_update.release()
    
    def read(self, timeout=5) -> bytes:
        """
        Block until data is available, then return a copy of the bytes
        stored in the shared memory buffer.
        """
        if not self.connected:
            raise RuntimeError("IPCBufferClient not connected")

        start = time.time()
        while time.time() < start + timeout:
            if self.has_update():
                break
        else:
            raise TimeoutError("Timeout while waiting for buffer update")

        # Protect the critical section
        self.sem_mutex.acquire()
        try:
            self.mapfile.seek(0)
            data = self.mapfile.read(self.shm_memory.size)
            return data
        finally:
            self.sem_mutex.release()
    
    async def read_async(self, timeout=5) -> bytes:
        """Non-blocking async read
        
        Returns:
            bytes: the read data
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, functools.partial(self.read, timeout=timeout))

    def close(self):
        """Close the connection to the IPC buffer

        Raises:
            RuntimeError: If the client was not connected
        """
        if not self.connected:
            raise RuntimeError("Tried to close IPCBufferClient which is not connected")
        _LOG.info("Closing IPC buffer '%s'", self._shm_key)
        self.mapfile.close()
        self.sem_update.close()
        self.sem_mutex.close()
        self.shm_memory.close_fd()
        if self._owner:  # only close the shm if we created it
            posix_ipc.unlink_shared_memory(self._shm_key)
            posix_ipc.unlink_semaphore(self._sem_update_key)
            posix_ipc.unlink_semaphore(self._sem_mutex_key)
        self._owner = False
        self.connected = False


async def connect_ipc_client(key: str, initial_data: bytes = b"") -> IPCBufferClient:
    """Connect an POSIX IPC buffer


    Args:
        key (str): The IPC buffer key
        initial_data (bytes): The initial data to write to the buffer

    Returns:
        IPCBufferClient: The connected IPC buffer instance
    """
    ipc_client = IPCBufferClient(key)
    await ipc_client.connect()
    if initial_data:
        ipc_client.write(initial_data)
    return ipc_client
