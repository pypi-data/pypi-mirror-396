import os

import ctypes
from ctypes import cdll, c_int, c_void_p

import tempfile
from sys import platform


class icdr_base:
    input_file = ""
    input_df = None
    input_dir = ""
    output_dir = ""
    icdr_lib = ""

    def __init__(self):
        self.icdr_lib = None

        # Import the FLAGR shared library in PyFLAGR
        if platform == "linux" or platform == "linux2":
            self.icdr_lib = ctypes.CDLL(os.path.dirname(os.path.realpath(__file__)) + "/icdr.so")

        elif platform == "win32":
            self.icdr_lib = ctypes.CDLL(os.path.dirname(os.path.realpath(__file__)) + '/icdr.dll')

        elif platform == "darwin":
            self.icdr_lib = ctypes.CDLL(os.path.dirname(os.path.realpath(__file__)) + "/icdr.dylib")

    # Check the input file or DataFrame that contains the text to be indexed
    def check_get_input(self, f, df):
        status = 0
        if len(f) > 0:
            self.input_file = f
            if not os.path.isfile(self.input_file):
                print("Error! Input file does not exist")
                status = -1

        elif df is not None:
            self.input_file = tempfile.gettempdir() + "/temp_input.csv"
            df.to_csv(self.input_file, index=False, header=False)

        else:
            print("Error! No input data was passed")
            status = -1

        return status

    def check_output_dir(self, path):
        self.output_dir = path
        if not os.path.isdir(self.output_dir):
            try:
                os.mkdir(path)
                return 0
            except FileNotFoundError as X:
                print("Error creating path for writing")
                return 1
        return 0

    def check_input_dir(self, path):
        self.input_dir = path
        if not os.path.isdir(self.input_dir):
            print("The directory '", self.input_dir, "' does noy exist, nothing to read from")
            return 1
        return 0
