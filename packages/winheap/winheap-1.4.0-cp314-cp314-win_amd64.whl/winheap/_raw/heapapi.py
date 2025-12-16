from ctypes import POINTER, Structure, WinDLL, c_int, c_size_t as SIZE_T
from ctypes.wintypes import BOOL, DWORD, HANDLE, LPCVOID, LPVOID, PHANDLE
from .minwinbase import LPPROCESS_HEAP_ENTRY


kernel = WinDLL('kernel32', use_last_error=True)


kernel.GetProcessHeap.argtypes = []
kernel.GetProcessHeap.restype = HANDLE
kernel.GetProcessHeaps.argtypes = [DWORD, PHANDLE]
kernel.GetProcessHeaps.restype = DWORD
class HEAP_SUMMARY(Structure):
	_fields_ = [('cb', DWORD),('cbAllocated', SIZE_T),('cbCommitted', SIZE_T),('cbReserved', SIZE_T),('cbMaxReserve', SIZE_T)]

PHEAP_SUMMARY = POINTER(HEAP_SUMMARY)

kernel.HeapAlloc.restype = LPVOID
kernel.HeapAlloc.argtypes = [HANDLE, DWORD, SIZE_T]
kernel.HeapCompact.restype = SIZE_T
kernel.HeapCompact.argtypes = [HANDLE, DWORD]
kernel.HeapCreate.restype = HANDLE
kernel.HeapCreate.argtypes = [DWORD, SIZE_T, SIZE_T]
kernel.HeapDestroy.restype = BOOL
kernel.HeapDestroy.argtypes = [HANDLE]
kernel.HeapFree.restype = BOOL
kernel.HeapFree.argtypes = [HANDLE, DWORD, LPVOID]
kernel.HeapLock.restype = BOOL
kernel.HeapLock.argtypes = [HANDLE]
kernel.HeapQueryInformation.argtypes = [HANDLE, c_int, LPVOID, SIZE_T, POINTER(SIZE_T)]
kernel.HeapQueryInformation.restype = BOOL
kernel.HeapReAlloc.restype  = LPVOID
kernel.HeapReAlloc.argtypes = [HANDLE, DWORD, LPVOID, SIZE_T]
kernel.HeapSetInformation.argtypes = [HANDLE, c_int, LPVOID, SIZE_T]
kernel.HeapSetInformation.restype = BOOL
kernel.HeapSize.restype = SIZE_T
kernel.HeapSize.argtypes = [HANDLE, DWORD, LPCVOID]
kernel.HeapSummary.argtypes = [HANDLE, DWORD, PHEAP_SUMMARY]
kernel.HeapSummary.restype = BOOL
kernel.HeapUnlock.argtypes = [HANDLE]
kernel.HeapUnlock.restype = BOOL
kernel.HeapValidate.argtypes = [HANDLE, DWORD, LPCVOID]
kernel.HeapValidate.restype = BOOL
kernel.HeapWalk.argtypes = [HANDLE, LPPROCESS_HEAP_ENTRY]
kernel.HeapWalk.restype = BOOL

get_process_heap = kernel.GetProcessHeap
get_process_heaps = kernel.GetProcessHeaps
heap_alloc = kernel.HeapAlloc
heap_compact = kernel.HeapCompact
heap_create = kernel.HeapCreate
heap_destroy = kernel.HeapDestroy
heap_free = kernel.HeapFree
heap_lock = kernel.HeapLock
heap_query_information = kernel.HeapQueryInformation
heap_realloc = kernel.HeapReAlloc
heap_set_information = kernel.HeapSetInformation
heap_size = kernel.HeapSize
heap_summary = kernel.HeapSummary
heap_unlock = kernel.HeapUnlock
heap_validate = kernel.HeapValidate
heap_walk = kernel.HeapWalk