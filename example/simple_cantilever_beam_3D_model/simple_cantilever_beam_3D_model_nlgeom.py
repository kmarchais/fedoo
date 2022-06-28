from fedoo import *
import numpy as np
import time

#--------------- Pre-Treatment --------------------------------------------------------

Util.ProblemDimension("3D")

#Units: N, mm, MPa
#Mesh.box_mesh(Nx=101, Ny=21, Nz=21, x_min=0, x_max=1000, y_min=0, y_max=100, z_min=0, z_max=100, ElementShape = 'hex8', name = 'Domain')
Mesh.box_mesh(Nx=31, Ny=21, Nz=21, x_min=0, x_max=1000, y_min=0, y_max=100, z_min=0, z_max=100, ElementShape = 'hex8', name = 'Domain')

meshname = "Domain"
#mesh = Mesh.get_all()[meshname]
#crd = mesh.nodes 
#xmax = np.max(crd[:,0]) ; xmin = np.min(crd[:,0])
#mesh.add_node_set(list(np.where(mesh.nodes[:,0] == xmin)[0]), "left")
#mesh.add_node_set(list(np.where(mesh.nodes[:,0] == xmax)[0]), "right")

#Material definition
ConstitutiveLaw.ElasticIsotrop(200e3, 0.3, name = 'ElasticLaw')
WeakForm.InternalForce("ElasticLaw", nlgeom = True)

#Assembly (print the time required for assembling)
assemb = Assembly.Create("ElasticLaw", meshname, 'hex8', name="Assembling") 

#Type of problem 
Problem.NonLinearStatic("Assembling")

#Boundary conditions
nodes_left = Mesh.get_all()[meshname].node_sets["left"]
nodes_right = Mesh.get_all()[meshname].node_sets["right"]
nodes_top = Mesh.get_all()[meshname].node_sets["top"]
nodes_bottom = Mesh.get_all()[meshname].node_sets["bottom"]

Problem.BoundaryCondition('Dirichlet','DispX',0,nodes_left)
Problem.BoundaryCondition('Dirichlet','DispY', 0,nodes_left)
Problem.BoundaryCondition('Dirichlet','DispZ', 0,nodes_left)

Problem.BoundaryCondition('Dirichlet','DispY', -10, nodes_right)

Problem.ApplyBoundaryCondition()

#--------------- Solve --------------------------------------------------------
t0 = time.time() 
Problem.SetSolver('cg')
print('Solving...')
Problem.NLSolve(dt=1) 
#Problem.Solve() 
print('Done in ' +str(time.time()-t0) + ' seconds')

#--------------- Post-Treatment -----------------------------------------------
#Get the displacement vector on nodes for export to vtk
U = np.reshape(Problem.GetDisp(),(3,-1)).T

#Get the stress tensor (nodal values)
TensorStrain = assemb.ConvertData(ConstitutiveLaw.get_all()['ElasticLaw'].GetStrain(), 'GaussPoint', 'Node')
TensorStress = assemb.ConvertData(ConstitutiveLaw.get_all()['ElasticLaw'].GetStress(), 'GaussPoint', 'Node')

#PrincipalStress, PrincipalDirection = TensorStress.GetPrincipalStress()
                                                   

#Write the vtk file                            
OUT = Util.ExportData(meshname)

OUT.addNodeData(U.astype(float),'Displacement')
OUT.addNodeData(TensorStress.vtkFormat(),'Stress')
OUT.addNodeData(TensorStress.vonMises(),'VMStress')
OUT.addNodeData(TensorStrain.vtkFormat(),'Strain')
#OUT.addNodeData(PrincipalStress, 'PrincipalStress')
#OUT.addNodeData(PrincipalDirection[0], '1stPrincipalDirection')

OUT.toVTK("simple_cantilever_3D_model.vtk")
# print('Elastic Energy: ' + str(Problem.GetElasticEnergy()))

print('Result file "simple_cantilever_3D_model.vtk" written in the active directory')

