from src.models.base_model import BaseModel
from src.models.black_scholes_model import BlackScholesModel
from src.process.base_process import StochasticProcess
from src.process.gbm_process import GBMProcess


class ProcessFactory:

    @staticmethod
    def create(model: BaseModel) -> StochasticProcess:
        if isinstance(model, BlackScholesModel):
            return GBMProcess(model)

        raise ValueError("Unsupported model")