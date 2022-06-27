#
# Plate element to model the canteleaver beam using different kind of plate elements
#

from fedoo import *
import numpy as np
# from matplotlib import pylab as plt
# import os 

Assembly.DeleteMemory()

Util.ProblemDimension("3D")
E = 1e5 
nu = 0.3

L = 100
h = 20
thickness = 1
F = -10

geomElementType = 'quad4' #choose among 'tri3', 'tri6', 'quad4', 'quad9'
plateElementType = 'p'+geomElementType #plate interpolation. Same as geom interpolation in local element coordinate (change of basis)
reduced_integration = True #if true, use reduce integration for shear 

material = ConstitutiveLaw.ElasticIsotrop(E, nu, ID = 'Material')
ConstitutiveLaw.ShellHomogeneous('Material', thickness, ID = 'PlateSection')

mesh = Mesh.RectangleMesh(51,11,0,L,-h/2,h/2, geomElementType, ndim = 3, ID='plate')

nodes_left = mesh.node_sets['left']
nodes_right = mesh.node_sets['right']

node_right_center = nodes_right[(mesh.nodes[nodes_right,1]**2).argmin()]


if reduced_integration == False:
    WeakForm.Plate("PlateSection", ID = "WFplate") #by default k=0 i.e. no shear effect
    Assembly.Create("WFplate", "plate", plateElementType, ID="plate")    
    post_tt_assembly = 'plate'
else:    
    WeakForm.Plate_RI("PlateSection", ID = "WFplate_RI") #by default k=0 i.e. no shear effect
    Assembly.Create("WFplate_RI", "plate", plateElementType, ID="plate_RI", nb_pg = 1)    
    
    WeakForm.Plate_FI("PlateSection", ID = "WFplate_FI") #by default k=0 i.e. no shear effect
    Assembly.Create("WFplate_FI", "plate", plateElementType, ID="plate_FI") 
    
    Assembly.Sum("plate_RI", "plate_FI", ID = "plate")
    post_tt_assembly = 'plate_FI'


Problem.Static("plate")

Problem.BoundaryCondition('Dirichlet','DispX',0,nodes_left)
Problem.BoundaryCondition('Dirichlet','DispY',0,nodes_left)
Problem.BoundaryCondition('Dirichlet','DispZ',0,nodes_left)
Problem.BoundaryCondition('Dirichlet','RotX',0,nodes_left)
Problem.BoundaryCondition('Dirichlet','RotY',0,nodes_left)
Problem.BoundaryCondition('Dirichlet','RotZ',0,nodes_left)

Problem.BoundaryCondition('Neumann','DispZ',F,node_right_center)

Problem.ApplyBoundaryCondition()
Problem.Solve()

# I = h*thickness**3/12
# # print('Beam analitical deflection: ', F*L**3/(3*E*I))
# # print('Numerical deflection: ', Problem.GetDisp('DispZ')[node_right_center])

assert np.abs(Problem.GetDisp('DispZ')[node_right_center]+19.62990873054593) < 1e-15

# # z, StressDistribution = ConstitutiveLaw.GetAll()['PlateSection'].GetStressDistribution(20)
# # plt.plot(StressDistribution[0], z)