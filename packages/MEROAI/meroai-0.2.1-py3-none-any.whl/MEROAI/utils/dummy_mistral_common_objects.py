from ..utils import DummyObject, requires_backends
class MistralCommonTokenizer(metaclass=DummyObject):
    _backends = ["mistral-common"]
    def __init__(self, *args, **kwargs):
        requires_backends(self, ["mistral-common"])