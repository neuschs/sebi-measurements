import argparse
from pymeasure.adapters import PrologixAdapter, VISAAdapter

parser = argparse.ArgumentParser(
                    prog='Advantest Basic Loader',
                    description='Loads the given BASIC program to the ATE scratch pad.'
                                'Start the editor on the R3265A with "Controller Start" button.'
                                'Execute this script afterwards.'
                                'ATTENTION! This deletes the current loaded buffer.'
                                ''
                                'Example (prologix): advantest_r3265a_load_basic_file.py -r ASRL7::INSTR -pg 10 TEST.BAS'
                                'Example (NI GPIB): advantest_r3265a_load_basic_file.py -r GPIB0::10::INSTR TEST.BAS')

parser.add_argument('filename', type=str, help='Path to the BASIC file', required=True)
parser.add_argument('-r', '--resource_string', type=str, help='Resource string like "GPIB0::10::INSTR" or "ASRL7::INSTR" for prologix.', required=True)
parser.add_argument('-pg', '--prologix', type=int, help='GPIB Address for prologix based mode, implicitly switches to prologix mode.')


args = parser.parse_args()
adapter = object
if args.prologix is not None:
    adapter = PrologixAdapter(args.ressource_string)

adapter.write("SCRATCH\r\n")
adapter.write("LOAD START\r\n")

with open(args.filename) as file:
    for line in file.readlines():
        adapter.write(line)

adapter.write("LOAD END\r\n")