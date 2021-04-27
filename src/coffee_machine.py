import time
import traceback
import threading
from enum import Enum
from collections import deque, defaultdict

from src.beverage import Beverage
from src.utils import Utils


class MachineState(Enum):
    """
    Describes states a machine can be in
    """
    RUNNING = 0
    STOPPED = 1

    def __str__(self):
        """
        Returns a string word corresponding to state provided
        """
        enum_to_string = {
            MachineState.RUNNING.value: 'running',
            MachineState.STOPPED.value: 'stopped'
        }

        return enum_to_string[self.value]

class CoffeeMachine:

    def __init__(self, total_outlets=5):

        # State of machine
        self.state = MachineState.STOPPED

        # Number of outlets in machine
        self.outlet = threading.Semaphore(total_outlets)

        # If ingredient count is below this limit, an alert will be be displayed
        self.ingredient_limit = 10

        # Interval between 2 quantity checks
        self.low_quantity_check_interval = 20

        # The ingredients and their quantity currently present in machine
        self.ingredient_container = defaultdict(int)

        # Acquire this while reading/updating ingredient_container
        self.lock_ingredient_container = threading.Lock()

        # Holds the pending beverage which are not handled yet
        self.pending_beverage = deque()

        # Acquire this while reading/updating pending_beverage
        self.lock_pending_beverage = threading.Lock()

    def add_ingredient_by_name_and_quantity(self, ingredient_name, quantity):
        """
        Add 1 ingredient with specified quantity to ingredient_container
        If a negative value is given no change is made
        """
        quantity = 0 if quantity < 0 else quantity
        # Lock inredient container and udate the add quantity to ingredient
        with self.lock_ingredient_container:
            self.ingredient_container[ingredient_name] += quantity
            print('coffee_machine.py: Successfully Added %s, Current Quantity: %d'
                   % (ingredient_name, self.ingredient_container[ingredient_name]))

    def add_ingredient_by_dict(self, ingredient_dict):
        """
        Add 1 or more ingredient(s) to ingredient_container using dictionary of ingredients with the quantity
        to be added
        """
        for ingredient_name, quantity in ingredient_dict.items():
            self.add_ingredient_by_name_and_quantity(ingredient_name, quantity)

    def ingredient_quantity_checker(self):
        """
        A check to throw alerts of some ingredient's quantity is less than limit(defined at init).
        This member function will run in a thread till machine is not stopped.
        """
        while self.state != MachineState.STOPPED:

            # Lock ingredient_container and check for insufficient ingredients using limit
            with self.lock_ingredient_container:
                for ingredient_name, quantity in self.ingredient_container.items():
                    if quantity < self.ingredient_limit:
                        print('coffee_machine.py: Ingredient check failed, Running low on: %s' % (ingredient_name))

            # Sleep for low_quantity_check_interval or break out if machine is stopped
            for i in range(self.low_quantity_check_interval):
                time.sleep(1)
                if self.state == MachineState.STOPPED:
                    break

    def picked_required_ingredients(self, ingredient_quantity_dict):
        """
        Check if all the ingredients with specified quantity in ingredient_quantity_dict
        can be picked or not. If the can be picked, pick all the required ingredients
        """
        all_ingredients_can_be_picked = True
        with self.lock_ingredient_container:

            # Check if all the ingredients can be picked
            for ingredient_name, quantity in ingredient_quantity_dict.items():
                if self.ingredient_container[ingredient_name] < quantity:
                    all_ingredients_can_be_picked = False
                    print('coffee_machine.py: Insufficient ingredient: %s, Required Quantity: %d, Found Quantity: %d'
                          % (ingredient_name, quantity, self.ingredient_container[ingredient_name]))
                    break

            # If they can be picked, pick all specified in ingredient_quantity_dict
            if all_ingredients_can_be_picked:
                for ingredient_name, quantity in ingredient_quantity_dict.items():
                    self.ingredient_container[ingredient_name] = self.ingredient_container[ingredient_name] - quantity

        return all_ingredients_can_be_picked

    def brew(self, beverage):
        """
        Every beverage will come here to get brewed.
        """
        print('coffee_machine.py: Brewing [%s]...' % (beverage.name))
        print('coffee_machine.py: Checking for ingredients...')

        # Try to pick beverage recipe ingredients
        if not self.picked_required_ingredients(beverage.ingredient_quantity_dict):
            # Insufficient quantity skip the beverage
            Utils.print_sub_banner('coffee_machine.py: Skipping brewing [%s]' % (beverage.name))
            return

        # Wait till a outlet gets free and then use it to brew
        self.outlet.acquire()
        try:
            print('coffee_machine.py: Started brewing [%s]' % (beverage.name))

            for i in range(beverage.prep_time):
                time.sleep(1)
                if self.state == MachineState.STOPPED:
                    raise Exception('Brewing was in progress, machine stopped abruptly')

            Utils.print_sub_banner('coffee_machine.py: [%s] brewed successfully' % (beverage.name))
        except:
            Utils.print_sub_banner('coffee_machine.py: ERROR: Brewing [%s] Failed' % (beverage.name))
            traceback.print_exc()
        finally:
            # Always release
            self.outlet.release()

    def add_beverage(self, beverage):
        """
        Add beverage to in pending list for brewing
        """
        with self.lock_pending_beverage:
            self.pending_beverage.append(beverage)
            print('coffee_machine.py: Successfully added [%s] to pending beverage list' % (beverage.name))


    def add_beverage_from_beverage_dict(self, beverage_dict):
        """
        Add 1 or more beverage(s) using beverage_dict which has a dictionay of beverages,
        with beverage name as key and recipe(i.e ingredient quantity dict) as value
        """
        for beverage_name, ingredient_quantity_dict in beverage_dict.items():
            print('coffee_machine.py: Sending beverage [%s] to pending beverage list' % (beverage_name))
            beverage = Beverage(beverage_name, ingredient_quantity_dict)
            self.add_beverage(beverage)

    def is_any_beverage_pending(self):
        """
        If pending_beverage is empty no beverage is pending
        """
        return len(self.pending_beverage) != 0

    def get_first_pending_beverage(self):
        """
        Get the first beverage in First Come First Serve fashion
        """
        beverage = None
        with self.lock_pending_beverage:
            beverage = self.pending_beverage.popleft()

        print('coffee_machine.py: Taking beverage [%s] for processing' % (beverage.name))
        return beverage

    def coffee_machine_controller(self):
        """
        This member will run in a thread till machine is stopped
        It will take care of starting ingredient quantity checker
        and taking beverage out from pending beverage and brewing them.
        """
        self.state = MachineState.RUNNING
        print('coffee_machine.py: Coffee Machine is %s...' % str(self.state))
        print('coffee_machine.py: Starting ingredient quantity checker...')
        # Start ingredient quantity checker thread
        ingredient_quantity_checker_thread = threading.Thread(target=self.ingredient_quantity_checker, args=())
        ingredient_quantity_checker_thread.start()
        #Continue till machine is stopped
        while self.state != MachineState.STOPPED:

            # Check for pending beverage
            if self.is_any_beverage_pending():
                # Take a pending beverage out and try brewing it
                beverage = self.get_first_pending_beverage()
                print('coffee_machine.py: Started processing beverage [%s]' % (beverage.name))
                brew_thread = threading.Thread(target=self.brew, args=(beverage,))
                brew_thread.start()

        print('coffee_machine.py: Coffee Machine is now %s' % str(self.state))

    def start(self):
        """
        Changes the state of machine and start machine controller thread.
        """
        if self.state == MachineState.STOPPED:
            coffee_machine_thread = threading.Thread(target=self.coffee_machine_controller)
            coffee_machine_thread.start()

    def stop(self):
        """
        Stops the machine.
        """
        self.state = MachineState.STOPPED
