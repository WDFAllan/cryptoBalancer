from app.domain.strategies.constantMix.constantMixParams import ConstantMixParams
from app.domain.strategies.constantMix.constantMixStrategy import ConstantMixStrategy
from app.infrastructure.runners.constantMixRunner import ConstantMixRunner
from app.infrastructure.runners.holdRunner import HoldRunner


class StrategyFactory:

    @staticmethod
    def create(name:str):
        if name == "constant_mix":
            return ConstantMixRunner
        if name == "hold":
            return HoldRunner

        raise ValueError("Strategy not supported")


