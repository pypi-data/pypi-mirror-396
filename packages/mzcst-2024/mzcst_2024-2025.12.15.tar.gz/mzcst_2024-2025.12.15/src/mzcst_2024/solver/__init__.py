"""定义各种求解器对象。"""
from . import hf, lf, mechanics, particles, thermal
from ._general import (
    ADSCosimulation,
    Background,
    Boundary,
    LayerStacking,
    Optimizer,
    ParameterSweep,
    SimuliaCSE,
    SolverParameter,
)
