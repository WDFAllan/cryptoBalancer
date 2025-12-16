from app.domain.strategies.constantMix.constantMixParams import ConstantMixParams
from app.domain.strategies.constantMix.constantMixStrategy import ConstantMixStrategy
from app.infrastructure.runners.constantMixRunner import ConstantMixRunner


class StrategyFactory:

    @staticmethod
    def create(name:str):
        if name == "constant_mix":
            return ConstantMixRunner

        raise ValueError("Strategy not supported")


