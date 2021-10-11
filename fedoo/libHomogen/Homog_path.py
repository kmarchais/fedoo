#derive de ConstitutiveLaw
#This law should be used with an InternalForce WeakForm

from simcoon import simmit as sim
from fedoo.libMesh import MeshBase as Mesh
from fedoo.libConstitutiveLaw import Simcoon
from fedoo.libWeakForm import InternalForce
from fedoo.libAssembly import Assembly
from fedoo.libProblem import NonLinearStatic, BoundaryCondition
from fedoo.libUtil import DefinePeriodicBoundaryCondition
import numpy as np
import os
import time

def SolverUnitCell(mesh, umat_name, props, nstatev, solver_type, corate_type, path_data, path_results, path_file, outputfile):

    #Definition of the set of nodes for boundary conditions
    if isinstance(mesh, str):
        mesh = Mesh.GetAll()[mesh]
        
    crd = mesh.GetNodeCoordinates()
    type_el = mesh.GetElementShape()

    xmax = np.max(crd[:,0]) ; xmin = np.min(crd[:,0])
    ymax = np.max(crd[:,1]) ; ymin = np.min(crd[:,1])
    zmax = np.max(crd[:,2]) ; zmin = np.min(crd[:,2])
    crd_center = (np.array([xmin, ymin, zmin]) + np.array([xmax, ymax, zmax]))/2
    center = [np.linalg.norm(crd-crd_center,axis=1).argmin()]

    Volume = (xmax-xmin)*(ymax-ymin)*(zmax-zmin) #total volume of the domain

    StrainNodes = mesh.AddNodes(crd_center,2) #add virtual nodes for macro strain

    
    if isinstance(umat_name, str):
        material = Simcoon(umat_name, props, nstatev, ID='ConstitutiveLaw')
        material.corate = corate_type
    else:
        material = umat_name
        

    #Assembly
    InternalForce(material, ID="wf")
    Assembly("wf", mesh, type_el, ID="Assembling")

    #Type of problem
    pb = NonLinearStatic("Assembling")
    
    #Shall add other conditions later on
    DefinePeriodicBoundaryCondition(mesh,
    [StrainNodes[0], StrainNodes[0], StrainNodes[0], StrainNodes[1], StrainNodes[1], StrainNodes[1]],
    ['DispX',        'DispY',        'DispZ',       'DispX',         'DispY',        'DispZ'], dim='3D')

    readPath = sim.read_path(path_data,path_file)
    blocks = readPath[1]

    MeanStress = np.zeros(6)
    MeanStrain = np.zeros(6)
    T = readPath[0] #temperature
    time = 0.

    BoundaryCondition('Dirichlet','DispX', 0, center)
    BoundaryCondition('Dirichlet','DispY', 0, center)
    BoundaryCondition('Dirichlet','DispZ', 0, center)

    #create a 'result' folder and set the desired ouputs
    if not(os.path.isdir(path_results)): os.mkdir(path_results)

    listBC =[];
    for block in blocks:
        for step in block:
            step.generate(time, MeanStrain, MeanStress, T)
            # print(step.mecas)
            
            #Boundary conditions
            BC_meca = step.BC_meca #stress or strain BC
            mecas = step.mecas
            
            BCtype = np.array(['Dirichlet' for i in range(6)])
            BCtype[step.cBC_meca.astype(bool)] = 'Neumann'

            for i, dt in enumerate(step.times):

                initValue = np.array(MeanStrain)
                initValue[step.cBC_meca.astype(bool)] = MeanStress[step.cBC_meca.astype(bool)]
                
                for bc in listBC:
                    bc.Remove()
                
                listBC = []
                listBC.append(BoundaryCondition(BCtype[0],'DispX', initValue[0] + mecas[0,i], [StrainNodes[0]], initialValue = initValue[0])) #EpsXX
                listBC.append(BoundaryCondition(BCtype[1],'DispY', initValue[1] + mecas[1,i], [StrainNodes[0]], initialValue = initValue[1])) #EpsYY
                listBC.append(BoundaryCondition(BCtype[2],'DispZ', initValue[2] + mecas[2,i], [StrainNodes[0]], initialValue = initValue[2])) #EpsZZ
                listBC.append(BoundaryCondition(BCtype[3],'DispX', initValue[3] + mecas[3,i], [StrainNodes[1]], initialValue = initValue[3])) #EpsXY
                listBC.append(BoundaryCondition(BCtype[4],'DispY', initValue[4] + mecas[4,i], [StrainNodes[1]], initialValue = initValue[4])) #EpsXZ
                listBC.append(BoundaryCondition(BCtype[5],'DispZ', initValue[5] + mecas[5,i], [StrainNodes[1]], initialValue = initValue[5])) #EpsYZ
                
                #pb.ApplyBoundaryCondition()
                pb.NLSolve(dt = dt*step.Dn_init, dt_min = dt*step.Dn_init*step.Dn_mini, tmax = dt, update_dt = True, ToleranceNR = 0.05, intervalOutput = 2.0*dt)
                
                #--------------- Post-Treatment -----------------------------------------------

                #Compute the mean stress and strain
                #Get the stress tensor (PG values)
                # TensorStrain = Assembly.GetAll()['Assembling'].GetStrainTensor(Problem.GetDoFSolution(), "GaussPoint")

                TensorStrain = material.GetStrain()
                TensorStress = material.GetPKII()
                
                # print(listBC)
                # print(step.mecas)
                # print(pb.GetA().shape)
                # print(TensorStrain)
                # print(TensorStress)
                # print(mesh.GetNodeCoordinates())
                      
                # Volume_mesh = Assembly.GetAll()['Assembling'].IntegrateField(np.ones_like(TensorStress[0])) #volume of domain without the void (hole)
                
                MeanStress = np.array([1/Volume*Assembly.GetAll()['Assembling'].IntegrateField(TensorStress[i]) for i in range(6)])
                
                MeanStrain = np.array([pb.GetDisp('DispX')[-2], pb.GetDisp('DispY')[-2], pb.GetDisp('DispZ')[-2],
                                       pb.GetDisp('DispX')[-1], pb.GetDisp('DispY')[-1], pb.GetDisp('DispZ')[-1]])
                
                Wm_mean = (1/Volume) * Assembly.GetAll()['Assembling'].IntegrateField(material.Wm)
                
                # Other method: only work if volume with no void (Void=0)
                # Void = Volume-Volume_mesh
                # MeanStrain = [1/Volume*Assembly.GetAll()['Assembling'].IntegrateField(TensorStrain[i]) for i in range(6)]
                
                print('Strain tensor ([Exx, Eyy, Ezz, Exy, Exz, Eyz]): ' )
                print(MeanStrain)
                print('Stress tensor ([Sxx, Syy, Szz, Sxy, Sxz, Syz]): ' )
                print(MeanStress)
    

