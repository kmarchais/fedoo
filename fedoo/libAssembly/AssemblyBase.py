#baseclass

class AssemblyBase:

    __dic = {}

    def __init__(self, name = "", space=None):
        assert isinstance(name, str) , "An name must be a string" 
        self.__name = name

        self.global_matrix = None
        self.global_vector = None
        self.mesh = None 
        
        if name != "": AssemblyBase.__dic[self.__name] = self
        self.__space = space

    def get_global_matrix(self):
        if self.global_matrix is None: self.assemble_global_mat()        
        return self.global_matrix

    def get_global_vector(self):
        if self.global_vector is None: self.assemble_global_mat()        
        return self.global_vector

    # def SetVector(self, V):
    #     self.global_vector = V 

    # def SetMatrix(self, M):
    #     self.global_matrix = M
    
    # def AddMatrix(self, M):
    #     self.global_matrix += M
        
    def assemble_global_mat(self):
        #needs to be defined in inherited classes
        pass

    def delete_global_mat(self):
        """
        Delete Global Matrix and Global Vector related to the assembly. 
        This method allow to force a new assembly
        """
        self.global_matrix = None
        self.global_vector = None
    
    
    @staticmethod
    def get_all():
        return AssemblyBase.__dic
    
    # @staticmethod
    # def Launch(name):
    #     """
    #     Assemble the global matrix and global vector of the assembly name
    #     name is a str
    #     """
    #     AssemblyBase.get_all()[name].assemble_global_mat()    
    
    @property
    def space(self):
        return self.__space
   
    @property
    def name(self):
        return self.__name


class AssemblySum(AssemblyBase):
    """
    Build a sum of Assembly objects
    All the Assembly objects should be associated to:
    * meshes based on the same list of nodes.
    * the same modeling space (ie the same space property)
        
    Parameters
    ----------
    list_assembly: list of Assembly 
        list of Assembly objects to sum
    name: str
        name of the Assembly             
    assembly_output: Assembly (optional keyword arg)
        Assembly object used to extract output values (using Problem.GetResults or Problem.SaveResults)
    """
    def __init__(self, list_assembly, name ="", **kargs):      
        AssemblyBase.__init__(self, name)  
        
        for i,assembly in enumerate(list_assembly):
            if isinstance(assembly, str): list_assembly[i] = AssemblyBase.get_all()[assembly]                                
            
        assert len(set([a.space for a in list_assembly])) == 1, \
            "Sum of assembly are possible only if all assembly are associated to the same modeling space"
        assert len(set([a.mesh.n_nodes for a in list_assembly])) == 1,\
            "Sum of assembly are possible only if the two meshes have the same number of Nodes"

        self.__list_assembly = list_assembly
        self.__assembly_output = kargs.get('assembly_output', None)
                        
        self.mesh = list_assembly[0].mesh

        if name == "":
            name = '_'.join([assembly.name for assembly in list_assembly])    
            
        self.__reload = kargs.pop('reload', 'all')                      

    # def SetMesh(self, mesh):
    #     self.mesh = mesh

    # def GetMesh(self):
    #     return self.mesh

    def assemble_global_mat(self,compute='all'):
        if self.__reload == 'all': 
            for assembly in self.__list_assembly:
                assembly.assemble_global_mat(compute)
        else:
            for numAssembly in self.__reload:
                self.__list_assembly[numAssembly].assemble_global_mat(compute)
            
        if not(compute == 'vector'):         
            self.SetMatrix(sum([assembly.get_global_matrix() for assembly in self.__list_assembly]))
        if not(compute == 'matrix'):
            self.SetVector(sum([assembly.get_global_vector() for assembly in self.__list_assembly]))
    
    def update(self, pb, dtime=None, compute = 'all'):
        """
        Update the associated weak form and assemble the global matrix
        Parameters: 
            - pb: a Problem object containing the Dof values
            - time: the current time        
        """
        if self.__reload == 'all' or compute in ['vector', 'none']: #if compute == 'vector' or 'none' the reload arg is ignored
            for assembly in self.__list_assembly:
                assembly.update(pb,dtime,compute)           
        else:
            for numAssembly in self.__reload:
                self.__list_assembly[numAssembly].update(pb,dtime,compute)
                    
        if not(compute == 'vector'):         
            self.SetMatrix( sum([assembly.get_global_matrix() for assembly in self.__list_assembly]) )
        if not(compute == 'matrix'):
            self.SetVector( sum([assembly.get_global_vector() for assembly in self.__list_assembly]) )


    def set_start(self, pb, dt):
        """
        Apply the modification to the constitutive equation required at each new time increment. 
        Generally used to increase non reversible internal variable
        Assemble the new global matrix. 
        """
        for assembly in self.__list_assembly:
            assembly.set_start(pb, dt)   
                

    def initialize(self, pb, initialTime=0.):
        """
        reset the current time increment (internal variable in the constitutive equation)
        Doesn't assemble the new global matrix. Use the Update method for that purpose.
        """
        for assembly in self.__list_assembly:
            assembly.initialize(pb, initialTime=0.)   

    def to_start(self):
        """
        Reset the current time increment (internal variable in the constitutive equation)
        Doesn't assemble the new global matrix. Use the Update method for that purpose.
        """
        for assembly in self.__list_assembly:
            assembly.to_start()         

    def reset(self):
        """
        reset the assembly to it's initial state.
        Internal variable in the constitutive equation are reinitialized 
        And stored global matrix and vector are deleted
        """
        for assembly in self.__list_assembly:
            assembly.reset() 
        self.delete_global_mat()

    @property
    def list_assembly(self):
        return self.__list_assembly
   
    @property
    def assembly_output(self):
        return self.__assembly_output
    



def Sum(*listAssembly, name ="", **kargs):
    """
    Return a new assembly which is a sum of N assembly. 
    Assembly.Sum(assembly1, assembly2, ..., assemblyN, name ="", reload = [1,4] )
    
    The N first arguments are the assembly to be summed.
    name is the name of the created assembly:
    reload: a list of indices for subassembly that are recomputed at each time the summed assembly
    is Launched. Default is 'all' (equivalent to all indices).     
    """
    return AssemblySum(list(listAssembly), name, **kargs)
            
def get_all():
    return AssemblyBase.get_all()

def Launch(name):
    AssemblyBase.get_all()[name].assemble_global_mat()    
