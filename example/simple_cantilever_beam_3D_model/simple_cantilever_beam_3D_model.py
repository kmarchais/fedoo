import fedoo as fd
import numpy as np
import time

#--------------- Pre-Treatment --------------------------------------------------------

fd.ModelingSpace("3D")

#Units: N, mm, MPa
#fd.mesh.box_mesh(nx=101, ny=21, nz=21, x_min=0, x_max=1000, y_min=0, y_max=100, z_min=0, z_max=100, elm_type = 'hex8', name = 'Domain')
fd.mesh.box_mesh(nx=101, ny=21, nz=21, x_min=0, x_max=1000, y_min=0, y_max=100, z_min=0, z_max=100, elm_type = 'hex8', name = 'Domain')

meshname = "Domain"
#mesh = Mesh.get_all()[meshname]
#crd = mesh.nodes 
#xmax = np.max(crd[:,0]) ; xmin = np.min(crd[:,0])
#mesh.add_node_set(list(np.where(mesh.nodes[:,0] == xmin)[0]), "left")
#mesh.add_node_set(list(np.where(mesh.nodes[:,0] == xmax)[0]), "right")

#Material definition
fd.constitutivelaw.ElasticIsotrop(200e3, 0.3, name = 'ElasticLaw')
fd.weakform.InternalForce("ElasticLaw")

#Assembly (print the time required for assembling)
fd.Assembly.create("ElasticLaw", meshname, 'hex8', name="Assembling") 

#Type of problem 
pb = fd.problem.Linear("Assembling")

#Boundary conditions
nodes_left = fd.Mesh[meshname].node_sets["left"]
nodes_right = fd.Mesh[meshname].node_sets["right"]
nodes_top = fd.Mesh[meshname].node_sets["top"]
nodes_bottom = fd.Mesh[meshname].node_sets["bottom"]

pb.bc.add('Dirichlet',nodes_left, 'Disp', 0)
pb.bc.add('Dirichlet',nodes_right, 'DispY', -10)

pb.apply_boundary_conditions()

#--------------- Solve --------------------------------------------------------
t0 = time.time() 
# pb.set_solver('cg') #uncomment for conjugate gradient solver
print('Solving...')
pb.solve() 
print('Done in ' +str(time.time()-t0) + ' seconds')

res = pb.get_results('Assembling', ['Stress']).plot('Stress')


#--------------- Post-Treatment -----------------------------------------------
#Get the displacement vector on nodes for export to vtk
U = np.reshape(pb.get_dof_solution('all'),(3,-1)).T

#Get the stress tensor (nodal values)
TensorStrain = fd.Assembly['Assembling'].get_strain(pb.get_dof_solution(), "Node")       
TensorStress = pb.get_results('Assembling', ['Stress'], 'Node')['Stress']
# ConstitutiveLaw.get_all()['ElasticLaw'].GetStress()

#PrincipalStress, PrincipalDirection = TensorStress.GetPrincipalStress()

# Get the principal directions (vectors on nodes)
#temp = np.array([np.linalg.eig([[TensorStress[0][nd], TensorStress[5][nd]],[TensorStress[5][nd], TensorStress[1][nd]]])[1] for nd in range(len(TensorStress[0]))])
#PrincipalDirection1 = np.c_[temp[:,:,0], np.zeros(len(TensorStress[0]))]
#PrincipalDirection2 = np.c_[temp[:,:,1], np.zeros(len(TensorStress[0]))]

#modification of TensorStress and TensorStressEl for compatibility with the export to vtk 
#TensorStress = np.vstack([TensorStress[i] for i in [0,1,2,5,3,4]]).T                         
#TensorStressEl = np.vstack([TensorStressEl[i] for i in [0,1,2,5,3,4]]).T 
#TensorStrain = np.vstack([TensorStrain[i] for i in [0,1,2,5,3,4]]).T                         
#TensorStrainEl = np.vstack([TensorStrainEl[i] for i in [0,1,2,5,3,4]]).T 
                                                    

# #Write the vtk file                            
# OUT = Util.ExportData(meshname)

# OUT.addNodeData(U.astype(float),'Displacement')
# OUT.addNodeData(TensorStress.vtkFormat(),'Stress')
# OUT.addNodeData(TensorStress.vonMises(),'VMStress')
# OUT.addNodeData(TensorStrain.vtkFormat(),'Strain')
# #OUT.addNodeData(PrincipalStress, 'PrincipalStress')
# #OUT.addNodeData(PrincipalDirection[0], '1stPrincipalDirection')

# OUT.toVTK("simple_cantilever_3D_model.vtk")
# print('Elastic Energy: ' + str(pb.GetElasticEnergy()))

# print('Result file "simple_cantilever_3D_model.vtk" written in the active directory')

