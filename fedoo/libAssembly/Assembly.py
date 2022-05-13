#simcoon compatible

from fedoo.libAssembly.AssemblyBase import AssemblyBase, AssemblySum
from fedoo.libUtil.PostTreatement import listStressTensor, listStrainTensor
from fedoo.libMesh.Mesh import Mesh
from fedoo.libElement import *
from fedoo.libWeakForm.WeakForm import WeakForm
from fedoo.libConstitutiveLaw.ConstitutiveLaw import ConstitutiveLaw
from fedoo.libAssembly.SparseMatrix import _BlocSparse as BlocSparse
from fedoo.libAssembly.SparseMatrix import _BlocSparseOld as BlocSparseOld #required for 'old' computeMatrixMehtod
from fedoo.libAssembly.SparseMatrix import RowBlocMatrix

from scipy import sparse
import numpy as np
from numbers import Number 
import time

def Create(weakForm, mesh="", elementType="", ID="", **kargs): 
    if isinstance(weakForm, str):
        weakForm = WeakForm.GetAll()[weakForm]
        
    if hasattr(weakForm, 'list_weakform') and weakForm.assembly_options is None: #WeakFormSum object
        list_weakform = weakForm.list_weakform
        
        if isinstance(mesh, str): mesh = Mesh.GetAll()[mesh]
        if elementType == "": elementType = mesh.GetElementShape()
                
        #get lists of some non compatible assembly_options items for each weakform in list_weakform
        list_nb_pg = [wf.assembly_options.get('nb_pg', GetDefaultNbPG(elementType, mesh)) for wf in list_weakform]
        list_assume_sym = [wf.assembly_options.get('assume_sym', False) for wf in list_weakform]
        list_prop = list(zip(list_nb_pg, list_assume_sym))
        list_diff_prop = list(set(list_prop)) #list of different non compatible properties that required separated assembly
        
        if len(list_diff_prop) == 1: #only 1 assembly is required
            #update assembly_options
            prop = list_diff_prop[0]
            weakForm.assembly_options = {'nb_pg': prop[0] , 'assume_sym': prop[1]}
            weakForm.assembly_options['mat_lumping'] = [wf.assembly_options.get('mat_lumping',False) for wf in weakForm.list_weakform]
            return Assembly(weakForm, mesh, elementType, ID, **kargs)
        
        else: #we need to create and sum several assemblies
            list_assembly = []
            for prop in list_diff_prop:
                l_wf = [list_weakform[i] for i,p in enumerate(list_prop) if p == prop] #list_weakform with compatible properties
                if len(l_wf) == 1:
                    wf = l_wf[0] #standard weakform. No WeakFormSum required
                else:
                    #create a new WeakFormSum object
                    wf = WeakFormSum(l_wf) #to modify : add automatic ID
                    #define the assembly_options dict of the new weakform
                    wf.assembly_options = {'nb_pg': prop[0] , 'assume_sym': prop[1]}
                    wf.assembly_options['assume_sym'] = [w.assembly_options['assume_sym'] for w in l_wf]
                list_assembly.append(Assembly(wf, mesh, elementType, "", **kargs))
        
        # list_assembly = [Assembly(wf, mesh, elementType, "", **kargs) for wf in weakForm.list_weakform]
        kargs['assembly_output'] = kargs.get('assembly_output', list_assembly[0])
        return AssemblySum(list_assembly, ID, **kargs)       
    
    return Assembly(weakForm, mesh, elementType, ID, **kargs)
               
class Assembly(AssemblyBase):
    __saveOperator = {} 
    __saveMatrixChangeOfBasis = {}   
    __saveMatGaussianQuadrature = {} 
    __saveNodeToPGMatrix = {}
    __savePGtoNodeMatrix = {}
    __associatedVariables = {} #dict containing all associated variables (rotational dof for C1 elements) for elementType
           
    def __init__(self,weakForm, mesh="", elementType="", ID="", **kargs):                      
        
        if isinstance(weakForm, str):
            weakForm = WeakForm.GetAll()[weakForm]
        
        if weakForm.assembly_options is None:
            #should be a non compatible WeakFormSum object
            raise NameError('Some Assembly associated to WeakFormSum object can only be created using the Create function')

        if isinstance(mesh, str):
            mesh = Mesh.GetAll()[mesh]
            
        if isinstance(weakForm, WeakForm):
            self._weakForm = weakForm
            AssemblyBase.__init__(self, ID, weakForm.space)
        else: #weakForm should be a ModelingSpace object
            assert hasattr(weakForm, 'list_variable') and hasattr(weakForm, 'list_coordinate'),\
                'WeakForm not understood'
            self._weakForm = None
            AssemblyBase.__init__(self, ID, space = weakForm)
        
        self.__MeshChange = kargs.pop('MeshChange', False)        
        self.__Mesh = mesh   
        if elementType == "": elementType = mesh.GetElementShape()
        self.__elmType= elementType #.lower()
        self.__TypeOfCoordinateSystem = self._GetTypeOfCoordinateSystem()

        self.__nb_pg = kargs.pop('nb_pg', None)
        if self.__nb_pg is None: 
            self.__nb_pg = weakForm.assembly_options.get('nb_pg', GetDefaultNbPG(elementType, mesh))
        
        self.assume_sym = weakForm.assembly_options.get('assume_sym', False)
        self.mat_lumping = weakForm.assembly_options.get('mat_lumping', False)
        
        self.__saveBlocStructure = None #use to save data about the sparse structure and avoid time consuming recomputation
        #print('Finite element operator for Assembly "' + ID + '" built in ' + str(time.time()-t0) + ' seconds')        
        self.computeMatrixMethod = 'new' #computeMatrixMethod = 'old' and 'very_old' only used for debug purpose        
        self.__factorizeOp = True #option for debug purpose (should be set to True for performance)
        


    def ComputeGlobalMatrix(self, compute = 'all'):
        """
        Compute the global matrix and global vector related to the assembly
        if compute = 'all', compute the global matrix and vector
        if compute = 'matrix', compute only the matrix
        if compute = 'vector', compute only the vector
        if compute = 'none', compute nothing
        """                        
        if compute == 'none': return
        
        # t0 = time.time()

        computeMatrixMethod = self.computeMatrixMethod
        
        nb_pg = self.__nb_pg
        mesh = self.__Mesh        
        
        if self.__MeshChange == True:             
            if mesh in Assembly.__saveMatrixChangeOfBasis: del Assembly.__saveMatrixChangeOfBasis[mesh]            
            self.PreComputeElementaryOperators()
                 
        nvar = self.space.nvar
        wf = self._weakForm.GetDifferentialOperator(mesh)      
        
        MatGaussianQuadrature = self._GetGaussianQuadratureMatrix()        
        MatrixChangeOfBasis = self.GetMatrixChangeOfBasis()        
        associatedVariables = self._GetAssociatedVariables() #for element requiring many variable such as beam with disp and rot dof        

        if computeMatrixMethod == 'new': 
            
            intRef, sorted_indices = wf.sort()
            #sl contains list of slice object that contains the dimension for each variable
            #size of VV and sl must be redefined for case with change of basis
            VV = 0
            nbNodes = self.__Mesh.GetNumberOfNodes()            
            sl = [slice(i*nbNodes, (i+1)*nbNodes) for i in range(nvar)] 
            
            if nb_pg == 0: #if finite difference elements, don't use BlocSparse                              
                blocks = [[None for i in range(nvar)] for j in range(nvar)]
                self.__saveBlocStructure = 0 #don't save block structure for finite difference mesh
                    
                Matvir = self._GetElementaryOp(wf.op_vir[0], nb_pg=0)[0].T #should be identity matrix restricted to nodes used in the finite difference mesh
                
                for ii in range(len(wf.op)):
                    if compute == 'matrix' and wf.op[ii] is 1: continue
                    if compute == 'vector' and wf.op[ii] is not 1: continue
                
                    if ii > 0 and intRef[ii] == intRef[ii-1]: #if same operator as previous with different coef, add the two coef
                        coef_PG += wf.coef[ii]
                    else: coef_PG = wf.coef[ii]   #coef_PG = nodal values (finite diffirences)
                    
                    if ii < len(wf.op)-1 and intRef[ii] == intRef[ii+1]: #if operator similar to the next, continue 
                        continue
                                                    
                    var_vir = wf.op_vir[ii].u
                    assert wf.op_vir[ii].ordre == 0, "This weak form is not compatible with finite difference mesh"
                    
                    if wf.op[ii] == 1: #only virtual operator -> compute a vector which is the nodal values
                        if VV is 0: VV = np.zeros((self.__Mesh.GetNumberOfNodes() * nvar))
                        VV[sl[var_vir[i]]] = VV[sl[var_vir[i]]] - (coef_PG) 
                            
                    else: #virtual and real operators -> compute a matrix
                        var = wf.op[ii].u   
                        if isinstance(coef_PG, Number): coef_PG = coef_PG * np.ones_like(MatGaussianQuadrature.data)
                        CoefMatrix = sparse.csr_matrix( (coef_PG, MatGaussianQuadrature.indices, MatGaussianQuadrature.indptr), shape = MatGaussianQuadrature.shape)   
                        Mat    =  self._GetElementaryOp(wf.op[ii])[0]
                        
                        if blocks[var_vir][var] is None: 
                            blocks[var_vir][var] = Matvir @ CoefMatrix @ Mat
                        else:                    
                            blocks[var_vir][var].data += (Matvir @ CoefMatrix @ Mat).data
                            
                blocks = [[b if b is not None else sparse.csr_matrix((nbNodes,nbNodes)) \
                          for b in blocks_row] for blocks_row in blocks ]        
                MM = sparse.bmat(blocks, format ='csr')
                
            else:
                MM = BlocSparse(nvar, nvar, self.__nb_pg, self.__saveBlocStructure, assume_sym = self.assume_sym)
                listMatvir = listCoef_PG = None
                                  
                if hasattr(self._weakForm, '_list_mat_lumping'):
                    change_mat_lumping = True  #use different mat_lumping option for each operator                             
                else:
                    change_mat_lumping = False
                    mat_lumping = self.mat_lumping                

                for ii in range(len(wf.op)):                                        
                        
                    if compute == 'matrix' and wf.op[ii] is 1: continue
                    if compute == 'vector' and wf.op[ii] is not 1: continue
                    
                    if wf.op[ii] is not 1 and self.assume_sym and wf.op[ii].u < wf.op_vir[ii].u:
                        continue                
                    
                    if change_mat_lumping:
                        mat_lumping = self._weakForm._list_mat_lumping[sorted_indices[ii]]                        
                    
                    if isinstance(wf.coef[ii], Number) or len(wf.coef[ii])==1: 
                        #if nb_pg == 0, coef_PG = nodal values (finite diffirences)
                        coef_PG = wf.coef[ii] 
                    else:
                        coef_PG = self._ConvertToGaussPoints(wf.coef[ii][:])                                                 
                    
                    if ii > 0 and intRef[ii] == intRef[ii-1]: #if same operator as previous with different coef, add the two coef
                        coef_PG_sum += coef_PG
                    else: coef_PG_sum = coef_PG   
                    
                    if ii < len(wf.op)-1 and intRef[ii] == intRef[ii+1]: #if operator similar to the next, continue 
                        continue
                                    
                    coef_PG = coef_PG_sum * MatGaussianQuadrature.data #MatGaussianQuadrature.data is the diagonal of MatGaussianQuadrature
                                              
    #                Matvir = (RowBlocMatrix(self._GetElementaryOp(wf.op_vir[ii]), nvar, var_vir, coef_vir) * MatrixChangeOfBasis).T
                    #check how it appens with change of variable and rotation dof
                    
                    Matvir = self._GetElementaryOp(wf.op_vir[ii])
                    
                    if listMatvir is not None: #factorization of real operator (sum of virtual operators)
                        listMatvir = [listMatvir[j]+[Matvir[j]] for j in range(len(Matvir))] 
                        listCoef_PG = listCoef_PG + [coef_PG]  
                        
                    if ii < len(wf.op)-1 and wf.op[ii] != 1 and wf.op[ii+1] != 1 and self.__factorizeOp == True:
                        #if it possible, factorization of op to increase assembly performance (sum of several op_vir)                        
                        factWithNextOp = [wf.op[ii].u, wf.op[ii].x, wf.op[ii].ordre, wf.op_vir[ii].u] == [wf.op[ii+1].u, wf.op[ii+1].x, wf.op[ii+1].ordre, wf.op_vir[ii+1].u] #True if factorization is possible with next op                                            
                        if factWithNextOp:
                            if listMatvir is None: 
                                listMatvir = [[Matvir[j]] for j in range(len(Matvir))] #initialization of listMatvir and listCoef_PG
                                listCoef_PG = [coef_PG]
                            continue #si factorization possible -> go to next op, all the factorizable operators will treat together                        
                    else: factWithNextOp = False

                    coef_vir = [1] ; var_vir = [wf.op_vir[ii].u] #list in case there is an angular variable                                                   
                    if var_vir[0] in associatedVariables:
                        var_vir.extend(associatedVariables[var_vir[0]][0])
                        coef_vir.extend(associatedVariables[var_vir[0]][1])   
                    
                    if wf.op[ii] == 1: #only virtual operator -> compute a vector 
                        if VV is 0: VV = np.zeros((self.__Mesh.GetNumberOfNodes() * nvar))
                        for i in range(len(Matvir)):
                            VV[sl[var_vir[i]]] = VV[sl[var_vir[i]]] - coef_vir[i] * Matvir[i].T * (coef_PG) #this line may be optimized
                            
                    else: #virtual and real operators -> compute a matrix                                         
                        coef = [1] ; var = [wf.op[ii].u] #list in case there is an angular variable                
                        if var[0] in associatedVariables:
                            var.extend(associatedVariables[var[0]][0])
                            coef.extend(associatedVariables[var[0]][1])                                             
    
    #                    Mat    =  RowBlocMatrix(self._GetElementaryOp(wf.op[ii]), nvar, var, coef)         * MatrixChangeOfBasis             
                        Mat    =  self._GetElementaryOp(wf.op[ii])
        
                        #Possibility to increase performance for multivariable case 
                        #the structure should be the same for derivative dof, so the blocs could be computed altogether
                        if listMatvir is None:
                            for i in range(len(Mat)):
                                for j in range(len(Matvir)):
                                    MM.addToBlocATB(Matvir[j], Mat[i], (coef[i]*coef_vir[j]) * coef_PG, var_vir[j], var[i], mat_lumping)
                        else:
                            for i in range(len(Mat)):
                                for j in range(len(Matvir)):
                                    MM.addToBlocATB(listMatvir[j], Mat[i], [(coef[i]*coef_vir[j]) * coef_PG for coef_PG in listCoef_PG], var_vir[j], var[i], mat_lumping)                        
                            listMatvir = None
                            listCoef_PG = None
                        
            if compute != 'vector':
                if MatrixChangeOfBasis is 1: 
                    self.SetMatrix(MM.tocsr()) #format csr         
                else: 
                    self.SetMatrix(MatrixChangeOfBasis.T * MM.tocsr() * MatrixChangeOfBasis) #format csr         
            if compute != 'matrix': 
                if VV is 0: self.SetVector(0)
                elif MatrixChangeOfBasis is 1: self.SetVector(VV) #numpy array
                else: self.SetVector(MatrixChangeOfBasis.T * VV)                     
                        
            if self.__saveBlocStructure is None: self.__saveBlocStructure = MM.GetBlocStructure()        

        elif computeMatrixMethod == 'old': #keep a lot in memory, not very efficient in a memory point of view. May be slightly more rapid in some cases                            
        
            intRef = wf.sort() #intRef = list of integer for compareason (same int = same operator with different coef)            
            
            if (mesh, self.__elmType, nb_pg) not in Assembly.__saveOperator:
                Assembly.__saveOperator[(mesh, self.__elmType, nb_pg)] = {}
            saveOperator = Assembly.__saveOperator[(mesh, self.__elmType, nb_pg)]
            
            #list_elementType contains the id of the element associated with every variable
            #list_elementType could be stored to avoid reevaluation 
            if isinstance(eval(self.__elmType), dict):
                elementDict = eval(self.__elmType)
                list_elementType = [elementDict.get(self.space.variable_name(i))[0] for i in range(nvar)]
                list_elementType = [elementDict.get('__default') if elmtype is None else elmtype for elmtype in list_elementType]
            else: list_elementType = [self.__elmType for i in range(nvar)]
            
            if 'blocShape' not in saveOperator:
                saveOperator['blocShape'] = saveOperator['colBlocSparse'] = saveOperator['rowBlocSparse'] = None
            
            #MM not used if only compute vector
            MM = BlocSparseOld(nvar, nvar)
            MM.col = saveOperator['colBlocSparse'] #col indices for bloc to build coo matrix with BlocSparse
            MM.row = saveOperator['rowBlocSparse'] #row indices for bloc to build coo matrix with BlocSparse
            MM.blocShape = saveOperator['blocShape'] #shape of one bloc in BlocSparse
            
            #sl contains list of slice object that contains the dimension for each variable
            #size of VV and sl must be redefined for case with change of basis
            VV = 0
            nbNodes = self.__Mesh.GetNumberOfNodes()            
            sl = [slice(i*nbNodes, (i+1)*nbNodes) for i in range(nvar)] 
            
            for ii in range(len(wf.op)):                   
                if compute == 'matrix' and wf.op[ii] is 1: continue
                if compute == 'vector' and wf.op[ii] is not 1: continue
            
                if isinstance(wf.coef[ii], Number) or len(wf.coef[ii])==1: 
                    coef_PG = wf.coef[ii] #MatGaussianQuadrature.data is the diagonal of MatGaussianQuadrature
                else:
                    coef_PG = self._ConvertToGaussPoints(wf.coef[ii][:])                                                 
                
                if ii > 0 and intRef[ii] == intRef[ii-1]: #if same operator as previous with different coef, add the two coef
                    coef_PG_sum += coef_PG
                else: coef_PG_sum = coef_PG   
                
                if ii < len(wf.op)-1 and intRef[ii] == intRef[ii+1]: #if operator similar to the next, continue 
                    continue
                
                coef_PG = coef_PG_sum * MatGaussianQuadrature.data 
                            
                coef_vir = [1] ; var_vir = [wf.op_vir[ii].u] #list in case there is an angular variable
                               
                if var_vir[0] in associatedVariables:
                    var_vir.extend(associatedVariables[var_vir[0]][0])
                    coef_vir.extend(associatedVariables[var_vir[0]][1])         
                                                 
                if wf.op[ii] == 1: #only virtual operator -> compute a vector 
                                            
                    Matvir = self._GetElementaryOp(wf.op_vir[ii])         
                    if VV is 0: VV = np.zeros((self.__Mesh.GetNumberOfNodes() * nvar))
                    for i in range(len(Matvir)):
                        VV[sl[var_vir[i]]] = VV[sl[var_vir[i]]] - coef_vir[i] * Matvir[i].T * (coef_PG) #this line may be optimized
                        
                else: #virtual and real operators -> compute a matrix
                    coef = [1] ; var = [wf.op[ii].u] #list in case there is an angular variable                
                    if var[0] in associatedVariables:
                        var.extend(associatedVariables[var[0]][0])
                        coef.extend(associatedVariables[var[0]][1])                                                                                     
                    
                    tupleID = (list_elementType[wf.op_vir[ii].u], wf.op_vir[ii].x, wf.op_vir[ii].ordre, list_elementType[wf.op[ii].u], wf.op[ii].x, wf.op[ii].ordre) #tuple to identify operator
                    if tupleID in saveOperator:
                        MatvirT_Mat = saveOperator[tupleID] #MatvirT_Mat is an array that contains usefull data to build the matrix MatvirT*Matcoef*Mat where Matcoef is a diag coefficient matrix. MatvirT_Mat is build with BlocSparse class
                    else: 
                        MatvirT_Mat = None
                        saveOperator[tupleID] = [[None for i in range(len(var))] for j in range(len(var_vir))]
                        Matvir = self._GetElementaryOp(wf.op_vir[ii])         
                        Mat = self._GetElementaryOp(wf.op[ii])

                    for i in range(len(var)):
                        for j in range(len(var_vir)):
                            if MatvirT_Mat is not None:           
                                MM.addToBloc(MatvirT_Mat[j][i], (coef[i]*coef_vir[j]) * coef_PG, var_vir[j], var[i])                                     
                            else:  
                                saveOperator[tupleID][j][i] = MM.addToBlocATB(Matvir[j], Mat[i], (coef[i]*coef_vir[j]) * coef_PG, var_vir[j], var[i])
                                if saveOperator['colBlocSparse'] is None: 
                                    saveOperator['colBlocSparse'] = MM.col
                                    saveOperator['rowBlocSparse'] = MM.row
                                    saveOperator['blocShape'] = MM.blocShape
                               
            if compute != 'vector': 
                if MatrixChangeOfBasis is 1: 
                    self.SetMatrix(MM.toCSR()) #format csr         
                else: 
                    self.SetMatrix(MatrixChangeOfBasis.T * MM.toCSR() * MatrixChangeOfBasis) #format csr         
            if compute != 'matrix': 
                if VV is 0: self.SetVector(0)
                elif MatrixChangeOfBasis is 1: self.SetVector(VV) #numpy array
                else: self.SetVector(MatrixChangeOfBasis.T * VV)         
        
        
        elif computeMatrixMethod == 'very_old':
            MM = 0
            VV = 0
            
            for ii in range(len(wf.op)):
                if compute == 'matrix' and wf.op[ii] is 1: continue
                if compute == 'vector' and wf.op[ii] is not 1: continue
            
                coef_vir = [1] ; var_vir = [wf.op_vir[ii].u] #list in case there is an angular variable      
                if var_vir[0] in associatedVariables:
                    var_vir.extend(associatedVariables[var_vir[0]][0])
                    coef_vir.extend(associatedVariables[var_vir[0]][1])     
                     
                Matvir = (RowBlocMatrix(self._GetElementaryOp(wf.op_vir[ii]), nvar, var_vir, coef_vir) * MatrixChangeOfBasis).T
    
                if wf.op[ii] == 1: #only virtual operator -> compute a vector 
                    if isinstance(wf.coef[ii], Number): 
                        VV = VV - wf.coef[ii]*Matvir * MatGaussianQuadrature.data
                    else:
                        coef_PG = self._ConvertToGaussPoints(wf.coef[ii][:])*MatGaussianQuadrature.data                             
                        VV = VV - Matvir * (coef_PG)
                        
                else: #virtual and real operators -> compute a matrix
                    coef = [1] ; var = [wf.op[ii].u] #list in case there is an angular variable                  
                    if var[0] in associatedVariables:
                        var.extend(associatedVariables[var[0]][0])
                        coef.extend(associatedVariables[var[0]][1])     
                                    
                    Mat    =  RowBlocMatrix(self._GetElementaryOp(wf.op[ii]), nvar, var, coef)         * MatrixChangeOfBasis             
    
                    if isinstance(wf.coef[ii], Number): #and self.op_vir[ii] != 1: 
                        MM = MM + wf.coef[ii]*Matvir * MatGaussianQuadrature * Mat  
                    else:
                        coef_PG = self._ConvertToGaussPoints(wf.coef[ii][:])                    
                        CoefMatrix = sparse.csr_matrix( (MatGaussianQuadrature.data*coef_PG, MatGaussianQuadrature.indices, MatGaussianQuadrature.indptr), shape = MatGaussianQuadrature.shape)   
                        MM = MM + Matvir * CoefMatrix * Mat                

#            MM = MM.tocsr()
#            MM.eliminate_zeros()
            if compute != 'vector': self.SetMatrix(MM) #format csr         
            if compute != 'matrix': self.SetVector(VV) #numpy array
            
        # print('temps : ', print(compute), ' - ', time.time()- t0)
    
    def SetMesh(self, mesh):
        self.__Mesh = mesh

    def GetMesh(self):
        return self.__Mesh
    
    def GetWeakForm(self):
        return self._weakForm
           
    def GetNumberOfGaussPoints(self):
        return self.__nb_pg
    
    def GetMatrixChangeOfBasis(self):
        if self.__TypeOfCoordinateSystem == 'global': return 1
        
        mesh = self.__Mesh
        if mesh not in Assembly.__saveMatrixChangeOfBasis:        
            ### change of basis treatment for beam or plate elements
            ### Compute the change of basis matrix for vector defined in self.space.list_vector()
            MatrixChangeOfBasis = 1
            computeMatrixChangeOfBasis = False

            Nnd = mesh.GetNumberOfNodes()
            Nel = mesh.GetNumberOfElements()
            elm = mesh.GetElementTable()
            nNd_elm = np.shape(elm)[1]            
            crd = mesh.GetNodeCoordinates()
            dim = self.space.ndim
            localFrame = mesh.GetLocalFrame()
            elmRefGeom = eval(mesh.GetElementShape())(mesh=mesh)
    #        xi_nd = elmRefGeom.xi_nd
            xi_nd = GetNodePositionInElementCoordinates(mesh.GetElementShape(), nNd_elm) #function to define

            if 'X' in mesh.GetCoordinateID() and 'Y' in mesh.GetCoordinateID(): #if not in physical space, no change of variable                
                for nameVector in self.space.list_vector():
                    if computeMatrixChangeOfBasis == False:
                        range_nNd_elm = np.arange(nNd_elm) 
                        computeMatrixChangeOfBasis = True
                        nvar = self.space.nvar
                        listGlobalVector = []  ; listScalarVariable = list(range(nvar))
#                        MatrixChangeOfBasis = sparse.lil_matrix((nvar*Nel*nNd_elm, nvar*Nnd)) #lil is very slow because it change the sparcity of the structure
                    listGlobalVector.append(self.space.get_vector(nameVector)) #vector that need to be change in local coordinate            
                    listScalarVariable = [i for i in listScalarVariable if not(i in listGlobalVector[-1])] #scalar variable that doesnt need to be converted
                #Data to build MatrixChangeOfBasis with coo sparse format
                if computeMatrixChangeOfBasis:
                    rowMCB = np.empty((len(listGlobalVector)*Nel, nNd_elm, dim,dim))
                    colMCB = np.empty((len(listGlobalVector)*Nel, nNd_elm, dim,dim))
                    dataMCB = np.empty((len(listGlobalVector)*Nel, nNd_elm, dim,dim))
                    LocalFrameEl = elmRefGeom.GetLocalFrame(crd[elm], xi_nd, localFrame) #array of shape (Nel, nb_nd, nb of vectors in basis = dim, dim)
                    for ivec, vec in enumerate(listGlobalVector):
                        # dataMCB[ivec*Nel:(ivec+1)*Nel] = LocalFrameEl[:,:,:dim,:dim]                  
                        dataMCB[ivec*Nel:(ivec+1)*Nel] = LocalFrameEl                  
                        rowMCB[ivec*Nel:(ivec+1)*Nel] = np.arange(Nel).reshape(-1,1,1,1) + range_nNd_elm.reshape(1,-1,1,1)*Nel + np.array(vec).reshape(1,1,-1,1)*(Nel*nNd_elm)
                        colMCB[ivec*Nel:(ivec+1)*Nel] = elm.reshape(Nel,nNd_elm,1,1) + np.array(vec).reshape(1,1,1,-1)*Nnd        
    
                    if len(listScalarVariable) > 0:
                        #add the component from scalar variables (ie variable not requiring a change of basis)
                        dataMCB = np.hstack( (dataMCB.reshape(-1), np.ones(len(listScalarVariable)*Nel*nNd_elm) )) #no change of variable so only one value adding in dataMCB

                        rowMCB_loc = np.empty((len(listScalarVariable)*Nel, nNd_elm))
                        colMCB_loc = np.empty((len(listScalarVariable)*Nel, nNd_elm))
                        for ivar, var in enumerate(listScalarVariable):
                            rowMCB_loc[ivar*Nel:(ivar+1)*Nel] = np.arange(Nel).reshape(-1,1) + range_nNd_elm.reshape(1,-1)*Nel + var*(Nel*nNd_elm)
                            colMCB_loc[ivar*Nel:(ivar+1)*Nel] = elm + var*Nnd        
                        
                        rowMCB = np.hstack( (rowMCB.reshape(-1), rowMCB_loc.reshape(-1)))
                        colMCB = np.hstack( (colMCB.reshape(-1), colMCB_loc.reshape(-1)))
                        
                        MatrixChangeOfBasis = sparse.coo_matrix((dataMCB,(rowMCB,colMCB)), shape=(Nel*nNd_elm*nvar, Nnd*nvar))                   
                    else:
                        MatrixChangeOfBasis = sparse.coo_matrix((dataMCB.reshape(-1),(rowMCB.reshape(-1),colMCB.reshape(-1))), shape=(Nel*nNd_elm*nvar, Nnd*nvar))
                    
                    MatrixChangeOfBasis = MatrixChangeOfBasis.tocsr()                     
            
            Assembly.__saveMatrixChangeOfBasis[mesh] = MatrixChangeOfBasis   
            return MatrixChangeOfBasis

        return Assembly.__saveMatrixChangeOfBasis[mesh]


    # def InitializeConstitutiveLaw(self, assembly, pb, initialTime=0.):
    #     if hasattr(self,'nlgeom'): nlgeom = self.nlgeom
    #     else: nlgeom=False
    #     constitutivelaw = self.GetConstitutiveLaw()
        
    #     if constitutivelaw is not None:
    #         if isinstance(constitutivelaw, list):
    #             for cl in constitutivelaw:
    #                 cl.Initialize(assembly, pb, initialTime, nlgeom)
    #         else:
    #             constitutivelaw.Initialize(assembly, pb, initialTime, nlgeom)
 
    def Initialize(self, pb, initialTime=0.):
        """
        Initialize the associated weak form and assemble the global matrix with the elastic matrix
        Parameters: 
            - initialTime: the initial time        
        """        
        if self._weakForm.GetConstitutiveLaw() is not None:
            if hasattr(self._weakForm,'nlgeom'): nlgeom = self._weakForm.nlgeom
            else: nlgeom=False
            self._weakForm.GetConstitutiveLaw().Initialize(self, pb, initialTime, nlgeom)
        
        self._weakForm.Initialize(self, pb, initialTime)
                
    def InitTimeIncrement(self, pb, dtime):
        self._weakForm.InitTimeIncrement(self, pb, dtime)
        self.ComputeGlobalMatrix() 
        #no need to compute vector if the previous iteration has converged and (dtime hasn't changed or dtime isn't used in the weakform)
        #in those cases, self.ComputeGlobalMatrix(compute = 'matrix') should be more efficient

    def Update(self, pb, dtime=None, compute = 'all'):
        """
        Update the associated weak form and assemble the global matrix
        Parameters: 
            - pb: a Problem object containing the Dof values
            - time: the current time        
        """
        if self._weakForm.GetConstitutiveLaw() is not None:
            self._weakForm.GetConstitutiveLaw().Update(self, pb, dtime)
        self._weakForm.Update(self, pb, dtime)
        self.ComputeGlobalMatrix(compute)

    def ResetTimeIncrement(self):
        """
        Reset the current time increment (internal variable in the constitutive equation)
        Doesn't assemble the new global matrix. Use the Update method for that purpose.
        """
        if self._weakForm.GetConstitutiveLaw() is not None:
            self._weakForm.GetConstitutiveLaw().ResetTimeIncrement()
        self._weakForm.ResetTimeIncrement()
        # self.ComputeGlobalMatrix(compute='all')

    def NewTimeIncrement(self):
        """
        Apply the modification to the constitutive equation required at each change of time increment. 
        Generally used to increase non reversible internal variable
        Doesn't assemble the new global matrix. Use the Update method for that purpose.
        """
        if self._weakForm.GetConstitutiveLaw() is not None:
            self._weakForm.GetConstitutiveLaw().NewTimeIncrement()
        self._weakForm.NewTimeIncrement() #should update GetH() method to return elastic rigidity matrix for prediction        
        # self.ComputeGlobalMatrix(compute='matrix')
 
    def Reset(self):
        """
        Reset the assembly to it's initial state.
        Internal variable in the constitutive equation are reinitialized 
        and stored global matrix and vector are deleted
        """
        if self._weakForm.GetConstitutiveLaw() is not None:
            self._weakForm.GetConstitutiveLaw().Reset()
        self._weakForm.Reset()    
        self.deleteGlobalMatrix()

    @staticmethod
    def DeleteMemory():
        """
        Static method of the Assembly class. 
        Erase all the static variables of the Assembly object. 
        Stored data, are data that are used to compute the global assembly in an
        efficient way. 
        However, the stored data may cause errors if the mesh is modified. In this case, the data should be recomputed, 
        but it is not done by default. In this case, deleting the memory should 
        resolve the problem. 
        
        -----------
        Remark : it the MeshChange argument is set to True when creating the Assembly object, the
        memory will be recomputed by default, which may cause a decrease in assembling performances
        """
        Assembly.__saveOperator = {} 
        Assembly.__saveMatrixChangeOfBasis = {}   
        Assembly.__saveMatGaussianQuadrature = {} 
        Assembly.__saveNodeToPGMatrix = {}
        Assembly.__savePGtoNodeMatrix = {}
        Assembly.__associatedVariables = {} #dict containing all associated variables (rotational dof for C1 elements) for elementType
        
        
    def PreComputeElementaryOperators(self,nb_pg = None): #Précalcul des opérateurs dérivés suivant toutes les directions (optimise les calculs en minimisant le nombre de boucle)               
        #-------------------------------------------------------------------
        #Initialisation   
        #-------------------------------------------------------------------
        mesh = self.__Mesh
        elementType = self.__elmType
        if nb_pg is None: NumberOfGaussPoint = self.__nb_pg
        else: NumberOfGaussPoint = nb_pg
                  
        Nnd = mesh.GetNumberOfNodes()
        Nel = mesh.GetNumberOfElements()
        elm = mesh.GetElementTable()
        nNd_elm = np.shape(elm)[1]
        crd = mesh.GetNodeCoordinates()
        
        #-------------------------------------------------------------------
        #Case of finite difference mesh    
        #-------------------------------------------------------------------        
        if NumberOfGaussPoint == 0: # in this case, it is a finite difference mesh
            # we compute the operators directly from the element library
            elmRef = eval(elementType)(NumberOfGaussPoint)
            OP = elmRef.computeOperator(crd,elm)
            Assembly.__saveMatGaussianQuadrature[(mesh,NumberOfGaussPoint)] = sparse.identity(OP[0][0].shape[0], 'd', format= 'csr') #No gaussian quadrature in this case : nodal identity matrix
            Assembly.__savePGtoNodeMatrix[(mesh, NumberOfGaussPoint)] = 1  #no need to translate between pg and nodes because no pg 
            Assembly.__saveNodeToPGMatrix[(mesh, NumberOfGaussPoint)] = 1                                    
            Assembly.__saveMatrixChangeOfBasis[mesh] = 1 # No change of basis:  MatrixChangeOfBasis = 1 #this line could be deleted because the coordinate should in principle defined as 'global' 
            Assembly.__saveOperator[(mesh,elementType,NumberOfGaussPoint)] = OP #elmRef.computeOperator(crd,elm)
            return                                

        #-------------------------------------------------------------------
        #Initialise the geometrical interpolation
        #-------------------------------------------------------------------   
        elmRefGeom = eval(mesh.GetElementShape())(NumberOfGaussPoint, mesh=mesh) #initialise element
        nNd_elm_geom = len(elmRefGeom.xi_nd) #number of dof used in the geometrical interpolation
        elm_geom = elm[:,:nNd_elm_geom] 

        localFrame = mesh.GetLocalFrame()
        nb_elm_nd = np.bincount(elm_geom.reshape(-1)) #len(nb_elm_nd) = Nnd #number of element connected to each node        
        vec_xi = elmRefGeom.xi_pg #coordinate of points of gauss in element coordinate (xi)
        
        elmRefGeom.ComputeJacobianMatrix(crd[elm_geom], vec_xi, localFrame) #compute elmRefGeom.JacobianMatrix, elmRefGeom.detJ and elmRefGeom.inverseJacobian

        #-------------------------------------------------------------------
        # Compute the diag matrix used for the gaussian quadrature
        #-------------------------------------------------------------------  
        gaussianQuadrature = (elmRefGeom.detJ * elmRefGeom.w_pg).T.reshape(-1) 
        Assembly.__saveMatGaussianQuadrature[(mesh,NumberOfGaussPoint)] = sparse.diags(gaussianQuadrature, 0, format='csr') #matrix to get the gaussian quadrature (integration over each element)        

        #-------------------------------------------------------------------
        # Compute the array containing row and col indices used to assemble the sparse matrices
        #-------------------------------------------------------------------          
        range_nbPG = np.arange(NumberOfGaussPoint)                 
        if self.GetMatrixChangeOfBasis() is 1: ChangeOfBasis = False
        else: 
            ChangeOfBasis = True
            range_nNd_elm = np.arange(nNd_elm)
        
        row = np.empty((Nel, NumberOfGaussPoint, nNd_elm)) ; col = np.empty((Nel, NumberOfGaussPoint, nNd_elm))                
        row[:] = np.arange(Nel).reshape((-1,1,1)) + range_nbPG.reshape(1,-1,1)*Nel 
        col[:] = elm.reshape((Nel,1,nNd_elm))
        #row_geom/col_geom: row and col indices using only the dof used in the geometrical interpolation (col = col_geom if geometrical and variable interpolation are the same)
        row_geom = np.reshape(row[...,:nNd_elm_geom], -1) ; col_geom = np.reshape(col[...,:nNd_elm_geom], -1)
        
        if ChangeOfBasis: 
            col = np.empty((Nel, NumberOfGaussPoint, nNd_elm))
            col[:] = np.arange(Nel).reshape((-1,1,1)) + range_nNd_elm.reshape((1,1,-1))*Nel 
            Ncol = Nel * nNd_elm
        else: 
            Ncol = Nnd                      
        row = np.reshape(row,-1) ; col = np.reshape(col,-1)  

        #-------------------------------------------------------------------
        # Assemble the matrix that compute the node values from pg based on the geometrical shape functions (no angular dof for ex)    
        #-------------------------------------------------------------------                                
        PGtoNode = np.linalg.pinv(elmRefGeom.ShapeFunctionPG) #pseudo-inverse of NodeToPG
        dataPGtoNode = PGtoNode.T.reshape((1,NumberOfGaussPoint,nNd_elm_geom))/nb_elm_nd[elm_geom].reshape((Nel,1,nNd_elm_geom)) #shape = (Nel, NumberOfGaussPoint, nNd_elm)   
        Assembly.__savePGtoNodeMatrix[(mesh, NumberOfGaussPoint)] = sparse.coo_matrix((dataPGtoNode.reshape(-1),(col_geom,row_geom)), shape=(Nnd,Nel*NumberOfGaussPoint) ).tocsr() #matrix to compute the node values from pg using the geometrical shape functions 

        #-------------------------------------------------------------------
        # Assemble the matrix that compute the pg values from nodes using the geometrical shape functions (no angular dof for ex)    
        #-------------------------------------------------------------------             
        dataNodeToPG = np.empty((Nel, NumberOfGaussPoint, nNd_elm_geom))
        dataNodeToPG[:] = elmRefGeom.ShapeFunctionPG.reshape((1,NumberOfGaussPoint,nNd_elm_geom)) 
        Assembly.__saveNodeToPGMatrix[(mesh, NumberOfGaussPoint)] = sparse.coo_matrix((np.reshape(dataNodeToPG,-1),(row_geom,col_geom)), shape=(Nel*NumberOfGaussPoint, Nnd) ).tocsr() #matrix to compute the pg values from nodes using the geometrical shape functions (no angular dof)

        #-------------------------------------------------------------------
        # Build the list of elementType to assemble (some beam element required several elementType in function of the variable)
        #-------------------------------------------------------------------        
        objElement = eval(elementType)
        if isinstance(objElement, dict):
            listElementType = set([objElement[key][0] for key in objElement.keys() if key[:2]!='__' or key == '__default'])               
        else: 
            listElementType =  [elementType]
        
        #-------------------------------------------------------------------
        # Assembly of the elementary operators for each elementType 
        #-------------------------------------------------------------------      
        for elementType in listElementType: 
            elmRef = eval(elementType)(NumberOfGaussPoint, mesh = mesh, elmGeom = elmRefGeom)
            nb_dir_deriv = 0
            if hasattr(elmRef,'ShapeFunctionDerivativePG'):
                derivativePG = elmRefGeom.inverseJacobian @ elmRef.ShapeFunctionDerivativePG #derivativePG = np.matmul(elmRefGeom.inverseJacobian , elmRef.ShapeFunctionDerivativePG)
                nb_dir_deriv = derivativePG.shape[-2] 
            nop = nb_dir_deriv+1 #nombre d'opérateur à discrétiser
    
            NbDoFperNode = np.shape(elmRef.ShapeFunctionPG)[-1]//nNd_elm
            
            data = [[np.empty((Nel, NumberOfGaussPoint, nNd_elm)) for j in range(NbDoFperNode)] for i in range(nop)] 
    
            for j in range(0,NbDoFperNode):
                data[0][j][:] = elmRef.ShapeFunctionPG[...,j*nNd_elm:(j+1)*nNd_elm].reshape((-1,NumberOfGaussPoint,nNd_elm)) #same as dataNodeToPG matrix if geometrical shape function are the same as interpolation functions
                for dir_deriv in range(nb_dir_deriv):
                    data[dir_deriv+1][j][:] = derivativePG[...,dir_deriv, j*nNd_elm:(j+1)*nNd_elm]
                        
            op_dd = [ [sparse.coo_matrix((data[i][j].reshape(-1),(row,col)), shape=(Nel*NumberOfGaussPoint , Ncol) ).tocsr() for j in range(NbDoFperNode) ] for i in range(nop)]        
                
            data = {0: op_dd[0]} #data is a dictionnary
            for i in range(nb_dir_deriv): 
                data[1, i] = op_dd[i+1]

            Assembly.__saveOperator[(mesh,elementType,NumberOfGaussPoint)] = data   
    
    def _GetElementaryOp(self, deriv, nb_pg=None): 
        #Gives a list of sparse matrix that convert node values for one variable to the pg values of a simple derivative op (for instance d/dz)
        #The list contains several element if the elementType include several variable (dof variable in beam element). In other case, the list contains only one matrix
        #The variables are not considered. For a global use, the resulting matrix should be assembled in a block matrix with the nodes values for all variables
        if nb_pg is None: nb_pg = self.__nb_pg

        elementType = self.__elmType
        mesh = self.__Mesh
        
        if isinstance(eval(elementType), dict):
            elementDict = eval(elementType)
            elementType = elementDict.get(self.space.variable_name(deriv.u))
            if elementType is None: elementType = elementDict.get('__default')
            elementType = elementType[0]
            
        if not((mesh,elementType,nb_pg) in Assembly.__saveOperator):
            self.PreComputeElementaryOperators(nb_pg)
        
        data = Assembly.__saveOperator[(mesh,elementType,nb_pg)]

        if deriv.ordre == 0 and 0 in data:
            return data[0]
        
        #extract the mesh coordinate that corespond to coordinate rank given in deriv.x     
        ListMeshCoordinateIDRank = [self.space.coordinate_rank(crdID) for crdID in mesh.GetCoordinateID() if crdID in self.space.list_coordinate()]
        if deriv.x in ListMeshCoordinateIDRank: xx= ListMeshCoordinateIDRank.index(deriv.x)
        else: return data[0] #if the coordinate doesnt exist, return operator without derivation (for PGD)
                         
        if (deriv.ordre, xx) in data:
            return data[deriv.ordre, xx]
        else: assert 0, "Operator unavailable"      
              

    def _GetGaussianQuadratureMatrix(self): #calcul la discrétision relative à un seul opérateur dérivé   
        mesh = self.__Mesh
        nb_pg = self.__nb_pg
        if not((mesh,nb_pg) in Assembly.__saveMatGaussianQuadrature):
            self.PreComputeElementaryOperators()
        return Assembly.__saveMatGaussianQuadrature[(mesh,nb_pg)]

    def _GetAssociatedVariables(self): #associated variables (rotational dof for C1 elements) of elementType        
        elementType = self.__elmType
        if elementType not in Assembly.__associatedVariables:
            objElement = eval(elementType)
            if isinstance(objElement, dict):            
                Assembly.__associatedVariables[elementType] = {self.space.variable_rank(key): 
                                       [[self.space.variable_rank(v) for v in val[1][1::2]],
                                        val[1][0::2]] for key,val in objElement.items() if len(val)>1 and key in self.space.list_variable()} 
                    # val[1][0::2]] for key,val in objElement.items() if key in self.space.list_variable() and len(val)>1}
            else: Assembly.__associatedVariables[elementType] = {}
        return Assembly.__associatedVariables[elementType] 

    def _GetTypeOfCoordinateSystem(self): 
        #determine the type of coordinate system used for vector of variables (displacement for instance). This type may be specified in element (under dict form only)        
        #TypeOfCoordinateSystem may be 'local' or 'global'. If 'local' variables are used, a change of variable is required
        #If TypeOfCoordinateSystemis not specified in the element, 'global' value (no change of basis) is considered by default
        if isinstance(eval(self.__elmType), dict):
            return eval(self.__elmType).get('__TypeOfCoordinateSystem', 'global')                
        else: 
            return 'global'
    
    def _GetGaussianPointToNodeMatrix(self, nb_pg=None): #calcul la discrétision relative à un seul opérateur dérivé   
        if nb_pg is None: nb_pg = self.__nb_pg     
        if not((self.__Mesh,nb_pg) in Assembly.__savePGtoNodeMatrix):
            self.PreComputeElementaryOperators(nb_pg)        
        return Assembly.__savePGtoNodeMatrix[(self.__Mesh,nb_pg)]
    
    def __GetNodeToGaussianPointMatrix(self, nb_pg=None): #calcul la discrétision relative à un seul opérateur dérivé   
        if nb_pg is None: nb_pg = self.__nb_pg     
        if not((self.__Mesh,nb_pg) in Assembly.__saveNodeToPGMatrix):
            Assembly.PreComputeElementaryOperators(nb_pg)
        
        return Assembly.__saveNodeToPGMatrix[(self.__Mesh,nb_pg)]
    
    def _ConvertToGaussPoints(self, data, nb_pg=None):         
        """
        Convert an array of values related to a specific mesh (Nodal values, Element Values or Points of Gauss values) to the gauss points
        mesh: the considered Mesh object
        data: array containing the values (nodal or element value)
        The shape of the array is tested.
        """               
        if nb_pg is None: nb_pg = self.__nb_pg            
        dataType = DetermineDataType(data, self.__Mesh, nb_pg)       

        if dataType == 'Node': 
            return self.__GetNodeToGaussianPointMatrix(nb_pg) * data
        if dataType == 'Element':
            if len(np.shape(data)) == 1: return np.tile(data.copy(),nb_pg)
            else: return np.tile(data.copy(),[nb_pg,1])            
        return data #in case data contains already PG values
                
    def GetElementResult(self, operator, U):
        """
        Return some element results based on the finite element discretization of 
        a differential operator on a mesh being given the dof results and the type of elements.
        
        Parameters
        ----------
        mesh: string or Mesh 
            If mesh is a string, it should be a meshID.
            Define the mesh to get the results from
            
        operator: OpDiff
            Differential operator defining the required results
         
        U: numpy.ndarray
            Vector containing all the DoF solution 
            
        Return: numpy.ndarray
            A Vector containing the values on each element. 
            It is computed using an arithmetic mean of the values from gauss points
            The vector lenght is the number of element in the mesh              
        """
                
        res = self.GetGaussPointResult(operator, U)
        NumberOfGaussPoint = res.shape[0]//self.__Mesh.GetNumberOfElements()
        return np.reshape(res, (NumberOfGaussPoint,-1)).sum(0) / NumberOfGaussPoint

    def GetGaussPointResult(self, operator, U, nb_pg = None):
        """
        Return some results at element Gauss points based on the finite element discretization of 
        a differential operator on a mesh being given the dof results and the type of elements.
        
        Parameters
        ----------           
        operator: OpDiff
            Differential operator defining the required results
         
        U: numpy.ndarray
            Vector containing all the DoF solution 
            
        Return: numpy.ndarray
            A Vector containing the values on each point of gauss for each element. 
            The vector lenght is the number of element time the number of Gauss points per element
        """
        
        #TODO : can be accelerated by avoiding RowBlocMatrix (need to be checked) -> For each elementary 
        # 1 - at the very begining, compute Uloc = MatrixChangeOfBasis * U 
        # 2 - reshape Uloc to separate each var Uloc = Uloc.reshape(var, -1)
        # 3 - in the loop : res += coef_PG * (Assembly._GetElementaryOp(mesh, operator.op[ii], elementType, nb_pg) , nvar, var, coef) * Uloc[var]
        
        res = 0
        nvar = self.space.nvar
        
        mesh = self.__Mesh 
        elementType = self.__elmType
        if nb_pg is None: nb_pg = self.__nb_pg
        
        MatrixChangeOfBasis = self.GetMatrixChangeOfBasis()
        associatedVariables = self._GetAssociatedVariables()    
        
        for ii in range(len(operator.op)):
            var = [operator.op[ii].u] ; coef = [1] 
            
            if var[0] in associatedVariables:
                var.extend(associatedVariables[var[0]][0])
                coef.extend(associatedVariables[var[0]][1])     
    
            assert operator.op_vir[ii]==1, "Operator virtual are only required to build FE operators, but not to get element results"

            if isinstance(operator.coef[ii], Number): coef_PG = operator.coef[ii]                 
            else: coef_PG = Assembly._ConvertToGaussPoints(mesh, operator.coef[ii][:], elementType, nb_pg)

            res += coef_PG * (RowBlocMatrix(self._GetElementaryOp(operator.op[ii], nb_pg) , nvar, var, coef) * MatrixChangeOfBasis * U)
        
        return res
        

    def GetNodeResult(self, operator, U):
        """
        Not a Static Method.

        Return some node results based on the finite element discretization of 
        a differential operator on a mesh being given the dof results and the type of elements.
        
        Parameters
        ----------
        operator: OpDiff
            Differential operator defining the required results
         
        U: numpy.ndarray
            Vector containing all the DoF solution         
            
        Return: numpy.ndarray            
            A Vector containing the values on each node. 
            An interpolation is used to get the node values from the gauss point values on each element. 
            After that, an arithmetic mean is used to compute a single node value from all adjacent elements.
            The vector lenght is the number of nodes in the mesh  
        """
        
        GaussianPointToNodeMatrix = self._GetGaussianPointToNodeMatrix()
        res = self.GetGaussPointResult(operator, U)
        return GaussianPointToNodeMatrix * res        
                
    def ConvertData(self, data, convertFrom=None, convertTo='GaussPoint'):
        
        if isinstance(data, Number): return data
        
        nb_pg = self.__nb_pg        
        
        if isinstance(data, (listStrainTensor, listStressTensor)):        
            try:
                return type(data)(self.ConvertData(data.asarray().T, convertFrom, convertTo).T)
            except:
                NotImplemented
        
        if convertFrom is None: convertFrom = DetermineDataType(data, self.__Mesh, nb_pg)
            
        assert (convertFrom in ['Node','GaussPoint','Element']) and (convertTo in ['Node','GaussPoint','Element']), "only possible to convert 'Node', 'Element' and 'GaussPoint' values"
        
        if convertFrom == convertTo: return data       
        if convertFrom == 'Node': 
            data = self.__GetNodeToGaussianPointMatrix() * data
        elif convertFrom == 'Element':             
            if len(np.shape(data)) == 1: data = np.tile(data.copy(),nb_pg)
            else: data = np.tile(data.copy(),[nb_pg,1])
            
        # from here data should be defined at 'PG'
        if convertTo == 'Node': 
            return self._GetGaussianPointToNodeMatrix() * data 
        elif convertTo == 'Element': 
            return np.sum(np.split(data, nb_pg),axis=0) / nb_pg
        else: return data 
        
            
    def IntegrateField(self, Field, TypeField = 'GaussPoint'):
        assert TypeField in ['Node','GaussPoint','Element'], "TypeField should be 'Node', 'Element' or 'GaussPoint' values"
        Field = self.ConvertData(Field, TypeField, 'GaussPoint')
        return sum(self._GetGaussianQuadratureMatrix()@Field)

    # def GetStressTensor(self, U, constitutiveLaw, Type="Nodal"):
    #     """
    #     Not a static method.
    #     Return the Stress Tensor of an assembly using the Voigt notation as a python list. 
    #     The total displacement field and a ConstitutiveLaw have to be given.
        
    #     Can only be used for linear constitutive law. 
    #     For non linear ones, use the GetStress method of the ConstitutiveLaw object.

    #     Options : 
    #     - Type :"Nodal", "Element" or "GaussPoint" integration (default : "Nodal")

    #     See GetNodeResult, GetElementResult and GetGaussPointResult.

    #     example : 
    #     S = SpecificAssembly.GetStressTensor(Problem.Problem.GetDoFSolution('all'), SpecificConstitutiveLaw)
    #     """
    #     if isinstance(constitutiveLaw, str):
    #         constitutiveLaw = ConstitutiveLaw.GetAll()[constitutiveLaw]

    #     if Type == "Nodal":
    #         return listStressTensor([self.GetNodeResult(e, U) if e!=0 else np.zeros(self.__Mesh.GetNumberOfNodes()) for e in constitutiveLaw.GetStressOperator()])
        
    #     elif Type == "Element":
    #         return listStressTensor([self.GetElementResult(e, U) if e!=0 else np.zeros(self.__Mesh.GetNumberOfElements()) for e in constitutiveLaw.GetStressOperator()])
        
    #     elif Type == "GaussPoint":
    #         NumberOfGaussPointValues = self.__Mesh.GetNumberOfElements() * self.__nb_pg #Assembly.__saveOperator[(self.__Mesh, self.__elmType, self.__nb_pg)][0].shape[0]
    #         return listStressTensor([self.GetGaussPointResult(e, U) if e!=0 else np.zeros(NumberOfGaussPointValues) for e in constitutiveLaw.GetStressOperator()])
        
    #     else:
    #         assert 0, "Wrong argument for Type: use 'Nodal', 'Element', or 'GaussPoint'"
        
        
    def GetStrainTensor(self, U, Type="Nodal", nlgeom = None):
        """
        Not a static method.
        Return the Green Lagrange Strain Tensor of an assembly using the Voigt notation as a python list. 
        The total displacement field has to be given.
        see GetNodeResults and GetElementResults

        Options : 
        - Type :"Nodal", "Element" or "GaussPoint" integration (default : "Nodal")
        - nlgeom = True or False if the strain tensor account for geometrical non-linearities
        if nlgeom = False, the Strain Tensor is assumed linear (default : True)

        example : 
        S = SpecificAssembly.GetStrainTensor(Problem.Problem.GetDoFSolution('all'))
        """        

        if nlgeom is None: 
            if hasattr(self._weakForm, 'nlgeom'): nlgeom = self._weakForm.nlgeom
            else: nlgeom = False
            
        GradValues = self.GetGradTensor(U, Type)
        
        if nlgeom == False:
            Strain  = [GradValues[i][i] for i in range(3)] 
            Strain += [GradValues[0][1] + GradValues[1][0], GradValues[0][2] + GradValues[2][0], GradValues[1][2] + GradValues[2][1]]
        else:            
            Strain  = [GradValues[i][i] + 0.5*sum([GradValues[k][i]**2 for k in range(3)]) for i in range(3)] 
            Strain += [GradValues[0][1] + GradValues[1][0] + sum([GradValues[k][0]*GradValues[k][1] for k in range(3)])]             
            Strain += [GradValues[0][2] + GradValues[2][0] + sum([GradValues[k][0]*GradValues[k][2] for k in range(3)])]
            Strain += [GradValues[1][2] + GradValues[2][1] + sum([GradValues[k][1]*GradValues[k][2] for k in range(3)])]
        
        return listStrainTensor(Strain)
    
    def GetGradTensor(self, U, Type = "Nodal"):
        """
        Return the Gradient Tensor of a vector (generally displacement given by Problem.GetDofSolution('all')
        as a list of list of numpy array
        The total displacement field U has to be given as a flatten numpy array
        see GetNodeResults and GetElementResults

        Options : 
        - Type :"Nodal", "Element" or "GaussPoint" integration (default : "Nodal")
        """        
        grad_operator = self.space.op_grad_u()        

        if Type == "Nodal":
            return [ [self.GetNodeResult(op, U) if op != 0 else np.zeros(self.__Mesh.GetNumberOfNodes()) for op in line_op] for line_op in grad_operator]
            
        elif Type == "Element":
            return [ [self.GetElementResult(op, U) if op!=0 else np.zeros(self.__Mesh.GetNumberOfElements()) for op in line_op] for line_op in grad_operator]        
        
        elif Type == "GaussPoint":
            NumberOfGaussPointValues = self.__nb_pg * self.__Mesh.GetNumberOfElements() #Assembly.__saveMatGaussianQuadrature[(self.__Mesh, self.__nb_pg)].shape[0]
            return [ [self.GetGaussPointResult(op, U) if op!=0 else np.zeros(NumberOfGaussPointValues) for op in line_op] for line_op in grad_operator]        
        else:
            assert 0, "Wrong argument for Type: use 'Nodal', 'Element', or 'GaussPoint'"

    def GetExternalForces(self, U, nvar=None):
        """
        Not a static method.
        Return the nodal Forces and moments in global coordinates related to a specific assembly considering the DOF solution given in U
        The resulting forces are the sum of :
        - External forces (associated to Neumann boundary conditions)
        - Nodal reaction (associated to Dirichelet boundary conditions)
        - Inertia forces 
        
        Return an array whose columns are Fx, Fy, Fz, Mx, My and Mz.         
                    
        example : 
        S = SpecificAssembly.GetNodalForces(Problem.Problem.GetDoFSolution('all'))

        an optionnal parameter is allowed to have extenal forces for other types of simulation with no beams !
        """
        if nvar is None: nvar = self.space.nvar
        return np.reshape(self.GetMatrix() * U - self.GetVector(), (nvar,-1)).T                        
#        return np.reshape(self.GetMatrix() * U, (Nvar,-1)).T                        

        

#    def GetInternalForces(self, U, CoordinateSystem = 'global'): 
#        """
#        Not a static method.
#        Only available for 2 nodes beam element
#        Return the element internal Forces and moments related to a specific assembly considering the DOF solution given in U.
#        Return array whose columns are Fx, Fy, Fz, Mx, My and Mz. 
#        
#        Parameter: if CoordinateSystem == 'local' the result is given in the local coordinate system
#                   if CoordinateSystem == 'global' the result is given in the global coordinate system (default)
#        """
#        
##        operator = self._weakForm.GetDifferentialOperator(self.__Mesh)
#        operator = self._weakForm.GetGeneralizedStress()
#        res = [self.GetElementResult(operator[i], U) for i in range(5)]
#        return res
#        

                 
        
#        res = np.reshape(res,(6,-1)).T
#        Nel = mesh.GetNumberOfElements()
#        res = (res[Nel:,:]-res[0:Nel:,:])/2
#        res = res[:, [self.space.variable_rank('DispX'), self.space.variable_rank('DispY'), self.space.variable_rank('DispZ'), \
#                              self.space.variable_rank('ThetaX'), self.space.variable_rank('ThetaY'), self.space.variable_rank('ThetaZ')]]         
#        
#        if CoordinateSystem == 'local': return res
#        elif CoordinateSystem == 'global': 
#            #require a transformation between local and global coordinates on element
#            #classical MatrixChangeOfBasis transform only toward nodal values
#            elmRef = eval(self.__Mesh.GetElementShape())(1, mesh=mesh)#one pg  with the geometrical element
#            vec = [0,1,2] ; dim = 3
#       
#            #Data to build MatrixChangeOfBasisElement with coo sparse format
#            crd = mesh.GetNodeCoordinates() ; elm = mesh.GetElementTable()
#            rowMCB = np.empty((Nel, 1, dim,dim))
#            colMCB = np.empty((Nel, 1, dim,dim))            
#            rowMCB[:] = np.arange(Nel).reshape(-1,1,1,1) + np.array(vec).reshape(1,1,-1,1)*Nel # [[id_el + var*Nel] for var in vec]    
#            colMCB[:] = np.arange(Nel).reshape(-1,1,1,1) + np.array(vec).reshape(1,1,1,-1)*Nel # [id_el+Nel*var for var in vec]
#            dataMCB = elmRef.GetLocalFrame(crd[elm], elmRef.xi_pg, mesh.GetLocalFrame()) #array of shape (Nel, nb_pg=1, nb of vectors in basis = dim, dim)                        
#
#            MatrixChangeOfBasisElement = sparse.coo_matrix((np.reshape(dataMCB,-1),(np.reshape(rowMCB,-1),np.reshape(colMCB,-1))), shape=(dim*Nel, dim*Nel)).tocsr()
#            
#            F = np.reshape( MatrixChangeOfBasisElement.T * np.reshape(res[:,0:3].T, -1)  ,  (3,-1) ).T
#            C = np.reshape( MatrixChangeOfBasisElement.T * np.reshape(res[:,3:6].T, -1)  ,  (3,-1) ).T
#            return np.hstack((F,C))            

    def GetInternalForces(self, U, CoordinateSystem = 'global'): 
        """
        Not a static method.
        Only available for 2 nodes beam element
        Return the element internal Forces and moments related to a specific assembly considering the DOF solution given in U.
        Return array whose columns are Fx, Fy, Fz, Mx, My and Mz. 
        
        Parameter: if CoordinateSystem == 'local' the result is given in the local coordinate system
                   if CoordinateSystem == 'global' the result is given in the global coordinate system (default)
        """
        
        operator = self._weakForm.GetDifferentialOperator(self.__Mesh)
        mesh = self.__Mesh
        nvar = self.space.nvar
        dim = self.space.ndim
        MatrixChangeOfBasis = self.GetMatrixChangeOfBasis()

        MatGaussianQuadrature = self._GetGaussianQuadratureMatrix()
        associatedVariables = self._GetAssociatedVariables()
        
        #TODO: use the computeGlobalMatrix() method to compute sum(operator.coef[ii]*Matvir * MatGaussianQuadrature * Mat)
        #add options in computeGlobalMatrix() to (i): dont save the computed matrix, (ii): neglect the ChangeOfBasis Matrix
        res = 0        
        for ii in range(len(operator.op)):
            var = [operator.op[ii].u] ; coef = [1]
            var_vir = [operator.op_vir[ii].u] ; coef_vir = [1]

            if var[0] in associatedVariables:
                var.extend(associatedVariables[var[0]][0])
                coef.extend(associatedVariables[var[0]][1])     
            if var_vir[0] in associatedVariables:
                var_vir.extend(associatedVariables[var_vir[0]][0])
                coef_vir.extend(associatedVariables[var_vir[0]][1])             

            Mat    =  RowBlocMatrix(self._GetElementaryOp(operator.op[ii]), nvar, var, coef)        
            Matvir =  RowBlocMatrix(self._GetElementaryOp(operator.op_vir[ii]), nvar, var_vir, coef_vir).T 

            if isinstance(operator.coef[ii], Number): #and self.op_vir[ii] != 1: 
                res = res + operator.coef[ii]*Matvir * MatGaussianQuadrature * Mat * MatrixChangeOfBasis * U   
            else:
                return NotImplemented                      
        
        res = np.reshape(res,(nvar,-1)).T
        
        Nel = mesh.GetNumberOfElements()
        res = (res[Nel:2*Nel,:]-res[0:Nel:,:])/2
        
        # if dim == 3:
        #     res = res[:, [self.space.variable_rank('DispX'), self.space.variable_rank('DispY'), self.space.variable_rank('DispZ'), \
        #                   self.space.variable_rank('RotX'), self.space.variable_rank('RotY'), self.space.variable_rank('RotZ')]]   
        # else: 
        #     res = res[:, [self.space.variable_rank('DispX'), self.space.variable_rank('DispY'), self.space.variable_rank('RotZ')]]   
        
        if CoordinateSystem == 'local': return res
        elif CoordinateSystem == 'global': 
            #require a transformation between local and global coordinates on element
            #classical MatrixChangeOfBasis transform only toward nodal values
            elmRef = eval(self.__Mesh.GetElementShape())(1, mesh=mesh)#one pg  with the geometrical element            
            if dim == 3: vec = [0,1,2] 
            else: vec = [0,1]
       
            #Data to build MatrixChangeOfBasisElement with coo sparse format
            crd = mesh.GetNodeCoordinates() ; elm = mesh.GetElementTable()
            rowMCB = np.empty((Nel, 1, dim,dim))
            colMCB = np.empty((Nel, 1, dim,dim))            
            rowMCB[:] = np.arange(Nel).reshape(-1,1,1,1) + np.array(vec).reshape(1,1,-1,1)*Nel # [[id_el + var*Nel] for var in vec]    
            colMCB[:] = np.arange(Nel).reshape(-1,1,1,1) + np.array(vec).reshape(1,1,1,-1)*Nel # [id_el+Nel*var for var in vec]
            dataMCB = elmRef.GetLocalFrame(crd[elm], elmRef.xi_pg, mesh.GetLocalFrame()) #array of shape (Nel, nb_pg=1, nb of vectors in basis = dim, dim)                        

            MatrixChangeOfBasisElement = sparse.coo_matrix((np.reshape(dataMCB,-1),(np.reshape(rowMCB,-1),np.reshape(colMCB,-1))), shape=(dim*Nel, dim*Nel)).tocsr()
            
            F = np.reshape( MatrixChangeOfBasisElement.T * np.reshape(res[:,0:dim].T, -1)  ,  (dim,-1) ).T
            if dim == 3: 
                C = np.reshape( MatrixChangeOfBasisElement.T * np.reshape(res[:,3:6].T, -1)  ,  (3,-1) ).T
            else: C = res[:,2]
            
            return np.c_[F,C] #np.hstack((F,C))            


    def copy(self, new_id = ""):
        """
        Return a raw deep copy of the assembly without keeping current state (internal variable).

        Parameters
        ----------
        new_id : TYPE, optional
            The ID of the created constitutive law. The default is "".

        Returns
        -------
        The copy of the assembly
        """
        new_wf = self._weakForm.copy()
        
        return Assembly(new_wf, self.__Mesh, self.__elmType, new_id)
    
def DeleteMemory():
    Assembly.DeleteMemory()
    

# def ConvertData(data, mesh, convertFrom=None, convertTo='GaussPoint', elmType=None, nb_pg =None):        
#     if isinstance(data, Number): return data
    
#     if isinstance(mesh, str): mesh = Mesh.GetAll()[mesh]
#     if elmType is None: elmType = mesh.GetElementShape()
#     if nb_pg is None: nb_pg = GetDefaultNbPG(elmType, mesh)
    
#     if isinstance(data, (listStrainTensor, listStressTensor)):        
#         try:
#             return type(data)(ConvertData(data.asarray().T, mesh, convertFrom, convertTo, elmType, nb_pg).T)
#         except:
#             NotImplemented
    
#     if convertFrom is None: convertFrom = DetermineDataType(data, mesh, nb_pg)
        
#     assert (convertFrom in ['Node','GaussPoint','Element']) and (convertTo in ['Node','GaussPoint','Element']), "only possible to convert 'Node', 'Element' and 'GaussPoint' values"
    
#     if convertFrom == convertTo: return data       
#     if convertFrom == 'Node': 
#         data = Assembly._Assembly__GetNodeToGaussianPointMatrix(mesh, elmType, nb_pg) * data
#         convertFrom = 'GaussPoint'
#     elif convertFrom == 'Element':             
#         if len(np.shape(data)) == 1: data = np.tile(data.copy(),nb_pg)
#         else: data = np.tile(data.copy(),[nb_pg,1])
#         convertFrom = 'GaussPoint'
        
#     # from here convertFrom should be 'PG'
#     if convertTo == 'Node': 
#         return Assembly._Assembly_GetGaussianPointToNodeMatrix(mesh, elmType, nb_pg) * data 
#     elif convertTo == 'Element': 
#         return np.sum(np.split(data, nb_pg),axis=0) / nb_pg
#     else: return data 

def DetermineDataType(data, mesh, nb_pg):               
        if isinstance(mesh, str): mesh = Mesh.GetAll()[mesh]
        if nb_pg is None: nb_pg = GetDefaultNbPG(elmType, mesh)
 
        test = 0
        if len(data) == mesh.GetNumberOfNodes(): 
            dataType = 'Node' #fonction définie aux noeuds   
            test+=1               
        if len(data) == mesh.GetNumberOfElements(): 
            dataType = 'Element' #fonction définie aux éléments
            test += 1
        if len(data) == nb_pg*mesh.GetNumberOfElements():
            dataType = 'GaussPoint'
            test += 1
        assert test, "Error: data doesn't match with the number of nodes, number of elements or number of gauss points."
        if test>1: "Warning: kind of data is confusing. " + dataType +" values choosen."
        return dataType        