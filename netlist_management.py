# file management
import sys
from classes import passive_element
from classes import indep_source
from classes import i_dep_source
from classes import v_dep_source

def get_lines():

    pyfile = sys.argv[0]

    if len(sys.argv) not in [2,3] :
        print(f"Usage : python3 {pyfile} <netlist file> <optional config file>")
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
    v_dep_sources = []
    i_dep_sources = []
    passives = []
    nodes = {}  

    count = 1
    for line in lines:
        words = line.split()
        node1 = words[1]
        node2 = words[2]
        identifier = words[0][0]
        name = words[0]
        
        control_node1,control_node2 = None,None                  # for voltage dependent sources
        controlling_vsource = None                               # for current dependent sources
        
        if identifier in ['G','E'] :
            control_node1,control_node2 = words[3],words[4]      # for dependent sources

        if identifier in ['F','H'] :
            controlling_vsource = words[3]

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
        
        if control_node1 != None and control_node1 not in nodes:
            
            if control_node1 == "GND" :
                nodes[control_node1] = 0
            
            else :
                nodes[control_node1] = count
                count += 1

        if control_node2 != None and control_node2 not in nodes:
            
            if control_node2 == "GND" :
                nodes[control_node2] = 0
            
            else :
                nodes[control_node2] = count
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

        elif identifier in ['G','E'] :
            source = v_dep_source(identifier,name,nodes[node1],nodes[node2],nodes[control_node1],nodes[control_node2],value = float(words[5]))
            v_dep_sources.append(source)

        elif identifier in ['H','F'] :
            source = i_dep_source(identifier,name,nodes[node1],nodes[node2],controlling_vsource,value = float(words[4]))
            i_dep_sources.append(source)

        else :
            print("Error in the following line : ")
            print(line)

            print("\nAborting.")
            exit()

    return nodes,passives,sources,v_dep_sources,i_dep_sources

