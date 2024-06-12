# import pkgutil

# from .AssemblyPGDtest import AssemblyPGDtest as Assembly
from .AssemblyPGD import AssemblyPGD as Assembly
from .MeshPGD import MeshPGD as Mesh
from .PeriodicBoundaryConditionPGD import DefinePeriodicBoundaryCondition
from .ProblemPGD import Linear, ProblemPGD
from .SeparatedArray import (
    ConvertArraytoSeparatedArray,
    MergeSeparatedArray,
    SeparatedArray,
    SeparatedOnes,
    SeparatedZeros,
)
from .SeparatedOperator import SeparatedOperator
from .UsualFunctions import divide, exp, inv, power, sqrt


# for loader, module_name, is_pkg in  pkgutil.walk_packages(__path__):
#     module = loader.find_module(module_name).load_module(module_name)
#     exec('from .'+module_name+' import *')
