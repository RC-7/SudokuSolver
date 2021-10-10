

class Cell:
    def __init__(self, cell_value):
        self.value = cell_value
        self.possible_values = []

    def set_possible_values(self, possible_values):
        if self.value != 0:
            raise "Set cell can't have possible value"

        self.possible_values = possible_values
