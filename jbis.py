import time
import os
import os.path
import math
from datetime import datetime
from sys import platform

FILE_EXTENSION = "JBI"
RAPID_SPEED = 50

END_OF_LINE = ''


class Point:
    def __init__(self, x, y, z, i, j, k):
        self.x = x
        self.y = y
        self.z = z
        self.i = i
        self.j = j
        self.k = k


def define_eol():
    global END_OF_LINE
    if platform == "linux" or platform == "linux2":
        END_OF_LINE = '\r\n'
    elif platform == "darwin":
        print("!!!! no yet implemented !!!!")
    else:
        END_OF_LINE = '\n'


def write_lines(output_path, lines):
    with open(output_path, 'w') as output_file:
        for line in lines:
            output_file.write(line + END_OF_LINE)


class Jbi:

    def format_angles(self, points):
        lines = []
        for i, point in enumerate(points):
            point, self.previous_B = point.write_angle(i)
            lines.append(point)
        return lines

    def format_points(self, points):
        point_lines = []
        angle_lines = []
        A = 0
        B = 0
        for i, point in enumerate(points):
            if self.with_B or self.with_A:
                B = self.calculate_B(point)
            point_lines.append(self.write_point(i, point))
            if self.with_B or self.with_A:
                if self.with_A:
                    A = self.calculate_A(point)
                angle_line = self.write_angle(i, A, B)
                angle_lines.append(angle_line)
        return point_lines, angle_lines

    def calculate_A(self, point):
        i_turn = point.i * math.cos(math.radians(self.previous_B)) - point.j * math.sin(math.radians(self.previous_B))
        k_turn = point.k
        A = math.degrees(math.atan(i_turn / k_turn))
        return A

    def write_point(self, number, point):

        i_turn = point.i * math.cos(math.radians(self.previous_B)) - point.j * math.sin(math.radians(self.previous_B))
        j_turn = point.i * math.sin(math.radians(self.previous_B)) + point.j * math.cos(math.radians(self.previous_B))
        k_turn = point.k

        if self.with_B and not self.with_A:
            Rx = -math.degrees(math.atan2(j_turn, k_turn))
            Ry = math.degrees(math.atan(i_turn / k_turn))
        elif self.with_A:
            Rx = -math.degrees(math.atan2(j_turn, k_turn))
            Ry = math.degrees(math.atan(i_turn / k_turn))
        else:
            Rx = -math.degrees(math.atan2(point.j, point.k))
            Ry = math.degrees(math.atan(point.i / point.k))

        return "C" + str(number).zfill(5) + "=""{:.3f}".format(point.x) + "," + "{:.3f}".format(
            point.y) + "," + "{:.3f}".format(point.z) \
               + "," + "{:.4f}".format(Rx) + "," + "{:.4f}".format(Ry) + "," + "{:.4f}".format(-self.previous_B)

    def calculate_B(self, point):
        angle = math.degrees(math.atan2(point.x, point.y)) + self.initial_B
        if angle < 0:
            angle += 360
        previous_short_angle = self.previous_B % 360

        delta = angle - previous_short_angle
        if delta < -180:
            delta += 360
        B = self.previous_B + delta
        self.previous_B = B
        return B

    def write_angle(self, number, A, B):
        return "EC" + str(number).zfill(5) + "=""{:.4f}".format(A) + ",""{:.4f}".format(B)

    def intro(self, point_nb, name):
        lines = ["/JOB"]

        lines.append("//NAME " + name)
        lines.append("///FOLDERNAME " + self.folder_name)
        lines.append("//POS")
        if self.with_B:
            lines.append("///NPOS " + str(point_nb) + ",0," + str(point_nb) + ",0,0,0")
        else:
            lines.append("///NPOS " + str(point_nb) + ",0,0,0,0,0")
        lines.append("///TOOL 7")
        lines.append("///POSTYPE ROBOT")
        lines.append("///RECTAN")
        lines.append("///RCONF 1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
        return lines

    def intro_trj(self, point_nb, name):
        lines = ["/JOB"]

        lines.append("//NAME " + name)
        lines.append("///FOLDERNAME " + self.folder_name)
        lines.append("//POS")
        if self.with_B:
            lines.append("///NPOS " + str(point_nb) + ",0," + str(point_nb) + ",0,0,0")
        else:
            lines.append("///NPOS " + str(point_nb) + ",0,0,0,0,0")
        lines.append("///USER 2")
        lines.append("///TOOL 7")
        lines.append("///POSTYPE USER")
        lines.append("///RECTAN")
        lines.append("///RCONF 1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
        return lines

    def write_trj_file(self):
        path = self.output_path + "TRJ" + str(self.trj_part) + "." + FILE_EXTENSION
        name = os.path.splitext(os.path.basename(path))[0]
        lines = self.intro_trj(len(self.points), name)

        points, angles = self.format_points(self.points)
        lines.extend(points)

        if self.with_B:
            lines.append("///TOOL 0")  # outil de la main gauche
            lines.append("///POSTYPE ANGLE")
            lines.append("///ANGLE")
            lines.extend(angles)
        lines.append("//INST")
        now = datetime.now()  # current date and time
        lines.append("///DATE " + now.strftime("%Y/%m/%d %H:%M"))
        lines.append("///COMM")
        lines.append("///ATTR SC,RW,RJ")
        lines.append("////FRAME USER 2")
        lines.append("///GROUP1 RB1")
        if self.with_B:
            lines.append("///GROUP2 ST1")
        lines.append("NOP")
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
        name = os.path.basename(self.output_path)
        lines = self.intro(0, name)
        lines.append("//INST")
        lines.append("///DATE 2021/02/10 13:51")
        lines.append("///COMM")
        lines.append("///ATTR SC,RW,RJ")
        lines.append("////FRAME USER 2")
        lines.append("///GROUP1 RB1")
        if self.with_B:
            lines.append("///GROUP2 ST1")
        lines.append("NOP")
        lines.append("CALL JOB:DEBUT")
        lines.extend(instructions)
        lines.append("CALL JOB:FIN")
        lines.append("END")
        path = self.output_path + "." + FILE_EXTENSION
        write_lines(path, lines)
        self.files.append(path)

    def __init__(self, folder_name, with_B, with_A=False, initial_B=0, lines=None, output_path="", input_path=""):
        """

        :param folder_name: folder name for programm on the robot
        :type folder_name: string
        :param with_B: true if you want to use B axe
        :type with_B: bool
        :param with_A: true if you want to use A axe
        :type with_A: bool
        :param initial_B: initial position of the torch on B axes (only used if with_B is true)
        :type initial_B: float
        :param lines: APT instruction lines : used if you want to directly send APT instruction line (for example from Rhino)
        :type lines: list of string
        :param output_path: path where to sage the restult (must be a file path) only need if you send APT instruction lines
        :type output_path: string
        :param input_path: path for the APT file : only need if you do not want to send APT instruction line but read them in a file
        :type input_path: sting
        """
        define_eol()

        self.with_B = with_B
        self.with_A = with_A
        self.folder_name = folder_name
        self.initial_B = initial_B
        self.previous_B = 0
        if output_path is not None and lines is not None:
            self.output_path = os.path.splitext(output_path)[0]
            self.translate_lines(lines)
        elif input_path is not None:
            self.output_path = os.path.splitext(input_path)[0]
            self.read_file(input_path)
        else:
            print("!!! error in constructor parameters")

        print("Output path: " + self.output_path)

    def read_file(self, input_path):
        # time calculation monitoring
        tic = time.perf_counter()

        print("Input path: " + input_path)

        if os.path.isfile(input_path):
            with open(input_path, 'r') as file:
                lines = file.readlines()
                self.translate_lines(lines)
        else:
            print("no corresponding file to: " + input_path)

        # display calculation time
        toc = time.perf_counter()
        delay = toc - tic
        print("Calculation time: " + str(toc))

    def translate_lines(self, lines):
        self.files = []
        self.points = []
        self.main_instructions = []
        self.trj_part = 0
        self.trj_instructions = []
        rapid = False
        for line_number, line in enumerate(lines):
            line = line.rstrip()
            if len(line) == 0:
                print("Empty line")

            elif line[0] == "$" and line[1] == "$":
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
                    if self.with_B:
                        self.trj_instructions.append("SMOVL C" + str(len(self.points) - 1).zfill(5)
                                                     + " +MOVJ EC" + str(len(self.points) - 1).zfill(5))
                    else:
                        self.trj_instructions.append("MOVL C" + str(len(self.points) - 1).zfill(5))
                    if rapid:
                        rapid = False
                    if len(self.points) > 1999:
                        self.write_trj_file()

                elif instruction == "FEEDRATE":
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
