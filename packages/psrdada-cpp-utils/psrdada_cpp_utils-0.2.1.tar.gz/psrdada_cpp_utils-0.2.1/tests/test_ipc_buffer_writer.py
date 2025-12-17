import unittest
import posix_ipc
import mmap
from psrdada_cpp.ipc_client import IPCBufferClient  # replace with actual import

class TestIPCBufferWriterLinux(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.shm_key = "/test_ipc_buf"
        self.sem_update_key = self.shm_key + "_update"
        self.sem_mutex_key = self.shm_key + "_mutex"
        self.size = 128
        # Ensure no leftovers
        for name in [self.shm_key]:
            try: posix_ipc.unlink_shared_memory(name)
            except: pass
        for name in [self.sem_update_key, self.sem_mutex_key]:
            try: posix_ipc.unlink_semaphore(name)
            except: pass

    async def test_create_and_write_and_close(self):
        writer = IPCBufferClient(self.shm_key)
        writer.create(self.size)
        payload = b"hello"
        writer.write(payload)
        mapfile = mmap.mmap(writer.shm_memory.fd, self.size, mmap.MAP_SHARED, mmap.PROT_READ)
        mapfile.seek(0)
        data = mapfile.read(len(payload))
        self.assertEqual(data, payload)
        mapfile.close()
        writer.close()
        self.assertFalse(writer.connected)
        with self.assertRaises(posix_ipc.ExistentialError):
            posix_ipc.SharedMemory(self.shm_key, flags=0)

    async def test_connect_to_existing(self):
        # First, create it
        creator = IPCBufferClient(self.shm_key)
        creator.create(self.size)
        # Second, connect
        connector = IPCBufferClient(self.shm_key)
        await connector.connect()

        self.assertTrue(connector.connected)
        self.assertFalse(connector._owner)
        self.assertTrue(creator._owner)
        connector.close()
        creator.close()

    async def test_write_too_large(self):
        writer = IPCBufferClient(self.shm_key)
        writer.create(self.size)

        with self.assertRaises(RuntimeError):
            writer.write(b"x" * (self.size + 1))

        writer.close()

    async def test_close_not_connected(self):
        writer = IPCBufferClient(self.shm_key)
        with self.assertRaises(RuntimeError):
            writer.close()
            
    async def test_connect_not_created(self):
        connector = IPCBufferClient(self.shm_key)
        with self.assertRaises(posix_ipc.ExistentialError):
            await connector.connect()
            
if __name__ == '__main__':
    unittest.main()
