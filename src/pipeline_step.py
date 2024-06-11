from abc import ABC, abstractmethod

class PipelineStep(ABC):
    @abstractmethod
    def run(self, input_data):
        pass
