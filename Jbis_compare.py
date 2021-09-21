import time
import os
import os.path
import math


def compare(path1: str, path2: str):
    with open(path1) as file1:
        with open(path2) as file2:
            for line1, line2 in zip(file1, file2):
                if line1 != line2:
                    if line1.split(" ")[0] =="///DATE" and line2.split(" ")[0] =="///DATE":
                        break
                    else:
                        print("First difference find in files:")
                        print("- First line:")
                        print(line1)
                        print("- Second line:")
                        print(line2)
                        return False
    return True
