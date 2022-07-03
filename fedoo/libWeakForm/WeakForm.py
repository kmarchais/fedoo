# base class
from fedoo.libUtil.ModelingSpace import ModelingSpace
from fedoo.libConstitutiveLaw.ConstitutiveLaw import ListConstitutiveLaw

class WeakForm:

    __dic = {}

    def __init__(self, name = "", space=None):
        assert isinstance(name, str) , "An name must be a string" 
        self.__name = name
        if space is None: 
            space = ModelingSpace.GetActive()
        elif isinstance(space, str):
            space = ModelingSpace.get_all()[space]
        self.__space = space
        self.assembly_options = {}
        #possible options : 
        # * 'assume_sym' - self.assembly_options['assume_sym'] = True  to accelerate assembly if the weak form may be considered as symmetric
        # * 'nb_gp' - set the default nb_gp
        # * 'mat_lumping' - matrix lumping if set to True
        
        if name != "":WeakForm.__dic[self.__name] = self
        
    def GetNumberOfVariables(self):
        return self.__space.nvar
        # return self.GetDifferentialOperator().nvar()

    def GetConstitutiveLaw(self):
        #no constitutive law by default
        pass
    
    def GetDifferentialOperator(self, mesh=None, localFrame = None):
        pass
            
    def Initialize(self, assembly, pb, initialTime=0.):
        #function called at the very begining of the resolution
        pass

    def InitTimeIncrement(self, assembly, pb, dtime):
        #function called at the begining of a new time increment
        #For now, used only to inform the weak form the the time step for the next increment.
        pass

    def Update(self, assembly, pb, dtime):
        #function called when the problem is updated (NR loop or time increment)
        #- New initial Stress
        #- New initial Displacement
        #- Possible modification of the mesh
        #- Change in constitutive law (internal variable)
        pass
    
    def NewTimeIncrement(self):  
        #function called at the end of a time increment. Used to update variables to the new time.
        pass
    
    def ResetTimeIncrement(self):
        #function called if the time step is reinitialized. Used to reset variables to the begining of the step
        pass

    def Reset(self):
        #function called if all the problem history is reseted.
        pass           
    
    def copy(self):
        #function to copy a weakform at the initial state
        raise NotImplementedError()
      
    @staticmethod
    def get_all():
        return WeakForm.__dic

    @property
    def space(self):
        return self.__space
    
    @property
    def name(self):
        return self.__name
    
class WeakFormSum(WeakForm):
    
    def __init__(self, list_weakform, name =""):    
        assert len(set([a.space for a in list_weakform])) == 1, \
            "Sum of assembly are possible only if all assembly are associated to the same modeling space"
        WeakForm.__init__(self, name, space = list_weakform[0].space)        
        
        if any([wf.assembly_options!={} for wf in list_weakform]):
            self.assembly_options = None
            # if assembly_options is None, the weakForm have to be splited into several sub-weakform before 
            # being used in an Assembly. This is automatically done when using Assembly.Create function
            # The restulting Assembly will be an AssemblySum object
            
        self.__constitutivelaw = ListConstitutiveLaw([a.GetConstitutiveLaw() for a in list_weakform])
        self.__list_weakform = list_weakform
        
    def GetConstitutiveLaw(self):
        #return a list of constitutivelaw
        return self.__constitutivelaw    
    
    def GetDifferentialOperator(self, mesh=None, localFrame = None):
        Diff = 0
        self._list_mat_lumping = []
        for wf in self.__list_weakform: 
            Diff_wf = wf.GetDifferentialOperator(mesh, localFrame)
            mat_lumping = wf.assembly_options.get('mat_lumping', False) #True of False
            self._list_mat_lumping.extend([mat_lumping for i in range(len(Diff_wf.op))]) #generate a list of mat_lumping value for each elementary op
            Diff += Diff_wf            
        return Diff
    
    def Initialize(self, assembly, pb, initialTime=0.):
        for wf in self.__list_weakform:
            wf.Initialize(assembly, pb, initialTime)

    def InitTimeIncrement(self, assembly, pb, dtime):
        for wf in self.__list_weakform:
            wf.InitTimeIncrement(assembly, pb, dtime)
    
    def Update(self, assembly, pb, dtime):        
        for wf in self.__list_weakform:
            wf.Update(assembly, pb, dtime)
    
    def NewTimeIncrement(self):  
        for wf in self.__list_weakform:
            wf.NewTimeIncrement()
    
    def ResetTimeIncrement(self):
        #function called if the time step is reinitialized. Used to reset variables to the begining of the step
        for wf in self.__list_weakform:
            wf.ResetTimeIncrement()

    def Reset(self):
        #function called if all the problem history is reseted.
        for wf in self.__list_weakform:
            wf.Reset()
    
    def copy(self):
        #function to copy a weakform at the initial state
        raise NotImplementedError()

    @property
    def list_weakform(self):
        return self.__list_weakform
        


def get_all():
    return WeakForm.get_all()


