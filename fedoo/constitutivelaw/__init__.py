"""
=========================================================
Constitutive Law (:mod:`fedoo.constitutivelaw`)
=========================================================

.. currentmodule:: fedoo.constitutivelaw

The constitutive law module include several classical mechancical
constitutive laws. These laws are required to create some weak formulations.

The ConstitutiveLaw library contains the following classes:

Solid mechanical constitutive laws
======================================

These laws should be associated with :py:class:`fedoo.weakform.StressEquilibrium`

.. autosummary::
   :toctree: generated/
   :template: custom-class-template.rst

   ElasticIsotrop
   ElasticOrthotropic
   ElasticAnisotropic
   CompositeUD
   ElastoPlasticity
   FE2
   Simcoon

Interface mechanical constitutive laws
======================================

These laws should be associated with :py:class:`fedoo.weakform.StressEquilibrium`

.. autosummary::
   :toctree: generated/
   :template: custom-class-template.rst

   CohesiveLaw
   Spring

Shell constitutive laws
======================================

These laws should be associated with :py:class:`fedoo.weakform.PlateEquilibrium`

.. autosummary::
   :toctree: generated/
   :template: custom-class-template.rst

   ShellLaminate
   ShellHomogeneous

Thermal constitutive law
======================================

These laws should be associated with :py:class:`fedoo.weakform.HeatEquation` or  :py:class:`fedoo.weakform.SteadyHeatEquation`

.. autosummary::
   :toctree: generated/
   :template: custom-class-template.rst

   ThermalProperties

"""

import pkgutil

for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    # module = loader.find_module(module_name).load_module(module_name)
    exec("from ." + module_name + " import *")
