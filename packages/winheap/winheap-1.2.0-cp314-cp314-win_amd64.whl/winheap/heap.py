from ctypes import WinError, byref
from ctypes.wintypes import ULONG

from ._raw.heapapi import get_process_heap, heap_alloc, heap_compact, heap_create, heap_destroy, heap_free, heap_lock, heap_set_information, heap_unlock

from ._raw.winnt import HEAP_INFORMATION_CLASS


class heap:
	@staticmethod
	def create(flags = 0x00040000, initial_size: int = 0, maximum_size = 2048) -> int:
		hand = heap_create(flags, initial_size, maximum_size)
		if not hand:
			raise WinError()
		return hand

	def release(self):
		bOk = heap_destroy(self._hand)
		if not bOk:
			raise WinError()
		del self._hand
		self._hand = None

	def coalesce(self):
		r'''¯\_(ツ)_/¯'''
		return heap_compact(self.value, 0)

	def close(self, i: int):
		if i in range(len(self.blocks)):
			if not heap_free(self.value, 0, self.blocks[i]):
				raise WinError()
			self.blocks.pop(i)

	def lock(self):
		if not heap_lock(self.value):
			return False
		self._lock = True
		return True

	def unlock(self):
		if not heap_unlock(self.value):
			return False
		self._lock = False
		return True

	def allocate(self, size: int):
		lpmem = heap_alloc(self.value, 8, size )
		if lpmem:
			self.blocks.append(lpmem)
			return lpmem
		return False

	def __init__(self, size: int, max_pages: int):
		self.max = (max_pages, max_pages * 4096)
		self.size = (size, ((size + 4095) & ~4095))
		self._py_heap: int = get_process_heap()
		self._hand = heap.create(initial_size=self.size[1], maximum_size=self.max[1])
		self.blocks: list[int] = []
		heap_set_information(self._hand, HEAP_INFORMATION_CLASS.HeapEnableTerminationOnCorruption, None, 0)
		info = ULONG(0)
		heap_set_information(self._hand, HEAP_INFORMATION_CLASS.HeapCompatibilityInformation, byref(info), 4)
		self.mode = info.value

	@property
	def py_heap(self):
		return self._py_heap

	def __getitem__(self, i: int):
		return self.blocks[i]


	def __exit__(self, unk1, unk2, unk3):
		self.__dt()
	def __enter__(self):
		return self
	@property
	def value(self):
		return self._hand
	def __dt(self):
		if heap:
			if self:
				if self._hand:
					for b in range(len(self.blocks)):
						self.close(b)
					self.release()

	def __del__(self):
		self.__dt()

	def __repr__(self):
		return 'heap at ' + hex(self.value) + '\nPython heap at ' + hex(self.py_heap)

	def __reduce__(self):
		raise BaseException('Heaps cannot be reduced.')