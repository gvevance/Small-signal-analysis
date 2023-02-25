# methods to help circuit analysis
import sympy as sym
from netlist_management import get_lines
from netlist_management import extract_nodes_and_elems
import sympy.printing.latex as latex

# sym.init_printing(use_unicode=False, wrap_line=True)

def get_impedance_symbol(type,name,value,s,view='symbol'):
    
    if view == 'symbol' :
        if type == 'R' :
            return sym.Symbol(name)
        elif type == 'C' :
            return 1/(s*sym.Symbol(name))
        elif type == 'L' :
            return (s*sym.Symbol(name))

    elif view == 'value' :
        if type == 'R' :
            # return sym.Symbol(name)
            return value
        elif type == 'C' :
            # return 1/(s*sym.Symbol(name))
            return 1/(s*value)
        elif type == 'L' :
            # return (s*sym.Symbol(name))
            return (s*value)


def get_dep_source_symbol (name,value,view='symbol') :
    if view == 'symbol' :
        return sym.Symbol(name)
    elif view == 'value' :
        return value


def form_matrices(nodes,sources,passives,v_dep_sources,i_dep_sources):
    
    # to back-reference variable names and expressions
    reference_dic = {}

    # define symbol for complex frequency
    s = sym.Symbol('s')

    # identify size of matrices needed. fix variables - node voltages are the natural choice.
    # set Vgnd as 0. This reduces size of mattrices needed to be solved.

    num_of_nodes = len(nodes)    # each node voltage is an unknown

    num_of_vsources = len([i for i in sources if i.source_type == "V"])    # each voltage source presents an unknown (current)

    # added code for VCVS - auxiliary current variable required
    num_of_vcvs = len([i for i in v_dep_sources if i.source_type == "E"])    # each VCVS presents an unknown (auxiliary current)
    num_of_ccvs = len([i for i in i_dep_sources if i.source_type == "H"])
    
    matrix_size = num_of_vsources + num_of_nodes + num_of_vcvs + num_of_ccvs
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
    # dic_isources = {}
    dic_vcvs = {}
    dic_ccvs = {}
    count = num_of_nodes

    for i in range(count) :
        reference_dic[f'V_node_{i}'] = i

    for source in sources :
        if source.source_type == 'V' :
            dic_vsources[source.name] = count
            reference_dic['I_'+source.name] = count
            count += 1

    #! must check for correctness here. Commented out lines.
    # for source in sources :
    #      if source.source_type == 'I' :
    #         dic_isources[source.name] = count
    #         count += 1
    
    for source in v_dep_sources :
        if source.source_type == 'E' :
            dic_vcvs[source.name] = count
            reference_dic['I_'+source.name] = count
            count += 1

        # if source.source_type == "G" :
        #     dic_vccs[source.name] = count
        #     count += 1

    for source in i_dep_sources :
        if source.source_type == 'H' :
            dic_ccvs[source.name] = count
            reference_dic['I_'+source.name] = count
            count += 1

    # scan through node-wise except GND filling up the matrix
    
    for row_idx in range(1,num_of_nodes):       # GND not included
    # row_idx from 1 to num_of_nodes-1 => indirectly going over each node other than GND
        
        # print("Filling matrix with passives connected to node",row_idx)
        
        for elem in passives:
            impedance_symbol = get_impedance_symbol(elem.type,elem.name,elem.value,s,view='symbol')
            if elem.node1 == row_idx :
                M[row_idx,row_idx] += 1/impedance_symbol
                col_idx = elem.node2
                if col_idx != 0 :
                    M[row_idx,col_idx] -= 1/impedance_symbol

            if elem.node2 == row_idx :
                M[row_idx,row_idx] += 1/impedance_symbol
                col_idx = elem.node1
                if col_idx != 0 :
                    M[row_idx,col_idx] -= 1/impedance_symbol
            
        # print(M)
        # print()

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
                b[node1] -= (re + 1j*imag)  #!
               
            if node2 != 0 :
                re,imag = source.acmag,0    #! acphase kept 0 for small signal analysis
                b[node2] += (re + 1j*imag)  #!


    for source in v_dep_sources :
        
        dep_source_symbol = get_dep_source_symbol(source.name,source.value,view='symbol')
        if source.source_type == 'G' :
            node1 = source.node1
            node2 = source.node2
            control_node1 = source.control_node1
            control_node2 = source.control_node2

            if node1 != 0 :
                row_idx = node1
                M[row_idx,control_node1] += dep_source_symbol
                M[row_idx,control_node2] -= dep_source_symbol

            if node2 != 0 :
                row_idx = node2
                M[row_idx,control_node1] -= dep_source_symbol
                M[row_idx,control_node2] += dep_source_symbol

        if source.source_type == "E" :
            node1 = source.node1
            node2 = source.node2
            control_node1 = source.control_node1
            control_node2 = source.control_node2

            # fill the matrix for the auxiliary variable used
            if node1 != 0 :
                row_idx = node1
                M[row_idx,dic_vcvs[source.name]] = 1 #! =1 (?)

            if node2 != 0 :
                row_idx = node2
                M[row_idx,dic_vcvs[source.name]] = 1 #! =-1 (?)

            # must fill the matrix with the equation of the VCVS itself
            row_idx = dic_vcvs[source.name] 
            # dep_source_symbol = get_dep_source_symbol(source.name)
            
            if node1 != 0 :
                M[row_idx,node1] = 1
            if node2 != 0 :
                M[row_idx,node2] = -1
            if control_node1 != 0 :
                M[row_idx,control_node1] -= dep_source_symbol
            if control_node2 != 0 :
                M[row_idx,control_node2] += dep_source_symbol

    for source in i_dep_sources :

        dep_source_symbol = get_dep_source_symbol(source.name,source.value,view='symbol')
        if source.source_type == "H" :
            node1 = source.node1
            node2 = source.node2
            controlling_vsource = source.controlling_vsource

            # filling up wherever the auxiliary current appears in the M matrix
            if node1 != 0 :
                M[node1,dic_ccvs[source.name]] = 1

            if node2 != 0 :
                M[node2,dic_ccvs[source.name]] = -1

            # writing the CCVS equation at the row given for CCVS equation
            row_idx = dic_ccvs[source.name]

            if node1 != 0 :
                M[row_idx,node1] = 1
            if node2 != 0 :
                M[row_idx,node2] = -1

            M[row_idx,dic_vsources[controlling_vsource]] = -dep_source_symbol

        if source.source_type == 'F':
            node1 = source.node1
            node2 = source.node2
            controlling_vsource = source.controlling_vsource

            if node1 != 0 :
                M[node1,dic_vsources[controlling_vsource]] += dep_source_symbol
            if node2 != 0 :
                M[node2,dic_vsources[controlling_vsource]] -= dep_source_symbol

    return M,b,reference_dic


def solve() :
    
    lines = get_lines()
    verbose = False
    if verbose :
        print("\nPrinting relevant netlist lines :\n")
        for i in lines:
            print(i)
        print()

    # solve spice netlist
    nodes,passives,sources,v_dep_sources,i_dep_sources = extract_nodes_and_elems(lines)

    if verbose :
        print("\nNodes extracted : ")
        print(nodes)

        print("\nPassive elements extracted : \n")
        for obj in passives:
            print(obj.name,obj.node1,obj.node2,obj.value)

        print("\nSources extracted : \n")
        for src in sources :
            print(f"{src.name} {src.node1} {src.node2} acmag={src.acmag} acphase={src.acphase}")    

    M,b,reference_dic = form_matrices(nodes,sources,passives,v_dep_sources,i_dep_sources)
    
    if verbose :
        print("Printing matrix M :")
        print(M)
        print("Printing matrix b :")
        print(b)

    # solve for unknowns
    x = M.LUsolve(b)
    for item in reference_dic :
        print(item,reference_dic[item])
    print()

    # sym.pprint((x[-2]),num_columns=100)    
    # print(latex((x)))
    
    solution = {}
    for item in reference_dic :
        solution[item] = x[reference_dic[item]]
        
    print(latex(solution['V_node_2']))
