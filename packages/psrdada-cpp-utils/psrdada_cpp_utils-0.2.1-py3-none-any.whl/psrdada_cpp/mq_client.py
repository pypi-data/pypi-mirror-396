import posix_ipc
import json
import time
import pprint
import asyncio
import logging
import uuid
import os
import sys

log = logging.getLogger("mq-client")

class MQClient:
    def __init__(self, request_q_key, response_prefix="/tmp_response_", max_queue_size=8192):
        self._request_q_key = request_q_key
        self._request_q = None
        self._response_max_queue_size = max_queue_size
        self._response_prefix = response_prefix
        self._ready = False
    
    async def connect(self, timeout=15):
        start = time.time()
        while ((time.time() - start) < timeout):
            try:
                self._request_q = posix_ipc.MessageQueue(self._request_q_key)
                self._ready = True
                break
            except posix_ipc.ExistentialError:
                await asyncio.sleep(1)
        else:
            raise Exception("Timeout on connecting to message queues")
    
    def __del__(self):
        if self._request_q:
            self._request_q.close()
    
    async def send(self, command, timeout=10, **kwargs):
        if not self._ready:
            raise Exception("Client is not connected to queues, did you call connect()?")
        unique_suffix = f"{os.getpid()}_{int(time.time() * 1e6)}_{uuid.uuid4().hex[:6]}"
        response_queue_name = f"{self._response_prefix}{unique_suffix}"
        response_q = posix_ipc.MessageQueue(
            response_queue_name, flags=posix_ipc.O_CREX, max_messages=10, max_message_size=self._response_max_queue_size
        )
        message = json.dumps({
            "command": command,
            "response_queue": response_queue_name,
            "arguments": kwargs
        })
        await asyncio.to_thread(self._request_q.send, message)
        try:
            response_str, _ = await asyncio.to_thread(response_q.receive, timeout=timeout)
            response = json.loads(response_str)
        except posix_ipc.BusyError:
            log.error(f"Timeout waiting for a response to message: {message}")
            raise
        finally:
            response_q.close()
            response_q.unlink()
        return response

    async def show_help(self):
        response = await self.send("help")
        for key, params in response["response"].items():
            msg = "Command:\n"
            msg += f"{key} -- {params['description']}\n"
            if len(params['required_keys']) > 0:
                msg += "\nArgs:\n"
                for key, detail in params['required_keys'].items():
                    msg += f"--> {key} ({detail['type']}): {detail['description']} \n"
            print(msg)


async def main(client):
    await client.connect()
    await client.show_help()
    response = await client.send("record", naccumulations=10, 
                                 output_filepath="/tmp/test.npy", impedance_ohms=50.0, 
                                 reference_power_dbm=6.0)
    print(response)
    #await asyncio.sleep(2)
    #response = await client.send("cancel")
    #print(response)

if __name__ == "__main__":
    client = MQClient(sys.argv[1])
    asyncio.run(main(client))
