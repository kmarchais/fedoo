# base class

class WeakForm:

    __dic = {}

    def __init__(self, ClID = ""):
        assert isinstance(ClID, str) , "An ID must be a string" 
        self.__ID = ClID
        self.assumeSymmetric = False #use to accelerate assembly if the weak form may be considered as symmetric

        WeakForm.__dic[self.__ID] = self

    def GetID(self):
        return self.__ID

    def GetNumberOfVariables(self):
        return self.GetDifferentialOperator().nvar()

    def GetConstitutiveLaw(self):
        #no constitutive law by default
        pass
    
    
    def Initialize(self, assembly, pb, initialTime=0.):
        #function called at the begining of the resolution
        pass
    
    def Update(self, assembly, pb, dtime):
        #function called when the problem is updated (NR loop or time increment)
        #- New initial Stress
        #- New initial Displacement
        #- Possible modification of the mesh
        #- Change in constitutive law (internal variable)
        pass
    
    def NewTimeIncrement(self):  
        #function called when the time is increased.
        pass
    
    def ResetTimeIncrement(self):
        #function called if the time step is reinitialized.
        pass

    def Reset(self):
        #function called if all the problem history is reseted.
        pass


    @staticmethod
    def GetAll():
        return WeakForm.__dic


def GetAll():
    return WeakForm.GetAll()


