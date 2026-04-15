from base_scheme import BaseScheme
from src.models.base_model import BaseModel

class EulerScheme(BaseScheme):
    def step(self, model: BaseModel, S, t, dt, dW):
        return S + model.drift(S, t) * dt + model.diffusion(S, t) * dW