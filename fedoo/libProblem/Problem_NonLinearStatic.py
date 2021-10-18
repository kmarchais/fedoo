# import numpy as np
from fedoo.libAssembly.Assembly import Assembly
from fedoo.libProblem.Problem   import *
from fedoo.libProblem.ProblemPGD   import ProblemPGD

#dynamical inheritance. The class is generated inside a function
def _GenerateClass_NonLinearStatic(libBase):
    class __NonLinearStatic(libBase):
        
        def __init__(self, Assembling, ID):                                  
            #A = Assembling.GetMatrix() #tangent stiffness matrix
            A = 0 #tangent stiffness matrix - will be initialized only when required
            B = 0             
            #D = Assembling.GetVector() #initial stress vector
            D = 0 #initial stress vector #will be initialized later
            self.__Utot = 0 #displacement at the end of the previous converged increment
            self.__DU = 0 #displacement increment
            self.__Err0 = None #initial error for NR error estimation
            self.__ErrCriterion = 'Work' #Error criterion type   
            self.__Assembly = Assembling
            libBase.__init__(self,A,B,D,Assembling.GetMesh(), ID)        
            self.t0 = 0 ; self.tmax = 1
            self.__iter = 0
            self.__compteurOutput = 0
            
            self.intervalOutput = None #save results every self.intervalOutput iter or time step if self.__saveOutputAtExactTime = True
            self.__saveOutputAtExactTime = True
            self.err_num= 1e-8 #numerical error
        
        #Return the displacement components
        def GetDisp(self,name='Disp'):    
            if self.__DU is 0: return self._GetVectorComponent(self.__Utot, name)
            return self._GetVectorComponent(self.__Utot + self.__DU, name)    
        
        #Return the rotation components
        def GetRot(self,name='Rot'):    
            if self.__DU is 0: return self._GetVectorComponent(self.__Utot, name)
            return self._GetVectorComponent(self.__Utot + self.__DU, name)    
        
        #Return all the dof for every variable under a vector form
        def GetDoFSolution(self,name='all'):
            if self.__DU is 0: return self._GetVectorComponent(self.__Utot, name)
            return self._GetVectorComponent(self.__Utot + self.__DU, name)        
        
        def GetExternalForces(self, name = 'all'):
            return self._GetVectorComponent(-self.GetD(), name)        
        
        def UpdateA(self, dt = None):
            #dt not used for static problem
            self.SetA(self.__Assembly.GetMatrix())
        
        def UpdateD(self,dt=None, start=False):            
            #dt and start not used for static problem
            self.SetD(self.__Assembly.GetVector()) 
        
        def Initialize(self, initialTime=0.):   
            """
            """
            self.__Assembly.Initialize(self,initialTime)
            # self.SetA(self.__Assembly.GetMatrix())
            # self.SetD(self.__Assembly.GetVector())
        
        def ElasticPrediction(self, timeOld, dt):
            #update the boundary conditions with the time variation
            time = timeOld + dt
            timeFactor    = (time-self.t0)/(self.tmax-self.t0) #adimensional time            
            timeFactorOld = (timeOld-self.t0)/(self.tmax-self.t0)

            self.ApplyBoundaryCondition(timeFactor, timeFactorOld)
            
            #build and solve the linearized system with elastic rigidty matrix           
            self.UpdateA(dt) #should be the elastic rigidity matrix
            self.UpdateD(dt, start = True) #not modified in principle if dt is not modified, except the very first iteration. May be optimized by testing the change of dt
            self.Solve()        
            
            #the the increment Dirichlet boundray conditions to 0 (i.e. will not change during the NR interations)            
            try:
                self._Problem__Xbc *= 0 
            except:
                self._ProblemPGD__Xbc = 0

            #set the reference error to None to for a new estimation of err0            
            self.__Err0 = None

            #update displacement increment
            # if self.__TotalDisplacement is not 0: self.__TotalDisplacementOld = self.__TotalDisplacement.copy()
            # self.__TotalDisplacement += self.GetX()               
            self.__DU += self.GetX()
                
        def NewTimeIncrement(self,dt):
            #dt not used for static problem
            self.__Utot += self.__DU
            self.__DU = 0
            # self.__TotalDisplacementStart = self.__TotalDisplacement.copy()                       
            self.__Assembly.NewTimeIncrement()     

        def ResetTimeIncrement(self):   
            self.__DU = 0                           
            # self.__TotalDisplacement = self.__TotalDisplacementStart.copy()
            self.__Assembly.ResetTimeIncrement()
                              
        def NewtonRaphsonIncrement(self):                                      
            #solve and update total displacement. A and D should up to date
            self.Solve()
            self.__DU += self.GetX()
            # print(self.__DU)
        
        def Update(self, dtime=None, compute = 'all', updateWeakForm = True):   
            """
            Assemble the matrix including the following modification:
                - New initial Stress
                - New initial Displacement
                - Modification of the mesh
                - Change in constitutive law (internal variable)
            Don't Update the problem with the new assembled global matrix and global vector -> use UpdateA and UpdateD method for this purpose
            """
            if updateWeakForm == True:
                self.__Assembly.Update(self, dtime, compute)
            else: 
                self.__Assembly.ComputeGlobalMatrix(compute)

        def Reset(self):
            self.__Assembly.Reset()
            
            self.SetA(0) #tangent stiffness 
            self.SetD(0)                 
            # self.SetA(self.__Assembly.GetMatrix()) #tangent stiffness 
            # self.SetD(self.__Assembly.GetVector())            

            B = 0
            self.__Utot = 0
            self.__DU = 0
                        
            self.__Err0 = None #initial error for NR error estimation   
            self.t0 = 0 ; self.tmax = 1
            self.__iter = 0  
            self.ApplyBoundaryCondition() #perhaps not usefull here as the BC will be applied in the NewTimeIncrement method ?
        
        def ChangeAssembly(self,Assembling, update = True):
            """
            Modify the assembly associated to the problem and update the problem (see Assembly.Update for more information)
            """
            if isinstance(Assembling,str):
                Assembling = Assembly.GetAll()[Assembling]
                
            self.__Assembly = Assembling
            if update: self.Update()
            
        def NewtonRaphsonError(self):
            """
            Compute the error of the Newton-Raphson algorithm
            For Force and Work error criterion, the problem must be updated
            (Update method).
            """
            DofFree = self._Problem__DofFree
            if self.__Err0 is None:
                if self.__ErrCriterion == 'Displacement': 
                    self.__Err0 = np.max(np.abs((self.__Utot + self.__DU)[DofFree])) #Displacement criterion
                    # print(self.__Err0)
                else:
                    self.__Err0 = 1
                    self.__Err0 = self.NewtonRaphsonError() 
                return 1                
            else: 
                if self.__ErrCriterion == 'Displacement': 
                    return np.max(np.abs(self.GetX()))/self.__Err0  #Displacement criterion
                elif self.__ErrCriterion == 'Force': #Force criterion              
                    if self.GetD() is 0: return np.max(np.abs(self.GetB()[DofFree]))/self.__Err0 
                    else: return np.max(np.abs(self.GetB()[DofFree]+self.GetD()[DofFree]))/self.__Err0                     
                else: #self.__ErrCriterion == 'Work': #work criterion
                    if self.GetD() is 0: return np.max(np.abs(self.GetX()[DofFree]) * np.abs(self.GetB()[DofFree]))/self.__Err0 
                    else: return np.max(np.abs(self.GetX()[DofFree]) * np.abs(self.GetB()[DofFree]+self.GetD()[DofFree]))/self.__Err0 
       
        def SetNewtonRaphsonErrorCriterion(self, ErrorCriterion):
            if ErrorCriterion in ['Displacement', 'Force','Work']:
                self.__ErrCriterion = ErrorCriterion            
            else: 
                raise NameError('ErrCriterion must be set to "Displacement", "Force" or "Work"')
        
        # def GetElasticEnergy(self): #only work for classical FEM
        #     """
        #     returns : sum (0.5 * U.transposed * K * U)
        #     """
    
        #     return sum( 0.5*self.GetX().transpose() * self.GetA() * self.GetX() )

        # def GetNodalElasticEnergy(self):
        #     """
        #     returns : 0.5 * K * U . U
        #     """
    
        #     E = 0.5*self.GetX().transpose() * self.GetA() * self.GetX()

        #     E = np.reshape(E,(3,-1)).T

        #     return E                   
        
        def SolveTimeIncrement(self, timeOld, dt, max_subiter = 5, ToleranceNR = 5e-3):            
            
            # self.NewTimeIncrement(timeOld, dt)
            # self.__Err0 = 1
            
            self.ElasticPrediction(timeOld, dt)
            
            for subiter in range(max_subiter): #newton-raphson iterations
                #update Stress and initial displacement and Update stiffness matrix
                self.Update(dt, compute = 'vector') #update the out of balance force vector
                self.UpdateD(dt) #required to compute the NR error

                #Check convergence     
                normRes = self.NewtonRaphsonError()    

                # print('     Subiter {} - Time: {:.5f} - Err: {:.5f}'.format(subiter, timeOld+dt, normRes))

                if normRes < ToleranceNR:                                                  
                    return 1, subiter, normRes
                
                #--------------- Solve --------------------------------------------------------        
                # self.__Assembly.ComputeGlobalMatrix(compute = 'matrix')
                # self.SetA(self.__Assembly.GetMatrix())
                self.Update(dt, compute = 'matrix', updateWeakForm = False) #assemble the tangeant matrix
                self.UpdateA(dt)
                
                self.NewtonRaphsonIncrement()
                
            return 0, subiter, normRes


        def NLSolve(self, **kargs):              
            #parameters
            max_subiter = kargs.get('max_subiter',6)
            ToleranceNR = kargs.get('ToleranceNR',5e-3)
            self.t0 = kargs.get('t0',self.t0) #time at the start of the time step
            self.tmax = kargs.get('tmax',self.tmax) #time at the end of the time step
            dt = kargs.get('dt',0.1) #initial time step
            dt_min = kargs.get('dt_min',1e-6) #min time step
            
            self.__saveOutputAtExactTime = kargs.get('saveOutputAtExactTime',self.__saveOutputAtExactTime)
            intervalOutput = kargs.get('intervalOutput',self.intervalOutput) # time step for output if saveOutputAtExactTime == 'True' (default) or  number of iter increments between 2 output 
            update_dt = kargs.get('update_dt',True)
            outputFile = kargs.get('outputFile', None)
            
            if intervalOutput is None:
                if self.__saveOutputAtExactTime: intervalOutput = dt
                else: intervalOutput = 1
            
            if self.__saveOutputAtExactTime: next_time = self.t0 + intervalOutput
            else: next_time = self.tmax
            
            self.SetInitialBCToCurrent()            
                        
            time = self.t0                            
            
            if self.__Utot is 0:#Initialize only if 1st step
                self.Initialize(self.t0)
                            
            while time < self.tmax - self.err_num:
                timeOld = time
                time = time+dt                
                current_dt = dt 
                
                if time > next_time - self.err_num: 
                    time = next_time                 
                    current_dt = time-timeOld
                
                # print(self.__Assembly.GetWeakForm().GetConstitutiveLaw().GetPKII()[0][0]) #for debug purpose
                
                #self.SolveTimeIncrement = Newton Raphson loop
                convergence, nbNRiter, normRes = self.SolveTimeIncrement(timeOld, current_dt, max_subiter, ToleranceNR)

                if (convergence) :
                    print('Iter {} - Time: {:.5f} - dt {:.5f} - NR iter: {} - Err: {:.5f}'.format(self.__iter, time, dt, nbNRiter, normRes))
                                        
                    #Initialize the next increment                    
                    self.NewTimeIncrement(current_dt)
                    
                    #Output results
                    if outputFile is not None: outputFile(self, self.__iter, time, nbNRiter, normRes)                       
                    if (time == next_time) or (self.__saveOutputAtExactTime == False and self.__iter%self.intervalOutput == 0):
                        # self.__ProblemOutput.SaveResults(self, self.__compteurOutput)  
                        self.SaveResults(self.__compteurOutput)                              
                        self.__compteurOutput += 1     
                    
                    self.__iter += 1                    
                    if self.__saveOutputAtExactTime and time == next_time:
                        next_time = next_time + intervalOutput
                        if next_time > self.tmax - self.err_num: next_time = self.tmax
                    
                    #Check if dt can be increased
                    if update_dt and nbNRiter < 2: 
                        dt *= 1.25
                        # print('Increase the time increment to {:.5f}'.format(dt))
                        
                else:
                    if update_dt:
                        time = timeOld
                        dt *= 0.25                                     
                        print('NR failed to converge (err: {:.5f}) - reduce the time increment to {:.5f}'.format(normRes, dt ))
                        
                        if dt < dt_min: 
                            raise NameError('Current time step is inferior to the specified minimal time step (dt_min)')   
                            
                        #reset internal variables, update Stress, initial displacement and assemble global matrix at previous time                                      
                        self.ResetTimeIncrement()  
                        continue                    
                    else: 
                        raise NameError('Newton Raphson iteration has not converged (err: {:.5f})- Reduce the time step or use update_dt = True'.format(normRes))   
                                                                                        
    return __NonLinearStatic

def NonLinearStatic(Assembling, ID = "MainProblem"):
    if isinstance(Assembling,str):
        Assembling = Assembly.GetAll()[Assembling]
               
    if hasattr(Assembling.GetMesh(), 'GetListMesh'): libBase = ProblemPGD
    else: libBase = Problem            

    __NonLinearStatic = _GenerateClass_NonLinearStatic(libBase) 

    return __NonLinearStatic(Assembling, ID)
