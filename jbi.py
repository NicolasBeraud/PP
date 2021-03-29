import time
import os
import os.path
from datetime import datetime

FILE_EXTENSION = "JBI"
RAPID_SPEED = 50
VERSION = "0"


class Point:
    def __init__(self, x, y, z, i, j, k):
        self.x = x
        self.y = y
        self.z = z
        self.i = i
        self.j = j
        self.k = k

    def write(self, number):
        return "C" + str(number).zfill(5) + "=""{:.3f}".format(self.x) + ",""{:.3f}".format(
            self.y) + ",""{:.3f}".format(self.z) \
               + ",""{:.4f}".format(self.i) + ",""{:.4f}".format(self.j) + ",""{:.4f}".format(self.k)


def format_points(points):
    lines = []
    for i, point in enumerate(points):
        lines.append(point.write(i))
    return lines


def write_lines(output_path, lines):
    with open(output_path, 'w') as output_file:
        for line in lines:
            output_file.write(line + "\n")


class Jbi:

    def intro(self):
        lines = ["'version: "+ VERSION]
        lines.append("/JOB")
        name = os.path.splitext(self.input_path)[0]
        lines.append("//NAME " + name)
        lines.append("//POS")
        lines.append("///NPOS 48,0,0,2,0,0")
        lines.append("///TOOL 1")
        lines.append("///POSTYPE ROBOT")
        lines.append("///RECTAN")
        lines.append("///RCONF 1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
        return lines

    def pre_instruction(self, with_move):
        lines = ["//INST"]
        date = datetime.now()
        text = date.strftime("%m/%d/%Y %H:%M")
        lines.append("///DATE " + text)
        lines.append("///COMM")
        if with_move:
            lines.append("///ATTR SC,RW,RJ")
        else:
            lines.append("///ATTR SC,RW")
        lines.append("///FRAME ROBOT")
        lines.append("///GROUP1 RB1")
        lines.append("NOP")

        return lines

    def write_trj_file(self):
        print("Writing trajectory file number: " + str(self.trj_part))
        path = os.path.splitext(self.input_path)[0] + "_tjr" + str(self.trj_part) + "." + FILE_EXTENSION
        lines = self.intro()
        lines.extend(format_points(self.points))
        lines.extend(self.pre_instruction(True))
        lines.extend(self.trj_instructions)
        lines.append("END")
        write_lines(path, lines)
        self.files.append(path)

        self.main_instructions.append("'Part trajectory number: " + str(self.trj_part))
        self.main_instructions.append("CALL JOB:" + os.path.splitext(path)[0])

        self.points = []
        self.trj_instructions = []
        self.trj_part = self.trj_part + 1

    def write_main_file(self, instructions):
        if len(self.points) > 0:
            self.write_trj_file()
        lines = self.intro()
        lines.extend(self.pre_instruction(False))
        lines.append("CALL JOB:DEBUT")
        lines.extend(instructions)
        lines.append("CALL JOB:FIN")
        lines.append("END")
        write_lines(self.output_path, lines)
        self.files.append(self.output_path)

    def __init__(self, input_path):
        # time calculation monitoring
        tic = time.perf_counter()
        print("Post Processor version: " + VERSION)

        self.input_path = input_path
        self.output_path = os.path.splitext(input_path)[0] + "." + FILE_EXTENSION
        print("Input path: " + self.input_path)
        print("Output path: " + self.output_path)

        self.points = []
        self.files =[]

        if os.path.isfile(input_path):
            with open(input_path, 'r') as file:
                lines = file.readlines()
                self.main_instructions = []
                self.trj_part = 0
                self.trj_instructions = []
                rapid = False
                for line_number, line in enumerate(lines):
                    line = line.rstrip()
                    if line[0] == "$" and line[1] == "$":
                        self.trj_instructions.append("'" + line[2:])
                    else:
                        line = line.replace(" ", "")
                        arguments = line.split('/')
                        instruction = arguments[0]

                        if instruction == "ARC":
                            argument = arguments[1]
                            if argument == "ON":
                                self.trj_instructions.append("ARCON")
                            elif argument == "OFF":
                                self.trj_instructions.append("ARCOF")
                            else:
                                print("!!! Unknown argument in instruction ARC line " + str(line_number) + ": " + line)

                        elif instruction == "GOTO":
                            coordinates = arguments[1].split(',')
                            self.points.append(
                                Point(float(coordinates[0]), float(coordinates[1]), float(coordinates[2]),
                                      float(coordinates[3]), float(coordinates[4]), float(coordinates[5])))
                            self.trj_instructions.append("MOVL C" + str(len(self.points)).zfill(5))
                            if rapid:
                                rapid = False
                            if len(self.points) > 1999:
                                file_name = self.write_trj_file()

                        elif instruction == "FEDRATE":
                            options = arguments[1].split(',')
                            if options[0] != "MMPS":
                                print("!!! Unknown unit for instruction FEDRATE in line " + str(
                                    line_number) + ": " + line)
                            else:
                                speed = float(options[1])
                                self.trj_instructions.append("SPEED V={:.1f}".format(speed))
                        elif instruction == "WAIT":
                            timer = float(options[1])
                            self.trj_instructions.append("TIMER T={:.2f}".format(timer))
                        elif instruction == "RAPID":
                            rapid = True
                            self.trj_instructions.append("SPEED V={:.1f}".format(RAPID_SPEED))
                        elif instruction == "TASK":
                            self.trj_instructions.append("DOUT OG#(12) " + arguments[1])
                        else:
                            print("!!! Unknown instruction in line " + str(line_number) + ": " + line)

                print("Writing main file")
                self.write_main_file(self.main_instructions)

        else:
            print("!!! No corresponding file to: " + input_path)

        # display calculation time
        toc = time.perf_counter()
        delay = toc - tic
        print("Calculation time: " + str(toc))