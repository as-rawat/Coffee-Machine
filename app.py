import time
import argparse
import traceback

from src.utils import Utils
from src.coffee_machine import CoffeeMachine

app_description = """
    Coffee Machine: A Coffee Machine Simulator, It tries to brew beverages using their recipe and
                    ingredients provided.

    Note: To stop the machine, just enter "stop" without quotes in stdin and hit return.
"""

input_json_help = """
A json file which carries follwing details:-
* Machine Specification details, like number of outlets
* Instructions to be performed, these can be of 2 types:-
    1. *_total_items_quantity: This will be used to add ingredients to Coffee Machine
    2. *_beverages: This will have objects of beverages to be brewed with their recipe
    In the above 2 line '*' need to be replace with the instruction number.

For an Example please check out input_json files present in tests/ directory.
"""

def parse_args():
    """
    Parses the input arguments provided by user
    """
    parser = argparse.ArgumentParser(description=app_description,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--input-json", dest="input_json_path", required=True,
                        help=input_json_help)

    args = parser.parse_args()
    return args


if __name__ == '__main__':

    # Parse input from input_json_file into a dictionary
    args = parse_args()
    if args is None:
        print('app.py: Failed parsing arguments')
        exit(1)

    # Validate and parse input_file
    input_dict = Utils.get_input_dict_from_input_file(args.input_json_path)
    if input_dict is None:
        print('app.py: Failed parsing input file')
        exit(2)

    # Get Outlet count
    outlet_count = input_dict['machine']['outlets']['count_n']
    if outlet_count < 1:
        print('app.py: Atleast 1 outlet is needed')
        exit(1)
    del input_dict['machine']['outlets']

    # Instantiate and Start Coffee Machine
    coffee_machine = CoffeeMachine(outlet_count)
    coffee_machine.start()

    # Use the parsed input_json_file to give instructions to Coffee Machine
    for instruction, dict in input_dict['machine'].items():

        # Increase sleep for better simulation
        time.sleep(1)

        Utils.print_banner(instruction)
        parsed_instruction = Utils.get_parsed_instruction(instruction)
        print('app.py: Prased Instruction: %s' % (parsed_instruction))
        if 'total_items_quantity' == parsed_instruction:
            coffee_machine.add_ingredient_by_dict(dict)
        elif 'beverages' == parsed_instruction:
            coffee_machine.add_beverage_from_beverage_dict(dict)


    # Enter 'stop' in stdin and hit return to stop the Machine
    stop = False
    while not stop:
        word = input()
        stop = (word == 'stop')

    # Stop the machine and exit
    coffee_machine.stop()
