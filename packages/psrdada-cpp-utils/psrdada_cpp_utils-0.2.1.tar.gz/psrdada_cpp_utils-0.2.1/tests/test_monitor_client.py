import unittest
import unittest.mock as umock
import numpy as np
from psrdada_cpp.monitor_client import MonitorEndpoint, MONITOR_HEADER, MAGIC
from psrdada_cpp.type_conversion import to_numpy_dtype
# ------------- # 
# TEST HELPERS  #
# ------------- # 
def make_meta(key, command="", status="success"):
    return {
        "status": status,
        "command": command,
        "message":"some message",
        "response": {
            "dtype": "float",
            "shape": (10, 10),
            "key": key,
        }
    }
async def return_success_meta(command, **kwargs):
    return make_meta(kwargs["name"], command)
async def return_failure_meta(command, **kwargs):
    return make_meta(kwargs["name"], command, status="fail")

TEST_CASES = {
    "gouda": make_meta("gouda"),
    "cheese": make_meta("cheese"),
}
basic_requests = {
    "request_metadata":"monitor_metadata",
    "request_enable":"monitor_enable",
    "request_disable":"monitor_enable",
    "request_trigger":"monitor_trigger",
    "request_key":"monitor_key"
}
# fake data returned from the IPC buffer as bytes
def build_fake_raw_buffer(array: np.ndarray, timestamp: float) -> bytes:
    body = array.tobytes()
    header = MONITOR_HEADER.pack(MAGIC, 1, len(body), timestamp)
    return header + body

class TestMonitorEndpoint(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self._mock_client = umock.MagicMock()
        self._mock_client.send = umock.AsyncMock()
        self._mock_client.send.side_effect = return_success_meta
    
    async def test_basic_request_success(self):
        """Should test the existance of basic requests, the corresponding 
            MQ command, passed arguments passed to MQClient.send() and success response
        """
        for caller_request, command in basic_requests.items():
            for test_name in TEST_CASES.keys():
                # Context manager for convience -> find the failing request/improve failure visibilty
                with self.subTest(caller=caller_request, name=test_name):
                    test_object = MonitorEndpoint(test_name, self._mock_client)
                    # Line below is not ideal as 'read_array' method is only called by 'request_trigger'
                    # on the other hand, it allows generlized testing
                    # Alternativly, one could mock IPCBufferClient, but more overhead
                    test_object.read_array = umock.AsyncMock(return_value=(None, None)) 
                    res = await getattr(test_object, caller_request)()
                    args, kwargs = self._mock_client.send.call_args
                    self.assertIsNotNone(res) # Should never return None
                    self.assertEqual(command, args[0]) 
                    self.assertEqual(test_name, kwargs['name'])
                
    async def test_basic_request_failure(self):
        """Should test the existance of basic requests and fail response
        """
        self._mock_client.send.side_effect = return_failure_meta
        for caller_request in basic_requests.keys():
            for test_name in TEST_CASES.keys():
                # Context manager for convience -> find the failing request / improve failure visibilty
                with self.subTest(caller=caller_request, name=test_name):
                    test_object = MonitorEndpoint(test_name, self._mock_client)
                    test_object.read_array = umock.AsyncMock(return_value=(None, None))
                    with self.assertLogs(level="ERROR") as cm:
                        res = await getattr(test_object, caller_request)()
                        self.assertIn("failed", cm.output[0])
                    self.assertIsNone(res) # Should always return None
        
        
    async def test_request_key(self):
        """Should test that the correct key was returned.
        """
        for test_name in TEST_CASES.keys():
            test_object = MonitorEndpoint(test_name, self._mock_client)
            key = await test_object.request_key()
            self.assertEqual(key, test_name)
    
    
    async def test_request_metadata(self):
        """Should test that request_metadata returns correct meta data
            depending on the choosen monitoring endpoint 
        """
        for test_name in TEST_CASES.keys():
            test_object = MonitorEndpoint(test_name, self._mock_client)
            meta_data = await test_object.request_metadata()
            self.assertEqual(meta_data, TEST_CASES[test_name]["response"])
            
    @umock.patch("psrdada_cpp.monitor_client.IPCBufferClient")
    async def test_request_trigger(self, ipc_mock: umock.MagicMock):
        """_summary_

        Args:
            ipc_mock (umock.MagicMock): _description_
        """
        # We only need meta["response"] data to construct a fake buffer
        meta = make_meta('something')["response"] 
        act_timestamp = 1337.42
        print(to_numpy_dtype(meta["dtype"]))
        act_data = np.arange(np.prod(meta["shape"]), 
                             dtype=np.float32).reshape(meta["shape"])
        raw = build_fake_raw_buffer(act_data, act_timestamp)
        mock_instance = ipc_mock.return_value
        mock_instance.connected = False
        mock_instance.connect = umock.AsyncMock()
        mock_instance.read_async = umock.AsyncMock(return_value=raw)
         # We use the meta information from make_meta() for 'cheese'
        test_object = MonitorEndpoint("cheese", self._mock_client)
        exp_timestamp, exp_data = await test_object.request_trigger()
        self.assertAlmostEqual(act_timestamp, exp_timestamp, delta=0.005)
        self.assertTrue(np.allclose(act_data, exp_data))
            
    def test_check_response_success(self):
        """Should test if the MQ response is a success
        """
        test_object = MonitorEndpoint("I dont care", self._mock_client)
        res = test_object.check_response({"status":"success",
                                          "command":"I like cheese",
                                          "response":{"cheese":"gouda"}})
        self.assertEqual(res, {"cheese":"gouda"})
    
    def test_check_response_fail(self):
        """Should test if the MQ response is a failure
        """
        test_object = MonitorEndpoint("I dont care", self._mock_client)
        with self.assertLogs(level="ERROR") as cm:
            res = test_object.check_response({"status":"I'm not success, so I'm a failure",
                                            "command":"I dont like cheese",
                                            "message":"Some error message",
                                            "response":{"man, im suppose to fail"}})
            self.assertIn("failed", cm.output[0])
        self.assertEqual(res, None)
    
        
        

if __name__ == '__main__':
    unittest.main()
