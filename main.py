# Assignment 2. Solving simple spice files

import numpy as np
import sys
import sympy as sym

sym.init_printing(use_unicode=False, wrap_line=True)


class passive_element :

    def __init__(self,type,name,node1,node2,value) :
        
        try :
            if type in ["R","C","L"] :
                self.type = type
            else :
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


class indep_source :

    def __init__(self,type,name,node1,node2,acmag,acphase) :
        
        try :
            if type in ["V","I"]:
                self.acmag = acmag
                self.acphase = acphase

            else :
                print("Error in type entered.Aborting.")
                exit()
        except :
            print("Error in source intialisation.")

        self.source_type = type
        self.node1 = node1
        self.node2 = node2
        self.name = name


def get_lines():

    pyfile = sys.argv[0]

    if len(sys.argv) != 2 :
        print(f"Usage : python3 {pyfile} <netlist file>")
        exit()

    netlist = sys.argv[1]
    with open(netlist) as file :
        line_list = file.readlines()

    # check if input file is valid
    start , end = -1,-2
    for line in line_list :
        line_s = line.strip()
        if line_s == ".circuit" :
            start = line_list.index(line)

        elif line_s == ".end" :
            end = line_list.index(line)

    if start > end or start == -1 :
        print("Malformed input file.")
        exit()

    # remove extra junk from netlist
    ret_lines=[]
    for line in line_list[start+1:end]:
        temp = ' '.join(line.split('#')[0].split())
        if temp :       # check for empty line
            ret_lines.append(temp)

    return ret_lines


def extract_nodes_and_elems(lines):
    
    sources = []
    passives = []
    nodes = {}  


    count = 1
    for line in lines:
        words = line.split()
        node1 = words[1]
        node2 = words[2]
        identifier = words[0][0]
        name = words[0]

        if node1 not in nodes:
            
            if node1 == "GND" :
                nodes[node1] = 0
            
            else :
                nodes[node1] = count
                count += 1
                           
        if node2 not in nodes:
            
            if node2 == "GND" :
                nodes[node2] = 0
            
            else :
                nodes[node2] = count
                count += 1
        
        # passive elements
        if identifier in ['R','L','C'] :
            elem = passive_element(identifier,name,nodes[node1],nodes[node2],float(words[3]))
            passives.append(elem)

        # independent sources
        elif identifier in ['V','I'] :
            source = indep_source(identifier,name,nodes[node1],nodes[node2],acmag=float(words[4]),acphase=float(words[5]))
            #! acmag value float(words[5]) will be ignored and set to 0 for small signal analysis
            sources.append(source)
            
        else :
            print("Error in the following line : ")
            print(line)

            print("\nAborting.")
            exit()

    return nodes,passives,sources


def get_impedance_symbol(type,name,s):
    
    if type == 'R' :
        return sym.Symbol(name)
    elif type == 'C' :
        return 1/(s*sym.Symbol(name))
    elif type == 'L' :
        return (s*sym.Symbol(name))


def form_matrices(nodes,sources,passives):
    
    # define symbol for complex frequency
    s = sym.Symbol('s')

    # identify size of matrices needed. fix variables - node voltages are the natural choice.
    # set Vgnd as 0. This reduces size of mattrices needed to be solved.

    num_of_nodes = len(nodes)    # each node voltage is an unknown

    num_of_vsources = len([i for i in sources if i.source_type == "V"])    # each voltage source presents an unknown (current)

    matrix_size = num_of_vsources + num_of_nodes
    print(f"\nNumber of unknowns = {matrix_size}")
    print(f"Matrix size = {matrix_size}\n")

    M = sym.Matrix(matrix_size,matrix_size,[0 for i in range(matrix_size*matrix_size)])
    b = sym.Matrix([0 for i in range(matrix_size)])

    ''' Convention followed : 
        1. The first variable is V0 which is the ground node voltage. We know it is 0.
        2. The next k variables are the k node voltages whose voltages we must find.
        3. The next n variables are the currents through the n independent voltage sources in the circuit. 
           The convention for the current through a voltage source is "into the positive terminal" '''
    
    ''' Equation order :
        1. The first equation is V0 = 0.
        2. The next k equations are for the k nodes in the circuit. 
        3. The next n equations define the voltage source equations. '''

    # set V0 = 0 as equation 1
    M[0,0] = 1
    
    dic_vsources = {}
    dic_isources = {}
    count = num_of_nodes
    for source in sources :
        if source.source_type == 'V' :
            dic_vsources[source.name] = count
            count += 1

    for source in sources :
         if source.source_type == 'I' :
            dic_isources[source.name] = count
            count += 1

    # scan through node-wise except GND filling up the matrix
    
    for row_idx in range(1,num_of_nodes):       # GND not included
    # row_idx from 1 to num_of_nodes-1 => indirectly going over each node other than GND

        for elem in passives:
            impedance_symbol = get_impedance_symbol(elem.type,elem.name,s)
            if elem.node1 == row_idx :
                M[row_idx,row_idx] += 1/impedance_symbol
                col_idx = elem.node2
                if col_idx != 0 :
                    M[row_idx,col_idx] -= 1/impedance_symbol

            if elem.node2 == row_idx :
                M[row_idx,col_idx] += 1/impedance_symbol
                col_idx = elem.node1
                if col_idx != 0 :
                    M[row_idx,col_idx] -= 1/impedance_symbol


    for source in sources :
        
        if source.source_type == "V" :
            node1 = source.node1
            node2 = source.node2
            
            # current through vsource in the equation for node1
            if node1 != 0 :
                M[node1,dic_vsources[source.name]] = 1

            # current through vsource in the equation for node2
            if node2 != 0 :
                M[node2,dic_vsources[source.name]] = -1

            # voltage source equation
            
            if node1 != 0 :
                M[dic_vsources[source.name],node1] = 1
            if node2 != 0 :
                M[dic_vsources[source.name],node2] = -1
            
            re,imag = source.acmag,0    #! acphase kept 0 for small signal analysis
            b[dic_vsources[source.name]] += (re + 1j*imag)  #!

        elif source.source_type == "I" :
            node1 = source.node1
            node2 = source.node2

            # independent current source
            if node1 != 0 :
                re,imag = source.acmag,0    #! acphase kept 0 for small signal analysis
                b[node1] += (re + 1j*imag)  #!
               
            if node2 != 0 :
                re,imag = source.acmag,0    #! acphase kept 0 for small signal analysis
                b[node1] += (re + 1j*imag)  #!

    return M,b


def main():

    lines = get_lines()
    verbose = False
    if verbose :
        print("\nPrinting relevant netlist lines :\n")
        for i in lines:
            print(i)
        print()

    # solve spice netlist
    nodes,passives,sources = extract_nodes_and_elems(lines)

    if verbose :
        print("\nNodes extracted : ")
        print(nodes)

        print("\nPassive elements extracted : \n")
        for obj in passives:
            print(obj.name,obj.node1,obj.node2,obj.value)

        print("\nSources extracted : \n")
        for src in sources :
            print(f"{src.name} {src.node1} {src.node2} acmag={src.acmag} acphase={src.acphase}")    

    M,b = form_matrices(nodes,sources,passives)
    
    if verbose :
        print("Printing matrix M :")
        print(M)
        print("Printing matrix b :")
        print(b)

    # solve for unknowns
    x = M.LUsolve(b)
    sym.pprint((x))

if __name__ == "__main__":
    main()