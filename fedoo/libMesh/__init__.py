"""
===========================================
Geometry and Mesh (:mod:`fedoo.libMesh`)
===========================================

.. currentmodule:: fedoo.libMesh.Mesh

Class Mesh
====================

.. autosummary::   
   :toctree: generated/
   :template: custom-class-template.rst

   Mesh



.. currentmodule:: fedoo.libMesh

Mesh manipulation functions
==================================

.. autosummary::
   :toctree: generated/
   
   get_all
   stack

Import/Export Fedoo Mesh object        
==================================

.. autosummary::
   :toctree: generated/

   import_file
   import_msh
   import_vtk


Mesh Creation Functions
===============================

.. autosummary::
   :toctree: generated/
   
   rectangle_mesh 
   grid_mesh_cylindric
   line_mesh_1D
   line_mesh_cylindric
   box_mesh
   structured_mesh_2D
   generate_nodes          
"""


import pkgutil

for loader, module_name, is_pkg in  pkgutil.walk_packages(__path__):
    module = loader.find_module(module_name).load_module(module_name)
    exec('from .'+module_name+' import *')
    
    
