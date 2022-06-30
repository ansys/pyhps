# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------
from __future__ import division
import os
import re
import sys
import json
import math

def weight(P, d, t, B, H, rho, E):
    w = 2 * math.pi * rho * d * t * math.sqrt((0.5*B)**2 + H**2)
    return w

def stress(P, d, t, B, H, rho, E):
    s = P * math.sqrt((0.5*B)**2 + H**2) / (2*t*math.pi*d*H)
    return s/1000 #psi to ksi

def buckling_stress(P, d, t, B, H, rho, E):
    b = math.pi**2 * E * (d**2 + t**2) / ( 8 * ( (0.5*B)**2 + H**2) )
    return b/1000 #psi to ksi

def deflection(P, d, t, B, H, rho, E):
    f = P * math.pow((0.5*B)**2 + H**2, 3/2) / (2 * t * math.pi * d * H**2 * E)
    return f

def main():

    input_file_name = sys.argv[1]
    input_file_path = os.path.abspath(input_file_name)
    with open(input_file_path, 'r') as input_file:
        params = json.load(input_file)

    #print(params)

    output_parameters = {}
    output_parameters.update(weight=weight(**params))
    output_parameters.update(stress=stress(**params))
    output_parameters.update(buckling_stress=buckling_stress(**params))
    output_parameters.update(deflection=deflection(**params))
    
    #print(output_parameters)

    with open("output_parameters.json", 'w') as out_file:
        json.dump(output_parameters, out_file, indent=4)

if __name__ == '__main__':
  main()