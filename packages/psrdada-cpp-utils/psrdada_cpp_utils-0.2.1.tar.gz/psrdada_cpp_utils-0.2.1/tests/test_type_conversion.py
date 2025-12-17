import unittest
import unittest.mock as umock
import numpy as np
import ctypes
from psrdada_cpp.type_conversion import to_ctypes_type, to_numpy_dtype


def dtype_single(name, base):
    return np.dtype([(name, base)])


def dtype_multi(names, base):
    return np.dtype([(n, base) for n in names])

class TestTypeConversion(unittest.TestCase):
    
    def test_non_exist_ctype(self):
        with self.assertRaises(TypeError):
            to_ctypes_type("Im not a valid data type")
    
    @umock.patch("psrdada_cpp.type_conversion.to_ctypes_type")
    def test_non_exist_npdtype(self, mock):
        instance = mock
        instance.return_value = "Im not a valid data type"
        with self.assertRaises(TypeError):
            to_numpy_dtype("") # Returned value from mock just matters
            
    def test_floating_point_npdtype(self):
        self.assertEqual(np.float32, to_numpy_dtype("float"))
        self.assertEqual(np.float64, to_numpy_dtype("double"))
        self.assertEqual(np.float128, to_numpy_dtype("long double"))
        
    def test_integer_npdtype(self):
        # unsinged 8bit int
        # self.assertEqual(np.ubyte, to_numpy_dtype("unsigned char")) # Doenst work yet
        self.assertEqual(np.uint8, to_numpy_dtype("uint8_t"))
        self.assertEqual(np.uint8, to_numpy_dtype("uint8"))
        self.assertEqual(1, to_numpy_dtype("uint8").itemsize)
        # signed 8bit int
        # self.assertEqual(np.char, to_numpy_dtype("char")) # doenst work yet
        self.assertEqual(np.int8, to_numpy_dtype("int8_t"))
        self.assertEqual(np.int8, to_numpy_dtype("int8"))
        self.assertEqual(1, to_numpy_dtype("int8").itemsize)
        # Unsigned 16bit int 
        self.assertEqual(np.uint16, to_numpy_dtype("unsigned short"))
        self.assertEqual(np.uint16, to_numpy_dtype("uint16_t"))
        self.assertEqual(np.uint16, to_numpy_dtype("uint16"))
        self.assertEqual(2, to_numpy_dtype("uint16").itemsize)
        # Unsigned 16bit int 
        self.assertEqual(np.int16, to_numpy_dtype("short"))
        self.assertEqual(np.int16, to_numpy_dtype("int16_t"))
        self.assertEqual(np.int16, to_numpy_dtype("int16"))
        self.assertEqual(2, to_numpy_dtype("short").itemsize)
        # Unsigned 16bit int 
        self.assertEqual(np.uint32, to_numpy_dtype("unsigned int"))
        self.assertEqual(np.uint32, to_numpy_dtype("uint32_t"))
        self.assertEqual(np.uint32, to_numpy_dtype("uint32"))
        self.assertEqual(4, to_numpy_dtype("unsigned int").itemsize)
        # Signed 32bit int 
        self.assertEqual(np.int32, to_numpy_dtype("int"))
        self.assertEqual(np.int32, to_numpy_dtype("int32_t"))
        self.assertEqual(np.int32, to_numpy_dtype("int32"))
        self.assertEqual(4, to_numpy_dtype("int").itemsize)
        # Unigned 64bit int 
        self.assertEqual(np.uint64, to_numpy_dtype("std::size_t"))
        self.assertEqual(np.uint64, to_numpy_dtype("unsigned long"))
        self.assertEqual(np.uint64, to_numpy_dtype("uint64_t"))
        self.assertEqual(8, to_numpy_dtype("std::size_t").itemsize)
        # Unigned 64bit int 
        self.assertEqual(np.int64, to_numpy_dtype("long"))
        self.assertEqual(np.int64, to_numpy_dtype("int64_t"))
        self.assertEqual(8, to_numpy_dtype("long").itemsize)
        
        
    def test_vector_types_npdtype(self):
        dtype = np.dtype(("float32",(4,)))
        self.assertEqual(dtype, to_numpy_dtype("float4"))
        self.assertEqual(dtype.base, np.float32)
        self.assertEqual(dtype.shape, (4,))
        dtype = np.dtype(("int32",(4,)))
        self.assertEqual(dtype, to_numpy_dtype("int4"))
        self.assertEqual(dtype.base, np.int32)
        self.assertEqual(dtype.shape, (4,))
        dtype = np.dtype(("int64",(2,)))
        self.assertEqual(dtype, to_numpy_dtype("long2"))
        self.assertEqual(dtype.base, np.int64)
        self.assertEqual(dtype.shape, (2,))
        dtype = np.dtype(("float64",(3,)))
        self.assertEqual(dtype, to_numpy_dtype("double3"))
        self.assertEqual(dtype.base, np.float64)
        self.assertEqual(dtype.shape, (3,))
        
    def test_stokes_types(self):
        dt = to_numpy_dtype("psrdada_cpp::StokesVector<float, StokesI>")
        expected = dtype_single("I", np.float32)
        self.assertEqual(dt, expected)
        dt = to_numpy_dtype("StokesVector<double, StokesI>")
        expected = dtype_single("I", np.float64)
        self.assertEqual(dt, expected)
        dt = to_numpy_dtype("StokesVector<float, I>")
        expected = dtype_single("I", np.float32)
        self.assertEqual(dt, expected)
        dt = to_numpy_dtype("StokesVector<float, StokesI, StokesQ>")
        expected = dtype_multi(["I", "Q"], np.float32)
        self.assertEqual(dt, expected)
        dt = to_numpy_dtype("StokesVector<float, StokesI, StokesQ, StokesU>")
        expected = dtype_multi(["I", "Q", "U"], np.float32)
        self.assertEqual(dt, expected)
        dt = to_numpy_dtype("psrdada_cpp::StokesVector<float, I, Q, U, V>")
        expected = dtype_multi(["I", "Q", "U", "V"], np.float32)
        self.assertEqual(dt, expected)
        dt = to_numpy_dtype("StokesVector<int8_t, StokesI, StokesQ>")
        expected = dtype_multi(["I", "Q"], np.int8)
        self.assertEqual(dt, expected)
        dt = to_numpy_dtype("StokesVector<int16_t, I, Q, U>")
        expected = dtype_multi(["I", "Q", "U"], np.int16)
        self.assertEqual(dt, expected)
            
    def test_complex_npdtype(self):
        dtype = np.dtype(("int32",(2,)))
        self.assertEqual(dtype, to_numpy_dtype("complex<int32_t>"))
        self.assertEqual(dtype.base, np.int32)
        self.assertEqual(dtype.shape, (2,))
        dtype = np.dtype(("int8",(2,)))
        self.assertEqual(dtype, to_numpy_dtype("complex<int8_t>"))
        self.assertEqual(dtype.base, np.int8)
        self.assertEqual(dtype.shape, (2,))
        dtype = np.dtype(("float32",(2,)))
        self.assertEqual(dtype, to_numpy_dtype("complex<float>"))
        self.assertEqual(dtype.base, np.float32)
        self.assertEqual(dtype.shape, (2,))
        
    def test_user_conversion_npdtype(self):
        # He is a ctype
        user_conversion = {"Yo, I'm Mr. Bool": ctypes.c_bool}
        self.assertEqual(np.bool_, to_numpy_dtype("Yo, I'm Mr. Bool", user_conversion))
        # She is a np.dtype
        user_conversion = {"Hey, I'm Mrs. Bool": np.bool_}
        self.assertEqual(np.bool_, to_numpy_dtype("Hey, I'm Mrs. Bool", user_conversion))
        
                

if __name__ == '__main__':
    unittest.main()


# def test_stokesvector_weird_spaces():
#     dt = to_numpy_dtype("  psrdada_cpp::StokesVector< float ,  StokesI ,  StokesQ  > ")
#     expected = dtype_multi(["I", "Q"], np.float32)
#     self.assertEqual(dt, expected)


# def test_stokesvector_namespace_prefixes():
#     dt = to_numpy_dtype("StokesVector<float, psrdada_cpp::StokesU, psrdada_cpp::StokesV>")
#     expected = dtype_multi(["U", "V"], np.float32)
#     self.assertEqual(dt, expected)


# # -----------------------------------------------
# # Edge cases
# # -----------------------------------------------

# def test_stokesvector_single_parameter_alias():
#     # Only alias "Q"
#     dt = to_numpy_dtype("StokesVector<float, Q>")
#     expected = dtype_single("Q", np.float32)
#     self.assertEqual(dt, expected)


# def test_stokesvector_four_params_mixed():
#     dt = to_numpy_dtype(
#         "StokesVector<float, StokesI, Q, psrdada_cpp::StokesU, V>"
#     )
#     expected = dtype_multi(["I", "Q", "U", "V"], np.float32)
#     self.assertEqual(dt, expected)


# def test_invalid_missing_parameters():
#     with pytest.raises(TypeError):
#         to_numpy_dtype("StokesVector<float>")     # invalid C++ form
