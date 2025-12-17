import numpy as np
import struct
import logging
import asyncio
from typing import Dict

from .ipc_client import IPCBufferClient
from .mq_client import MQClient
from .type_conversion import to_numpy_dtype
_LOG = logging.getLogger("psrdada_cpp.ipc_buffer_writer")
MONITOR_HEADER = struct.Struct("<I I I f")
MAGIC = 0x51A0CBB8


class MonitorEndpoint:
    """
    Represents a single monitoring endpoint that communicates through an
    MQClient and a IPCBufferClient. Provides helper methods for metadata queries, 
    enabling or disabling monitoring, triggering data acquisition, and reading arrays
    from an IPC buffer.
    """
    def __init__(self, name: str, client: MQClient):
        """
        Initialize a monitoring endpoint with its name and MQ client.

        Args:
            name (str): The monitor name as defined by the backend.
            client (MQClient): MQ client used to send requests to the backend.
        """
        self._name = name
        self._mq_client = client
        self._ipc_client = None
        self.initialized = False

    def check_response(self, resp: dict):
        """
        Validate an MQ response object. Logs an error on failure.

        Args:
            resp (dict): The response dictionary returned by the MQ backend.

        Returns:
            Any | None: The response payload on success; otherwise None.
        """
        if resp["status"] == "success":
            return resp["response"]
        _LOG.error("'%s'-request to monitoring endpoint '%s' failed; %s", 
                   resp["command"], self._name, resp["message"])
        return None
        
    async def request_metadata(self):
        """
        Request metadata for this monitor endpoint.

        Returns:
            dict | None: The metadata dictionary if successful; otherwise None.
        """
        resp = await self._mq_client.send("monitor_metadata", name=self._name)
        return self.check_response(resp)

    async def request_enable(self):
        """Enable the monitor on the backend.

        Returns:
            Any | None: Backend response payload if successful; otherwise None.
        """
        resp = await self._mq_client.send("monitor_enable", name=self._name,
                                          enable=True)
        return self.check_response(resp)
    
    async def request_disable(self):
        """Disable the monitor on the backend.

        Returns:
            Any | None: Backend response payload if successful; otherwise None.
        """
        resp = await self._mq_client.send("monitor_enable", name=self._name, 
                                          enable=False)
        return self.check_response(resp)

    async def request_trigger(self):
        """Trigger data acquisition and read the resulting array.

        Returns:
            tuple | None:
                A tuple (timestamp, np.ndarray) if the trigger and read succeed.
                Returns None if the trigger fails.
        """
        resp = await self._mq_client.send("monitor_trigger", name=self._name)
        if self.check_response(resp) is None:
            return None
        ts, data = await self.read_array()
        return ts, data

    async def request_key(self):
        """Request the IPC key for this monitor's data buffer.

        Returns:
            str | None: The IPC key string if available; otherwise None
        """
        resp = await self._mq_client.send("monitor_key", name=self._name)
        if resp := self.check_response(resp):
            return resp["key"]
        return None

    async def read_array(self, dtype_map: dict=None):
        """
        Read the current data array from the IPC buffer. Handles first-time
        IPC connection, resolves metadata, validates data format, and parses
        the shared memory buffer into a NumPy array.
        
        Args:
            dtype_map (dict, optional): convert an arbiatry name into a type. Defaults to None.
                e.g. {"Yo, I'm Mr. Bool": ctypes.c_bool} -> np.bool_
                     {"Hey, I'm Mrs. Bool": np.bool_} -> np.bool_


        Raise:
            RuntimeError: If the IPC buffer contains an invalid magic number.
            RuntimeError: If the IPC buffer does not exists.

        Returns:
            tuple:
                A tuple (timestamp, numpy.ndarray) containing the decoded data.
                Returns (None, None) if metadata parsing fails.
        """
        if self._ipc_client is None:
            key = await self.request_key()
            self._ipc_client = IPCBufferClient(key)
            await self._ipc_client.connect()
            
        metadata = await self.request_metadata()
        dtype = to_numpy_dtype(metadata["dtype"], dtype_map)
        shape = tuple(metadata["shape"])
        # Read from IPC buffer
        raw = await self._ipc_client.read_async()
        magic, version, data_size, timestamp = MONITOR_HEADER.unpack_from(raw, 0)

        # ---- First read logic (initialization phase) ----
        i = 0
        while magic != MAGIC and i < 5 and not self.initialized:
            await asyncio.sleep(1)
            raw = await self._ipc_client.read_async()
            magic, version, data_size, timestamp = MONITOR_HEADER.unpack_from(raw, 0)
            i += 1
        # --------------------------------------------------
        if magic != MAGIC:
            raise RuntimeError(f"Magic number is invalid")
        
        arr = np.frombuffer(raw, dtype=dtype, 
                            count = data_size // dtype.itemsize, 
                            offset=MONITOR_HEADER.size)
        self.initialized = True
        return timestamp, arr.reshape(shape + dtype.shape)

        

class MonitorPool:
    """
    Dynamic container of available monitors. The pool is refreshed using
    the monitor_list command and provides snapshot and metadata helpers.
    """

    def __init__(self, mq_client: MQClient):
        
        """
        Initialize the monitor pool with an MQ client.

        Args:
            mq_client (MQClient): Client used to communicate with the backend.
        """
        self._mq_client = mq_client
        self.monitors: Dict[str, MonitorPool] = {}   # name -> MonitorEndpoint

    async def discover(self):
        """
        Query the backend for the list of available monitors and rebuild
        the internal monitor dictionary.

        Raise:
            RuntimeError: If the backend returns a failure response.
        """
        resp = await self._mq_client.send("monitor_list")

        if resp["status"] != "success":
            raise RuntimeError(f"monitor_list failed: {resp}")

        monitor_infos = resp["response"]["monitors"]

        self.monitors.clear()
        for m in monitor_infos:
            name = m["name"]
            endpoint = MonitorEndpoint(name, self._mq_client)
            self.monitors[name] = endpoint

    def __getitem__(self, name:str) -> MonitorEndpoint:
        """
        Retrieve a monitor endpoint by name.

        Args:
            name (str): Name of the monitor.

        Returns:
            MonitorEndpoint: The corresponding monitor endpoint instance.
        """
        return self.monitors[name]

    def names(self):
        """
        Return a list of all known monitor names.

        Returns:
            list[str]: Names of all discovered monitors.
        """
        return list(self.monitors.keys())
    
    async def snapshot(self, name):
        """
        Trigger acquisition and return snapshot from a monitor.

        Args:
            name (str): Name of the monitor to read.

        Returns:
            tuple | None:
                A tuple (timestamp, numpy_array) on success; otherwise None.
        """
        ts, data = await self[name].request_trigger()
        return ts, data
    
    async def properties(self):
        """
        Retrieve metadata for all monitors in the pool.

        Returns:
            dict:
                Mapping of monitor name → metadata dictionary.
        """
        d = {}
        for name, mon in self.monitors.items():
            d[name] = await mon.request_metadata()
        return d
