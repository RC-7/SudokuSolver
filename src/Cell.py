

class Cell:
    def __init__(self, cell_value, row, column, block):
        self.value = cell_value
        self.possible_values = []
        self.row = row
        self.column = column
        self.block = block

    def set_possible_values(self, possible_values):
        if self.value != 0:
            raise "Set cell can't have possible value"

        self.possible_values = possible_values
