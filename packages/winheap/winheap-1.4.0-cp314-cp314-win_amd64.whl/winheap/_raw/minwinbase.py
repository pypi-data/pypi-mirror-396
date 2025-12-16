from ctypes import POINTER, Structure, Union
from ctypes.wintypes import BYTE, DWORD, LPVOID, HANDLE, WORD

class Region(Structure):
	_fields_ = [('dwCommittedSize', DWORD), ('dwUnCommittedSize', DWORD), ('lpFirstBlock', LPVOID), ('lpLastBlock', LPVOID),]

class Block(Structure):
	_fields_ = [('hMem', HANDLE), ('dwReserved', DWORD * 3)]

class DUMMYUNIONNAME(Union):
	_fields_ = [('Block', Block), ('Region', Region)]

class PROCESS_HEAP_ENTRY(Structure):
	_anonymous_ = ('DUMMYUNIONNAME',)
	_fields_ = [('lpData', LPVOID), ('cbData', DWORD), ('cbOverhead', BYTE), ('iRegionIndex', BYTE), ('wFlags', WORD), ('DUMMYUNIONNAME', DUMMYUNIONNAME)]

LPPROCESS_HEAP_ENTRY = POINTER(PROCESS_HEAP_ENTRY)
PPROCESS_HEAP_ENTRY = POINTER(PROCESS_HEAP_ENTRY)