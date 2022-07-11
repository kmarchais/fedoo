import fedoo as fd
import numpy as np
import os

#--------------- Pre-Treatment --------------------------------------------------------

fd.ModelingSpace("3D")

meshname = "Domain"
nb_iter = 3

# Mesh.box_mesh(Nx=3, Ny=3, Nz=3, x_min=0, x_max=1, y_min=0, y_max=1, z_min=0, z_max=1, ElementShape = 'hex8', name = meshname) 
# Mesh.import_file('octet_surf.msh', meshname = "Domain")
# Mesh.import_file('data/octet_1.msh', meshname = "Domain")
fd.mesh.import_file('../util/meshes/gyroid.msh', meshname = "Domain")

mesh = fd.Mesh[meshname]

crd = mesh.nodes 

K = 500 # K = 18 #W/K/m
c = 0.500 #J/kg/K
rho = 7800 #kg/m2
material = fd.constitutivelaw.ThermalProperties(K, c, rho, name='ThermalLaw')
wf = fd.WeakForm.HeatEquation("ThermalLaw")
assemb = fd.Assembly.create("ThermalLaw", meshname, name="Assembling")    

#note set for boundary conditions
Xmin, Xmax = mesh.bounding_box
bottom = mesh.find_nodes('Z', Xmin[2])
top = mesh.find_nodes('Z', Xmax[2])
left = mesh.find_nodes('X', Xmin[2])
right = mesh.find_nodes('X', Xmax[2])

fd.Problem.NonLinearStatic("Assembling")

# Problem.SetSolver('cg', precond = True)

fd.Problem.SetNewtonRaphsonErrorCriterion("Displacement", tol = 5e-2, max_subiter=5, err0 = 100)
if not(os.path.isdir('results')): os.mkdir('results')
results = fd.Problem.AddOutput('results/thermal3D', 'Assembling', ['Temp'], output_type='Node', file_format ='npz')    
# Problem.AddOutput('results/bendingPlastic', 'Assembling', ['cauchy', 'PKII', 'strain', 'cauchy_vm', 'statev'], output_type='Element', file_format ='vtk')    

tmax = 10
# Problem.BoundaryCondition('Dirichlet','Temp',0,bottom)
def timeEvolution(timeFactor): 
    if timeFactor == 0: return 0
    else: return 1

# Problem.BoundaryCondition('Dirichlet','Temp',100,left, timeEvolution=timeEvolution)
fd.Problem.BoundaryCondition('Dirichlet','Temp',3,right, timeEvolution=timeEvolution)
# Problem.BoundaryCondition('Dirichlet','Temp',100,top, timeEvolution=timeEvolution)


# Problem.BoundaryCondition('Dirichlet','DispY', 0,nodes_bottomLeft)
# Problem.BoundaryCondition('Dirichlet','DispY',0,nodes_bottomRight)
# bc = Problem.BoundaryCondition('Dirichlet','DispY', uimp, nodes_topCenter)

fd.Problem.NLSolve(dt = tmax/nb_iter, tmax = tmax, update_dt = True)


results.load()
assert np.abs(results.node_data['Temp'][8712]-2.679360557129252) < 1e-15

