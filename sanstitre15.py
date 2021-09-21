# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 15:21:05 2021

@author: beraudn
"""

new_lines = []
no_arc = False
with open("points.txt", 'r') as file:
    lines = file.readlines()
    for line in lines:
        if line == "noarc\n":
            if not no_arc:
                new_lines.append("ARC / OFF\n")
                new_lines.append("ARC / ON\n")
            no_arc = True
        
        elif line == "newline\n":
            print("newline")
        else:
            no_arc = False
            new_lines.append(line)
            
with open("points.APT", 'w') as file:
    for line in new_lines:
        file.write(line )
        