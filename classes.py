# class definitions

class passive_element :

    def __init__(self,type,name,node1,node2,value) :
        
        try :
            if type not in ["R","C","L"] :
                print("Error in passive element definition. Aborting.")
                exit()
            
        except :
            print("Error initialising object. Exiting ...")
            exit()
        
        self.value = value      # can be complex, no problem
        self.node1 = node1
        self.node2 = node2
        self.name = name
        self.volage = None
        self.current = None
        self.type = type


class indep_source :

    def __init__(self,type,name,node1,node2,acmag,acphase) :
        
        try :
            if type not in ["V","I"]:
                print("Error in type entered.Aborting.")
                exit()
        except :
            print("Error in source intialisation.")

        self.source_type = type
        self.node1 = node1
        self.node2 = node2
        self.name = name
        self.acmag = acmag
        self.acphase = acphase


class v_dep_source :

    def __init__(self,type,name,node1,node2,control_node1,control_node2,value) -> None:
        
        try :
            if type not in ["G","E"] :
                print("Error in type entered.Aborting.")
                exit()
        except :
            print("Error in dependent source initialisation.")

        self.source_type = type
        self.node1 = node1
        self.node2 = node2
        self.control_node1 = control_node1
        self.control_node2 = control_node2
        self.value = value
        self.name = name

class i_dep_source :

    def __init__(self,type,name,node1,node2,controlling_vsource,value) -> None:
        
        try :
            if type not in ["H","F"] :
                print("Error in type entered.Aborting.")
                exit()
        except :
            print("Error in dependent source initialisation.")

        self.source_type = type
        self.node1 = node1
        self.node2 = node2
        self.controlling_vsource = controlling_vsource
        self.value = value
        self.name = name
