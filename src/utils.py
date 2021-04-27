import json

class Utils:

    @staticmethod
    def is_valid_input(input_dict):
        """
        Validates the input dictionary
        """
        if input_dict:
            print('utils.py: input_dict validated successfully')
            return True

        print('utils.py: input_dict validation failed')
        return False

    @staticmethod
    def get_input_dict_from_input_file(file_path):
        """
        Get dictionary from input file
        """
        input_dict = None
        with open(file_path, 'r') as fp:
            input_dict = json.load(fp)

        if Utils.is_valid_input(input_dict):
            return input_dict

        print('utils.py: Error: Input validation failed returning None')
        return input_dict

    @staticmethod
    def get_parsed_instruction(instruction):
        """
        Removes string till first underscore
        "1_instruction_one" --> "instruction_one"
        """
        first_underscore = instruction.find('_')
        if first_underscore != -1:
            return instruction[first_underscore + 1:]

        return instruction

    @staticmethod
    def get_tildes():
        return ('~' * 90)

    @staticmethod
    def print_sub_banner(heading):
        tildes = Utils.get_tildes()
        centered_heading = Utils.get_centered_text(heading)
        print("%s\n%s\n%s\n" % (tildes, centered_heading, tildes), end='')

    @staticmethod
    def get_dashes():
        return ('-' * 90)

    @staticmethod
    def get_centered_text(heading):
        spaces = ' ' * (45 - len(heading) // 2)
        return (spaces + heading)

    @staticmethod
    def print_banner(heading):
        dashes = Utils.get_dashes()
        centered_heading = Utils.get_centered_text(heading)
        print("%s\n%s\n%s\n" % (dashes, centered_heading, dashes), end='')
