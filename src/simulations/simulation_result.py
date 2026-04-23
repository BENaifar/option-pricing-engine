from dataclasses import dataclass

import numpy as np

@dataclass(frozen=True)
class SimulationResult:
    terminal_paths: np.ndarray
    normals: np.ndarray
    dt: float