#derive de ConstitutiveLaw
#This law should be used with an InternalForce WeakForm


from fedoo.libConstitutiveLaw.ConstitutiveLaw import Mechanical3D
from fedoo.libWeakForm.WeakForm_InternalForce import InternalForce
from fedoo.libAssembly.Assembly import Assembly
from fedoo.libProblem.Problem_NonLinearStatic import NonLinearStatic
from fedoo.libUtil.PostTreatement import listStressTensor, listStrainTensor
from fedoo.libHomogen.PeriodicBoundaryCondition import DefinePeriodicBoundaryCondition, DefinePeriodicBoundaryConditionNonPerioMesh
from fedoo.libHomogen.TangentStiffnessMatrix import GetTangentStiffness, GetHomogenizedStiffness
import numpy as np
import multiprocessing 

class FE2(Mechanical3D):
    """
    ConstitutiveLaw that solve a Finite Element Problem at each point of gauss
    in the contexte of the so called "FE²" method. 
    
    Parameters
    ----------
    assemb: Assembly or Assembly ID (str), or list of Assembly (with len(list) = number of integration points).
        Assembly that correspond to the microscopic problem
    ID: str, optional
        The ID of the constitutive law
    """
    def __init__(self, assemb, ID=""):
        #props is a nparray containing all the material variables
        #nstatev is a nparray containing all the material variables
        if isinstance(assemb, str): assemb = Assembly.GetAll()[assemb]
        Mechanical3D.__init__(self, ID) # heritage      
        
        if isinstance(assemb, list):
            self.__assembly = [Assembly.GetAll()[a] if isinstance(a,str) else a for a in assemb]
            self.__mesh = [a.GetMesh() for a in self.__assembly]
        else:
            self.__mesh = assemb.GetMesh()
            self.__assembly = assemb
            
        self.list_problem = None
                
        # self.__currentGradDisp = self.__initialGradDisp = 0        
            
    def GetPKII(self):
        return listStressTensor(self.__stress)
    
    # def GetKirchhoff(self):
    #     return listStressTensor(self.Kirchhoff.T)        
    
    # def GetCauchy(self):
    #     return listStressTensor(self.Cauchy.T)        
    
    def GetStrain(self, **kargs):
        return listStrainTensor(self.__strain)
           
    # def GetStatev(self):
    #     return self.statev.T

    def GetStress(self, **kargs): #same as GetPKII (used for small def)
        return listStressTensor(self.__stress)
    
    # def GetHelas (self):
    #     # if self.__L is None:                
    #     #     self.RunUmat(np.eye(3).T.reshape(1,3,3), np.eye(3).T.reshape(1,3,3), time=0., dtime=1.)

    #     return np.squeeze(self.L.transpose(1,2,0)) 
    
    def GetWm(self):
        return self.__Wm
    
    def GetCurrentGradDisp(self):
        if self.__currentGradDisp is 0: return 0
        else: return self.__currentGradDisp
        
    def GetTangentMatrix(self):
        
        H = np.squeeze(self.Lt.transpose(1,2,0))
        return H
        
    def NewTimeIncrement(self):
        # self.set_start() #in set_start -> set tangeant matrix to elastic
        
        #save variable at the begining of the Time increment
        self.__initialGradDisp = self.__currentGradDisp
        self.Lt = self.L.copy()

    
    def ResetTimeIncrement(self):
        # self.to_start()         
        self.__currentGradDisp = self.__initialGradDisp  
        self.Lt = self.L.copy()
    
    def Reset(self):
        """
        Reset the constitutive law (time history)
        """
        #a modifier
        self.__currentGradDisp = self.__initialGradDisp = 0
        # self.__Statev = None
        self.__currentStress = None #lissStressTensor object describing the last computed stress (GetStress method)
        # self.__currentGradDisp = 0
        # self.__F0 = None

    
    def Initialize(self, assembly, pb, initialTime = 0., nlgeom=False):  
        self.nlgeom = nlgeom            
        if self.list_problem is None:  #only initialize once
            nb_points = assembly.GetNumberOfGaussPoints() * assembly.GetMesh().n_elements
            
            #Definition of the set of nodes for boundary conditions
            if not(isinstance(self.__mesh, list)):            
                self.list_mesh = [self.__mesh for i in range(nb_points)]
                self.list_assembly = [self.__assembly.copy() for i in range(nb_points)]
            else: 
                self.list_mesh = self.__mesh
                self.list_assembly = self.__assembly
        
            self.list_problem = []
            self._list_volume = np.empty(nb_points)
            self._list_center = np.empty(nb_points, dtype=int)
            self.L = np.empty((nb_points,6,6))
                    
            print('-- Initialize micro problems --')
            for i in range(nb_points):
                print("\r", str(i+1),'/',str(nb_points), end="")
                
                crd = self.list_mesh[i].nodes
                type_el = self.list_mesh[i].elm_type
                xmax = np.max(crd[:,0]) ; xmin = np.min(crd[:,0])
                ymax = np.max(crd[:,1]) ; ymin = np.min(crd[:,1])
                zmax = np.max(crd[:,2]) ; zmin = np.min(crd[:,2])
                        
                crd_center = (np.array([xmin, ymin, zmin]) + np.array([xmax, ymax, zmax]))/2           
                self._list_volume[i] = (xmax-xmin)*(ymax-ymin)*(zmax-zmin) #total volume of the domain
        
                if '_StrainNodes' in self.list_mesh[i].ListSetOfNodes():
                    strain_nodes = self.list_mesh[i].node_sets['_StrainNodes']            
                else:
                    strain_nodes = self.list_mesh[i].add_nodes(crd_center,2) #add virtual nodes for macro strain
                    self.list_mesh[i].add_node_set(strain_nodes,'_StrainNodes')
               
                self._list_center[i] = np.linalg.norm(crd[:-2]-crd_center,axis=1).argmin()
                            # list_material.append(self.__constitutivelaw.copy())
                      
                #Type of problem
                self.list_problem.append(NonLinearStatic(self.list_assembly[i], ID = '_fe2_cell_'+str(i)))            
                pb_micro = self.list_problem[-1]
                meshperio = True
                
                #Shall add other conditions later on
                if meshperio:
                    DefinePeriodicBoundaryCondition(self.list_mesh[i],
                    [strain_nodes[0], strain_nodes[0], strain_nodes[0], strain_nodes[1], strain_nodes[1], strain_nodes[1]],
                    ['DispX',        'DispY',        'DispZ',       'DispX',         'DispY',        'DispZ'], dim='3D', ProblemID = '_fe2_cell_'+str(i))
                else:
                    DefinePeriodicBoundaryConditionNonPerioMesh(self.list_mesh[i],
                    [strain_nodes[0], strain_nodes[0], strain_nodes[0], strain_nodes[1], strain_nodes[1], strain_nodes[1]],
                    ['DispX',        'DispY',        'DispZ',       'DispX',         'DispY',        'DispZ'], dim='3D', ProblemID = '_fe2_cell_'+str(i))
                    
                pb_micro.BoundaryCondition('Dirichlet','DispX', 0, [self._list_center[i]])
                pb_micro.BoundaryCondition('Dirichlet','DispY', 0, [self._list_center[i]])
                pb_micro.BoundaryCondition('Dirichlet','DispZ', 0, [self._list_center[i]])
                
                self.L[i] = GetHomogenizedStiffness(self.list_assembly[i])
            
            pb.MakeActive()
            self.Lt = self.L.copy()
            
            self.__strain = np.zeros((6, nb_points))
            self.__stress = np.zeros((6, nb_points))
            self.__Wm = np.zeros((4, nb_points))
    
            print('')

    def _update_pb(self, id_pb):
        dtime = self.__dtime
        strain = self.__new_strain
        nb_points = len(self.list_problem)
        pb = self.list_problem[id_pb]

        print("\r", str(id_pb+1),'/',str(nb_points), end="")
        strain_nodes = self.list_mesh[id_pb].node_sets['_StrainNodes']  

        pb.RemoveBC("Strain")
        pb.BoundaryCondition('Dirichlet','DispX', strain[0][id_pb], [strain_nodes[0]], initialValue = self.__strain[0][id_pb], ID = 'Strain') #EpsXX
        pb.BoundaryCondition('Dirichlet','DispY', strain[1][id_pb], [strain_nodes[0]], initialValue = self.__strain[1][id_pb], ID = 'Strain') #EpsYY
        pb.BoundaryCondition('Dirichlet','DispZ', strain[2][id_pb], [strain_nodes[0]], initialValue = self.__strain[2][id_pb], ID = 'Strain') #EpsZZ
        pb.BoundaryCondition('Dirichlet','DispX', strain[3][id_pb], [strain_nodes[1]], initialValue = self.__strain[3][id_pb], ID = 'Strain') #EpsXY
        pb.BoundaryCondition('Dirichlet','DispY', strain[4][id_pb], [strain_nodes[1]], initialValue = self.__strain[4][id_pb], ID = 'Strain') #EpsXZ
        pb.BoundaryCondition('Dirichlet','DispZ', strain[5][id_pb], [strain_nodes[1]], initialValue = self.__strain[5][id_pb], ID = 'Strain') #EpsYZ
        
        
        pb.NLSolve(dt = dtime, tmax = dtime, update_dt = True, ToleranceNR = 0.05, print_info = 0)        
        
        self.Lt[id_pb]= GetTangentStiffness(pb.GetID())
        
        material = self.list_assembly[id_pb].GetWeakForm().GetConstitutiveLaw()
        stress_field = material.GetStress()
        self.__stress[:,id_pb] = np.array([1/self._list_volume[id_pb]*self.list_assembly[id_pb].IntegrateField(stress_field[i]) for i in range(6)])
    
        Wm_field = material.Wm
        self.__Wm[:,id_pb] = (1/self._list_volume[id_pb]) * self.list_assembly[id_pb].IntegrateField(Wm_field)


    def Update(self,assembly, pb, dtime):   
        displacement = pb.GetDoFSolution()

        if displacement is 0: 
            self.__currentGradDisp = 0
            self.__currentSigma = 0                        
        else:
            self.__currentGradDisp = assembly.GetGradTensor(displacement, "GaussPoint")

            grad_values = self.__currentGradDisp
            if self.nlgeom == False:
                strain  = [grad_values[i][i] for i in range(3)] 
                strain += [grad_values[0][1] + grad_values[1][0], grad_values[0][2] + grad_values[2][0], grad_values[1][2] + grad_values[2][1]]
            else:            
                strain  = [grad_values[i][i] + 0.5*sum([grad_values[k][i]**2 for k in range(3)]) for i in range(3)] 
                strain += [grad_values[0][1] + grad_values[1][0] + sum([grad_values[k][0]*grad_values[k][1] for k in range(3)])] 
                strain += [grad_values[0][2] + grad_values[2][0] + sum([grad_values[k][0]*grad_values[k][2] for k in range(3)])]
                strain += [grad_values[1][2] + grad_values[2][1] + sum([grad_values[k][1]*grad_values[k][2] for k in range(3)])]

        #resolution of the micro problem at each gauss points
        self.__new_strain = strain
        self.__dtime = dtime
        nb_points = len(self.list_problem)
        self.__stress = np.empty((6,nb_points))
        self.__Wm = np.empty((4,nb_points))
        
        print('-- Update micro cells --')
        
        # with multiprocessing.Pool(4) as pool:
        #     pool.map(self._update_pb, range(nb_points))
            
        for id_pb in range(nb_points):
            self._update_pb(id_pb)

        self.__strain = strain
        # self.__strain = listStrainTensor(strain)
        # self.__stress = listStressTensor([stress[i] for i in range(6)])        
        # self.__Wm = Wm
        
        print('')

       
            # H = self.GetH()
        
            # self.__currentSigma = listStressTensor([sum([TotalStrain[j]*assembly.ConvertData(H[i][j]) for j in range(6)]) for i in range(6)]) #H[i][j] are converted to gauss point excepted if scalar

        

        # self.Run(dtime)

        # (DRloc , listDR, Detot, statev) = self.Run(dtime)
