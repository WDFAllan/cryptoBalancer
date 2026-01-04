from app.domain.strategies.constantMix.constantMixParams import ConstantMixParams
from app.domain.strategies.constantMix.constantMixStrategy import ConstantMixStrategy
from app.infrastructure.runners.constantMixRunner import ConstantMixRunner
from app.infrastructure.runners.holdRunner import HoldRunner
from app.infrastructure.runners.dynamicThresholdRunner import DynamicThresholdRunner


class StrategyFactory:

    @staticmethod
    def create(name:str):
        if name == "constant_mix":
            return ConstantMixRunner
        if name == "hold":
            return HoldRunner
        if name == "dynamic_threshold":
            return DynamicThresholdRunner

        raise ValueError("Strategy not supported")


