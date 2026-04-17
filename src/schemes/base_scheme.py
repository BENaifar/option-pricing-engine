from abc import ABC

from src.models.base_model import BaseModel


class BaseScheme(ABC):
    def step(self, model: BaseModel, S, t, dt, brownian_increment):
        pass