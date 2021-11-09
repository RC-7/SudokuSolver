

class Cell:
    def __init__(self, cell_value, row, column, block):
        self.value = cell_value
        self.possible_values = []
        self.row = row
        self.column = column
        self.block = block
        self.set_value = cell_value != 0
        self.pencil_value = 0
        self.guessing = False
        # self.based_on

