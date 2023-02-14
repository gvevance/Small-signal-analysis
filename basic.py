import math


def db20(value) :
    try :
        return 20*math.log10(value)
    except :
        print("Error.Returning 0.")
        return 0


def db10(value) :
    try :
        return 10*math.log10(value)
    except :
        print("Error.Returning 0.")
        return 0