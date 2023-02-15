# Assignment 2. Solving simple spice files

import numpy as np
import sys
# from fractions import Fraction
import sympy as sym
# import IPython.display as disp

sym.init_printing(use_unicode=False, wrap_line=True)


class passive_element :

    def __init__(self,type,name,node1,node2,value) :
        
        try :
            if type in ["R","C","L"] :
                self.type = type
            # elif type == "C" :
            #     self.type = type
            # elif type == "L" :
            #     self.type = type
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

            # elif type == "I" :
            #     self.acmag = acmag
            #     self.acphase = acphase

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
        # if identifier == 'R' :
        #     elem = passive_element(identifier,name,nodes[node1],nodes[node2],float(words[3]))
        #     passives.append(elem)
        
        # elif identifier == 'C' :
        #     elem = passive_element(identifier,name,nodes[node1],nodes[node2],float(words[3]))
        #     passives.append(elem)

        # elif identifier == 'L' :
        #     elem = passive_element(identifier,name,nodes[node1],nodes[node2],float(words[3]))
        #     passives.append(elem)

        # passive elements
        if identifier in ['R','L','C'] :
            elem = passive_element(identifier,name,nodes[node1],nodes[node2],float(words[3]))
            passives.append(elem)

        # independent sources
        elif identifier in ['V','I'] :
            # ac_or_dc = words[3]

            # if ac_or_dc == "dc" :
                # source = indep_source(identifier,name,nodes[node1],nodes[node2],float(words[4]),0,0)
            
            # elif ac_or_dc == "ac" :
            source = indep_source(identifier,name,nodes[node1],nodes[node2],acmag=float(words[4]),acphase=float(words[5]))
            #! acmag value float(words[5]) will be ignored and set to 0 for small signal analysis

            # else :
            #     print("Error in voltage source definiton in the following line :")
            #     print(line)

            #     print("Aborting.")
            #     exit()

            sources.append(source)
            
        # elif identifier == 'I' :
        #     # type = words[3]
            
        #     # if type == "dc" :
        #     #     source = indep_source(identifier,name,nodes[node1],nodes[node2],float(words[4]),0,0)
            
        #     # elif type == "ac" :
        #     source = indep_source(identifier,name,nodes[node1],nodes[node2],acmag=float(words[4]),acphase=float(words[5]))
            
        #     # else :
        #     #     print("Error in current source definiton in the following line :")
        #     #     print(line)

        #     #     print("Aborting.")
        #     #     exit()

        #     sources.append(source)

        else :
            print("Error in the following line : ")
            print(line)

            print("\nAborting.")
            exit()

    return nodes,passives,sources
    

def extract_analysis():

    netlist = sys.argv[1]
    with open(netlist) as file :
        line_list = file.readlines()

    # check if input file is valid
    frequency = 0
    for line in line_list :
        line_spl = line.split("#")[0].strip().split()
        
        # try except for full comments inside netlist 'body'
        # eg: # comment xyz
        try :
            if line_spl[0] == ".ac" :
                frequency = line_spl[2]
        except :
            pass
    
    return frequency


def get_impedance(type,value,frequency):
    
    try:
        if type == "C" :
            impedance = complex(0,-1/(2*np.pi*float(frequency)*value)) 
        elif type == "L" :
            impedance = complex(0,2*np.pi*float(frequency)*value)
        elif type == "R" :
            impedance = value
        else :
            print(f" Else clause inside try in get_impedance(..) triggered. Inputs provided : type : {type} value : {value} frequency : {frequency}")
            return np.infty
    except Exception as e:
        print(f"Except clause of get_impedance(..) triggered. Inputs provided : type : {type} value : {value} frequency : {frequency}")
        print(e)
        return np.infty

    return impedance


def get_impedance_symbol(type,name,s):
    
    if type == 'R' :
        return sym.Symbol(name)
    elif type == 'C' :
        return 1/(s*sym.Symbol(name))
    elif type == 'L' :
        return (s*sym.Symbol(name))


# def pol_to_cart(r,phi,phase_units="degrees") :
    
#     if phase_units == "degrees":
#         re = r*np.cos(phi*np.pi/180)
#         imag = r*np.sin(phi*np.pi/180)
    
#     elif phase_units == "radians" :
#         re = r*np.cos(phi)
#         imag = r*np.sin(phi)

#     else :
#         re = imag = 0

#     return re,imag


def form_matrices(nodes,sources,passives):
    
    # define symbol for complex frequency
    s = sym.Symbol('s')

    # identify size of matrices needed. fix variables - node voltages are the natural choice.
    # set Vgnd as 0. This reduces size of mattrices needed to be solved.

    num_of_nodes = len(nodes)    # each node voltage is an unknown
    # print(num_of_nodes)

    num_of_vsources = len([i for i in sources if i.source_type == "V"])    # each voltage source presents an unknown (current)
    # print(num_of_source)

    matrix_size = num_of_vsources + num_of_nodes
    print(f"\nNumber of unknowns = {matrix_size}")
    print(f"Matrix size = {matrix_size}\n")

    # M = np.zeros((matrix_size,matrix_size),dtype=complex)
    M = sym.Matrix(matrix_size,matrix_size,[0 for i in range(matrix_size*matrix_size)])
    # b = np.zeros(matrix_size,dtype=complex)
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

    # print(dic_vsources)

    for source in sources :
         if source.source_type == 'I' :
            dic_isources[source.name] = count
            count += 1

    # print(dic_isources)

    # scan through node-wise except GND filling up the matrix
    
    for row_idx in range(1,num_of_nodes):       # GND not included
    # row_idx from 1 to num_of_nodes-1 => indirectly going over each node other than GND

        for elem in passives:
            # impedance = get_impedance(elem.type,elem.value,frequency)
            impedance_symbol = get_impedance_symbol(elem.type,elem.name,s)
            # print(f"{elem.name}; {impedance_symbol}")
            if elem.node1 == row_idx :
                # M[row_idx][row_idx] += 1/impedance
                M[row_idx,row_idx] += 1/impedance_symbol
                col_idx = elem.node2
                if col_idx != 0 :
                    # M[row_idx][col_idx] -= 1/impedance 
                    M[row_idx,col_idx] -= 1/impedance_symbol

            if elem.node2 == row_idx :
                # M[row_idx][row_idx] += 1/impedance
                M[row_idx,col_idx] += 1/impedance_symbol
                col_idx = elem.node1
                if col_idx != 0 :
                    # M[row_idx][col_idx] -= 1/impedance
                    M[row_idx,col_idx] -= 1/impedance_symbol


    for source in sources :
        
        if source.source_type == "V" :
            node1 = source.node1
            node2 = source.node2
            
            # current through vsource in the equation for node1
            if node1 != 0 :
                # M[node1][dic_vsources[source.name]] = 1
                M[node1,dic_vsources[source.name]] = 1

            # current through vsource in the equation for node2
            if node2 != 0 :
                # M[node2][dic_vsources[source.name]] = -1
                M[node2,dic_vsources[source.name]] = -1

            # voltage source equation
            
            if node1 != 0 :
                # M[dic_vsources[source.name]][node1] = 1
                M[dic_vsources[source.name],node1] = 1
            if node2 != 0 :
                # M[dic_vsources[source.name]][node2] = -1
                M[dic_vsources[source.name],node2] = -1
            
            # b[dic_vsources[source.name]] += source.dcmag
            # re,imag = pol_to_cart(source.acmag,source.acphase)
            re,imag = source.acmag,0    #! acphase kept 0 for small signal analysis
            b[dic_vsources[source.name]] += (re + 1j*imag)  #!

        elif source.source_type == "I" :
            node1 = source.node1
            node2 = source.node2

            # independent current source
            if node1 != 0 :
                # b[node1] += source.dcmag
                # re,imag = pol_to_cart(source.acmag,source.acphase)
                re,imag = source.acmag,0    #! acphase kept 0 for small signal analysis
                b[node1] += (re + 1j*imag)  #!
               
            if node2 != 0 :
                # b[node1] += source.dcmag
                # re,imag = pol_to_cart(source.acmag,source.acphase)
                re,imag = source.acmag,0    #! acphase kept 0 for small signal analysis
                b[node1] += (re + 1j*imag)  #!

    return M,b


# def conv_to_fraction(num):
#     numer = Fraction(num).limit_denominator(10000).numerator
#     denom = Fraction(num).limit_denominator(10000).denominator
#     return numer,denom


# def print_equations(M,b):
    
#     print("Printing the equations formed : \n")
#     vars = len(b)
#     for row_idx in range(1,vars):
#         start = False
#         for col_idx in range(vars):
#             if M[row_idx,col_idx] != 0 :
                
#                 if start :
#                     print("+ ",end='')
#                 real = M[row_idx,col_idx].real
#                 imag = M[row_idx,col_idx].imag
#                 rnumer,rdenom = conv_to_fraction(real)
#                 inumer,idenom = conv_to_fraction(imag)
                
#                 if not rnumer and inumer : 
#                     print(f"({inumer}/{idenom})j x{col_idx} ",end= '')
                
#                 elif not inumer and rnumer :
#                     print(f"({rnumer}/{rdenom}) x{col_idx} ",end= '')

#                 elif inumer and rnumer :
#                     print(f"(({rnumer}/{rdenom}) + ({inumer}/{idenom})j) x{col_idx} ",end= '')                    

#                 start = True
        
#         re_rhs = b[row_idx].real
#         imag_rhs = b[row_idx].imag

#         if not re_rhs and not imag_rhs :
#             string_rhs = " = 0"
        
#         elif not re_rhs and imag_rhs :
#             string_rhs = f" = j{imag_rhs}"
        
#         elif re_rhs and not imag_rhs :
#             string_rhs = f" = {re_rhs}"

#         else :
#             string_rhs = f" = {re_rhs} + {imag_rhs}j"

#         print(string_rhs)
    

# def print_soln(x):
#     print("\nPrinting the solution : \n")
#     for i in range(1,len(x)):
#         re = x[i].real
#         imag = x[i].imag
        
#         string = "error"

#         if re and imag :
#             re_s = "{:.3e}".format(re)
#             imag_s = "{:.3e}".format(re)
#             string = f"x{i} = {re_s} + {imag_s}j"

#         elif not re and imag :
#             imag_s = "{:.3e}".format(re)
#             string = f"x{i} = {imag_s}j"

#         elif re and not imag :
#             re_s = "{:.3e}".format(re)
#             string = f"x{i} = {re_s}"

#         elif not re and not imag :
#             string = f"x{i} = 0"
        
#         print(string)

#     print()


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
    # frequency = extract_analysis()

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

    # print_equations(M,b)        # check if equations are correct

    # solve linear equations - trivial-ish
    # x = np.linalg.solve(M, b)
    x = M.LUsolve(b)
    # print_soln(x)
    sym.pprint((x))
    # disp.display(x)

if __name__ == "__main__":
    main()