"""
2D plate with hole in tension
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Simple example of a plate with hole in tension with 2D plane stress assumption. 
"""
import fedoo as fd 
import numpy as np
import pyvista as pv

#--------------- Pre-Treatment --------------------------------------------------------
fd.ModelingSpace("2Dstress")

# read a mesh that is initialy in 3D (3 coordinates) and remove the 3rd coordinates
mesh = fd.mesh.import_file('plate_with_hole.msh').as_2d()
# 
#alternative mesh below (uncomment the line)
# mesh = fd.mesh.hole_plate_mesh()
# mesh = fd.mesh.rectangle_mesh(nx=101, ny=101, x_min=-50, x_max=50, y_min=-50, y_max=50, elm_type='quad4')

#Material definition
fd.constitutivelaw.ElasticIsotrop(1e5, 0.3, name = 'ElasticLaw')
fd.weakform.StressEquilibrium("ElasticLaw", name="Weakform")

#Assembly
fd.Assembly.create("Weakform", mesh, name="Assembling") 

#Type of problem 
pb = fd.problem.Linear("Assembling")

#Boundary conditions

#Definition of the set of nodes for boundary conditions
mesh.add_node_set(mesh.find_nodes('X', mesh.bounding_box.xmin), 'left')
mesh.add_node_set(mesh.find_nodes('X', mesh.bounding_box.xmax), 'right')

pb.bc.add('Dirichlet', "left", 'DispX',-5e-1)
pb.bc.add('Dirichlet', "right", 'DispX', 5e-1)
pb.bc.add('Dirichlet',[0], 'DispY',0)

pb.apply_boundary_conditions()

#--------------- Solve --------------------------------------------------------
pb.set_solver('CG')
pb.solve()

#--------------- Post-Treatment -----------------------------------------------
res = pb.get_results("Assembling", ['Disp', 'Stress','Strain'], 'Node')
pl = pv.Plotter(shape=(2,2))

### to use the background plotter, uncomment the following lines ###
# from pyvistaqt import BackgroundPlotter
# pl = BackgroundPlotter(shape = (2,2))

res.plot('Stress','vm','Node', plotter=pl)
pl.subplot(1,0)
res.plot('Stress','XX','Node', plotter=pl)
pl.subplot(0,1)
res.plot('Stress', 'YY', 'Node', plotter=pl)
pl.subplot(1,1)
res.plot('Stress', 'XY','Node',  plotter=pl)
pl.show()
    