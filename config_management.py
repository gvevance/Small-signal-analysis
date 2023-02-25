# methods to read config

import sys

def return_config_dic():
    
    try :
        config = sys.argv[2]
    except :
        return None

    with open(config) as file :
        config_line_list = file.readlines()

    config_dic = {}
    for line in config_line_list :
        line_s = line.strip()
        words = line_s.split()
        elem = words[0]
        view = words[1]
        config_dic[elem] = view

    return config_dic