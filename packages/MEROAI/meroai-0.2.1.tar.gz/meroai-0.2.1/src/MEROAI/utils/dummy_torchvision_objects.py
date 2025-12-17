from ..utils import DummyObject, requires_backends
class BaseImageProcessorFast(metaclass=DummyObject):
    _backends = ["torchvision"]
    def __init__(self, *args, **kwargs):
        requires_backends(self, ["torchvision"])
class BaseVideoProcessor(metaclass=DummyObject):
    _backends = ["torchvision"]
    def __init__(self, *args, **kwargs):
        requires_backends(self, ["torchvision"])