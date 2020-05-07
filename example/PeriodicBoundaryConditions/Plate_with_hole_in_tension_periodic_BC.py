from fedoo import *
import numpy as np
import time

#--------------- Pre-Treatment --------------------------------------------------------

Util.ProblemDimension("2Dstress")

Mesh.ImportFromFile('plate_with_hole.msh', meshID = "Domain")

#alternative mesh below (uncomment the line)
# Mesh.RectangleMesh(Nx=51, Ny=51, x_min=-50, x_max=50, y_min=-50, y_max=50, ElementShape = 'quad4', ID ="Domain")
type_el = Mesh.GetAll()['Domain'].GetElementShape()

meshID = "Domain"

#Definition of the set of nodes for boundary conditions
mesh = Mesh.GetAll()[meshID]
crd = mesh.GetNodeCoordinates() 
xmax = np.max(crd[:,0]) ; xmin = np.min(crd[:,0])
ymax = np.max(crd[:,1]) ; ymin = np.min(crd[:,1])

center = [np.linalg.norm(crd,axis=1).argmin()]

StrainNodes = Mesh.GetAll()[meshID].AddNodes(np.zeros(crd.shape[1]),2) #add virtual nodes for macro strain

#Material definition
ConstitutiveLaw.ElasticIsotrop(1e5, 0.3, ID = 'ElasticLaw')
WeakForm.InternalForce("ElasticLaw")

#Assembly
Assembly.Create("ElasticLaw", meshID, type_el, ID="Assembling") 

#Type of problem 
Problem.Static("Assembling")

#Boundary conditions
Exx = 0
Eyy = 0
Exy = 1

Util.DefinePeriodicBoundaryCondition("Domain", [StrainNodes[0], StrainNodes[1], StrainNodes[0]], ['DispX', 'DispY', 'DispY'], dim='2D')

Problem.BoundaryCondition('Dirichlet','DispX', 0, center)
Problem.BoundaryCondition('Dirichlet','DispY', 0, center)

Problem.BoundaryCondition('Dirichlet','DispX', Exx, [StrainNodes[0]]) #EpsXX
Problem.BoundaryCondition('Dirichlet','DispY', Exy, [StrainNodes[0]]) #EpsXY
# Problem.BoundaryCondition('Neumann','DispX', 1e4, [StrainNodes[0]]) #EpsXY

Problem.BoundaryCondition('Dirichlet','DispX', 0, [StrainNodes[1]]) #nothing (blocked to avoir singularity)
Problem.BoundaryCondition('Dirichlet','DispY', Eyy, [StrainNodes[1]]) #EpsYY

Problem.ApplyBoundaryCondition()

#--------------- Solve --------------------------------------------------------
Problem.SetSolver('CG')
t0 = time.time() 
print('Solving...')
Problem.Solve()
print('Done in ' +str(time.time()-t0) + ' seconds')

#--------------- Post-Treatment -----------------------------------------------

#Get the stress tensor (nodal values)
TensorStrain = Assembly.GetAll()['Assembling'].GetStrainTensor(Problem.GetDisp(), "Nodal")       
TensorStress = ConstitutiveLaw.GetAll()['ElasticLaw'].GetStress(TensorStrain)

#Get the stress tensor (element values)
TensorStrainEl = Assembly.GetAll()['Assembling'].GetStrainTensor(Problem.GetDisp(), "Element")       
TensorStressEl = ConstitutiveLaw.GetAll()['ElasticLaw'].GetStress(TensorStrainEl)

# Get the principal directions (vectors on nodes)
PrincipalStress, PrincipalDirection = TensorStress.GetPrincipalStress()

#Get the displacement vector on nodes for export to vtk
U = np.reshape(Problem.GetDoFSolution('all'),(2,-1)).T
N = Mesh.GetAll()[meshID].GetNumberOfNodes()
U = np.c_[U,np.zeros(N)]

#Write the vtk file                            
OUT = Util.ExportData(meshID)

OUT.addNodeData(U,'Displacement')
OUT.addNodeData(TensorStress.vtkFormat(),'Stress')
OUT.addElmData(TensorStressEl.vtkFormat(),'Stress')
OUT.addNodeData(TensorStrain.vtkFormat(),'Strain')
OUT.addElmData(TensorStrainEl.vtkFormat(),'Strain')
OUT.addNodeData(TensorStress.vonMises(),'VMStress')
OUT.addElmData(TensorStressEl.vonMises(),'VMStress')
OUT.addNodeData(PrincipalStress,'PrincipalStress')
OUT.addNodeData(PrincipalDirection[0],'DirPrincipal1')
OUT.addNodeData(PrincipalDirection[1],'DirPrincipal2')

OUT.toVTK("plate_with_hole_in_tension.vtk")
print('Elastic Energy: ' + str(Problem.GetElasticEnergy()))

print('Result file "plate_with_hole_in_tension.vtk" written in the active directory')


# F = Assembly.GetAll()["Assembling"].GetExternalForces(Problem.GetDoFSolution('all'))

#Try to get the reaction force = mean stress, from assembly
# M = Assembly.GetAll()["Assembling"].GetMatrix()
# B = Problem.BoundaryCondition.M
# F = np.reshape((M+B.T@M@B)@Problem.GetDoFSolution('all') , (2,-1)).T
# print(F[-2]/(100*100))
print([Problem.GetDisp('DispX')[-2], Problem.GetDisp('DispY')[-2]])

#Try to compute the mean stress 
#Get the stress tensor (PG values)
TensorStrain = Assembly.GetAll()['Assembling'].GetStrainTensor(Problem.GetDisp(), "GaussPoint", Linear = True)       
TensorStress = ConstitutiveLaw.GetAll()['ElasticLaw'].GetStress(TensorStrain)

# Surf = sum(Assembly.Assembly._Assembly__GetGaussianQuadratureMatrix(mesh, type_el)@(np.ones_like(TensorStress[5])))
Surf = (xmax-xmin)*(ymax-ymin)
S2 = [1/Surf*sum(Assembly.Assembly._Assembly__GetGaussianQuadratureMatrix(mesh, type_el)@TensorStress[i]) for i in [0,1,5]]
# E2 = [1/Surf*sum(Assembly.Assembly._Assembly__GetGaussianQuadratureMatrix(mesh, type_el)@TensorStrain[i]) for i in [0,1,5]]

print(S2)
# print(E2)
# print('G: '+str(1e5/(2*(1+0.3))))
# print('E: '+str(1e5))
# print(ConstitutiveLaw.GetAll()['ElasticLaw'].GetH())