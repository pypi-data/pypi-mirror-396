import posix_ipc
import json
import mmap
import ctypes
import pprint
import time
import argparse
import re
import numpy as np
from datetime import datetime

MAGIC_NUMBER = 0x51a0cbb8

class DescriptorHeader(ctypes.Structure):
    _pack_ = 1 
    _fields_ = [
        ('magic', ctypes.c_int),     
        ('version', ctypes.c_int), 
        ('descriptor_size', ctypes.c_int) 
    ]


# These are custom conversions for non trivially 
# parseable types.
TYPE_CONVERSIONS = {
    "complex<float>": ctypes.c_float * 2,
    "complex<double>": ctypes.c_double * 2,
}


def to_ctypes_type(type_name):
    # first strip the std:: namespace if it is included
    type_name = type_name.replace("std::","")
    
    # now look if there is a user defined conversion
    if type_name in TYPE_CONVERSIONS:
        return TYPE_CONVERSIONS[type_name]
    
    # next remove any spaces from the typename
    # removed the word signed and convert unsigned to i
    type_name = type_name.replace(" ", "")
    type_name = type_name.replace("unsigned", "u")
    type_name = type_name.replace("signed", "")
    
    # next first check if there is a trivial conversion, e.g. int
    try:
        return getattr(ctypes, f"c_{type_name}")
    except AttributeError:
        pass
    
    # next check if it is a cstdint-like type with a _t suffix, e.g. uint64_t
    try:
        return getattr(ctypes, f"c_{type_name.rstrip("_t")}")
    except AttributeError:
        pass
    
    # finally check if there is a vector type conversion, e.g. float4, char2
    match = re.match(r'([a-zA-Z]+)(\d+)$', type_name)
    if match:
        if match.group(1) == "char":
            base_type = "int8"
        else:
            base_type = match.group(1)
        return getattr(ctypes, f"c_{base_type}") * int(match.group(2))
    else:
        raise Exception("No valid type conversion for {}".format(type_name))
        
        
def create_data_type(name, json_desc):
    struct_fields = []
    for field in json_desc['fields']:
        field_name = field['name']
        field_type = field['type']
        field_count = field['count']
        ctypes_type = to_ctypes_type(field_type)
        if field_count > 1:
            field_type = ctypes_type * field_count  
        else:
            field_type = ctypes_type
        struct_fields.append((field_name, field_type))
    
    return type(name, (ctypes.Structure,), {'_fields_': struct_fields, '_pack_': 1})

         
class Lock:
    def __init__(self, mutex, update=None):
        self._mutex = mutex
        self._update = update
        
    def __enter__(self):
        self._mutex.acquire()
        
    def __exit__(self, *args):
        self._mutex.release()
        if self._update:
            self._update.release()
          
            
class SharedStruct:
    def __init__(self, key):
        self._shm = posix_ipc.SharedMemory(key, posix_ipc.O_RDWR)
        self._update_sem = posix_ipc.Semaphore(key+"_update", flags=0)
        self._mutex_sem = posix_ipc.Semaphore(key+"_mutex", flags=0)
        self._mm = mmap.mmap(self._shm.fd, 0)
        self._header = DescriptorHeader.from_buffer(self._mm)
        if self._header.magic != MAGIC_NUMBER:
            raise Exception("Buffer is not parseable (non-matching magic number)")
        self._mm.seek(ctypes.sizeof(DescriptorHeader))
        self._descriptor = json.loads(self._mm.read(self._header.descriptor_size))
        self._type = create_data_type("MonitoringData", self._descriptor)
        offset = ctypes.sizeof(DescriptorHeader) + self._header.descriptor_size
        self._data = self._type.from_buffer(self._mm, offset)
        self._keys = [field["name"] for field in self._descriptor["fields"]]
        self._field_map = {field["name"]: field for field in self._descriptor["fields"]}
        self._last_update_count = self._update_sem.value
    
    def descriptor(self):
        return self._descriptor
    
    def has_update(self):
        val = self._update_sem.value 
        if self._last_update_count == val:
            return False
        else:
            self._last_update_count = val
            return True
    
    def lock(self, notify=False):
        if notify:
            return Lock(self._mutex_sem, self._update_sem)
        else:
            return Lock(self._mutex_sem)
        
    def read(self, key):
        if self._field_map[key]["count"] > 1:
            return np.ctypeslib.as_array(getattr(self._data, key))
        else:
            return getattr(self._data, key)
    
    def write(self, key, value):
        if isinstance(value, str):
            value = value.encode("utf-8")
        setattr(self._data, key, value)
        
    def display(self):
        box_top = "┌" + "─" * 58 + "┐"
        box_bottom = "└" + "─" * 58 + "┘"
        box_sep = "├" + "─" * 58 + "┤"

        print("\n" + box_top)
        for i, key in enumerate(self._keys):
            if i > 0:
                print(box_sep)
            params = self._field_map[key]
            value = self.read(key)
            print(f"│ Name       : {params['name']:<44}│")
            print(f"│ Description: {params['description']:<44}│")
            print(f"│ Type       : {params['type']:<44}│")
            vallines = str(value).splitlines()
            print(f"│ Value      : {vallines[0]:<44}│")
            if len(vallines) > 1:
                for line in vallines[1:]:
                    print(f"│              {line:<44}│")
        print(box_bottom + "\n")


def main():
    parser = argparse.ArgumentParser(description="Monitor a shared memory buffer and display updates.")
    parser.add_argument("key", help="Shared memory key")
    parser.add_argument("--safe", action="store_true", help="Enable safe reading (use locks)")

    args = parser.parse_args()
    
    mon = SharedStruct(args.key)
    
    try:
        while True:
            if mon.has_update():
                if args.safe:
                    with mon.lock():
                        print(f"Update detected at {datetime.now()}:")
                        mon.display()
                else:
                    print(f"Update detected at {datetime.now()}:")
                    mon.display()
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()
