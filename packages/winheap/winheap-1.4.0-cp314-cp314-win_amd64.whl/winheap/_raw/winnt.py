from enum import IntEnum


class HEAP_INFORMATION_CLASS(IntEnum):
	HeapCompatibilityInformation = 0
	HeapEnableTerminationOnCorruption = 1
	HeapOptimizeResources = 3
	HeapTag = 4