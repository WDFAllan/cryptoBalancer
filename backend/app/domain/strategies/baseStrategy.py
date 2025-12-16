from abc import abstractmethod, ABC
import pandas as pd

class BaseStrategy(ABC):

    @abstractmethod
    def run(self, df: pd.DataFrame, ) -> pd.DataFrame:
        pass