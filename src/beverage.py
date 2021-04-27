import copy
import traceback
from collections import defaultdict


class Beverage:
    """
    Defines how a beverage needs to be stored
    """
    def __init__(self, name, ingredient_quantity_dict, prep_time=7):

        # Name of beverage
        self.name = name

        # Dict to hold recipe i.e. ingredients and their quantities requied to prep beverage
        # A new ingredient which is not present should automatically have quantity as 0
        self.ingredient_quantity_dict = defaultdict(lambda: 0, ingredient_quantity_dict)

        # Preparation time in seconds
        self.prep_time = prep_time

    @property
    def ingredient_quantity_dict(self):
        """
        Returns copy of recipe so that it cannot be altered
        """
        return copy.deepcopy(self.__ingredient_quantity_dict)

    @ingredient_quantity_dict.setter
    def ingredient_quantity_dict(self, new_ingredient_quantity_dict):
         """
         Stores of copy of recipe dictionary provided
         """
         self.__ingredient_quantity_dict = defaultdict(lambda: 0, new_ingredient_quantity_dict)


# Unit Tests
def run_tests():

    bev_name = 'Coffee'
    bev_ingredient_quantity_dict = {
        'Water': 20,
        'Coffee Syrup': 40,
        'Hot Milk': 20,
    }

    coffee = Beverage(bev_name, bev_ingredient_quantity_dict)

    if bev_name != coffee.name:
        print('Test Failed: Mismatch in beverage name')
    else:
        print('Check passed: Beverage Name check passed')

    if bev_ingredient_quantity_dict != coffee.ingredient_quantity_dict:
        print('Test Failed: Mismatch in beverage ingredient_quantity_dict')
    else:
        print('Check passed: Beverage ingredient_quantity_dict check passed')

    if id(bev_ingredient_quantity_dict) == id(coffee.ingredient_quantity_dict):
        print('Test Failed: Object should store copy of beverage ingredient_quantity_dict')
    else:
        print('Check passed: Object stores copy of beverage ingredient_quantity_dict')

    bev_ingredient_quantity_dict['Sugar'] = 2
    coffee.ingredient_quantity_dict = bev_ingredient_quantity_dict

    if coffee.ingredient_quantity_dict != bev_ingredient_quantity_dict:
        print('Test Failed: Mismatch while updating ingredient_quantity_dict')
    else:
        print('Check passed: Update ingredient_quantity_dict check passed')


    if id(bev_ingredient_quantity_dict) == id(coffee.ingredient_quantity_dict):
        print('Test Failed: Object should store copy of beverage ingredient_quantity_dict')
    else:
        print('Check passed: Object stores copy of beverage ingredient_quantity_dict')

# If this script is ran as standalone, run tests
if __name__ == '__main__':
    try:
        run_tests()
    except:
        traceback.print_exc()
