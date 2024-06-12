"""===========================================
Geometry and Mesh (:mod:`fedoo.mesh`)
===========================================

.. currentmodule:: fedoo

Class Mesh
====================

.. autosummary::
   :toctree: generated/
   :template: custom-class-template.rst

   Mesh

.. currentmodule:: fedoo.mesh

Mesh manipulation functions
==================================

.. autosummary::
   :toctree: generated/

   stack
   extrude
   extract_surface
   change_elm_type
   quad2tri

.. _importmesh:

Import/Export Fedoo Mesh object
==================================

.. autosummary::
   :toctree: generated/

   import_file
   import_msh
   import_vtk


.. _build_simple_mesh:

Mesh Creation Functions
===============================

.. autosummary::
   :toctree: generated/

   rectangle_mesh
   box_mesh
   disk_mesh
   hole_plate_mesh
   hollow_disk_mesh
   I_shape_mesh
   line_mesh_1D
   line_mesh
   line_mesh_cylindric
   grid_mesh_cylindric
   structured_mesh_2D
   generate_nodes
"""


# import pkgutil

# for loader, module_name, is_pkg in  pkgutil.walk_packages(__path__):
#     module = loader.find_module(module_name).load_module(module_name)
#     exec('from .'+module_name+' import *')

from .functions import change_elm_type, extract_surface, extrude, quad2tri
from .importmesh import import_file, import_msh, import_vtk
from .simple import (
    box_mesh,
    grid_mesh_cylindric,
    line_mesh,
    line_mesh_1D,
    line_mesh_cylindric,
    rectangle_mesh,
    stack,
)
from .structured_mesh import (
    I_shape_mesh,
    disk_mesh,
    generate_nodes,
    hole_plate_mesh,
    hollow_disk_mesh,
    structured_mesh_2D,
)
