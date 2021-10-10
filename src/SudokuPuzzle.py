import numpy as np
from src.Util import Util
from src.Util import view_image
from src.DigitClassifier import DigitClassifier
from src.Cell import Cell
from tensorflow.keras.preprocessing.image import img_to_array


class SudokuPuzzle:
    def __init__(self, puzzle_name, debug=False):
        self.util = Util(debug)
        self.util.set_puzzle(puzzle_name)
        self.puzzle_image = self.util.read_image()
        self.util.process_image()
        [self.board_contours, self.cell_contours] = self.util.get_contours()
        self.cell_images = self.util.get_cell_images()
        self.digit_classifier = DigitClassifier(False)
        self.debug = debug
        self.cell_objects = []

    def create_board(self):
        puzzle_values = []
        for cell in self.cell_images:
            image = cell
            cell = cell.astype('float') / 255.0
            cell = img_to_array(cell)
            cell = np.expand_dims(cell, axis=0)
            average_pixel = np.average(cell)
            if np.greater(average_pixel, 0.01):
                prediction = self.digit_classifier.predict_digits(cell)
                puzzle_values.append(prediction)
            else:
                puzzle_values.append(0)
            if self.debug:
                view_image(image)
                print(average_pixel)

        cell_objects = []
        cell_row = 0
        cell_column = 0
        cell_block = 0
        lowest_cell_block = 0
        for cell in puzzle_values:
            cell_objects.append(Cell(cell, cell_row, cell_column, cell_block))
            if cell_column == 8 and (cell_row + 1) % 3 == 0:
                cell_block += 1
                lowest_cell_block = cell_block
            if cell_column == 8:
                cell_row += 1
                cell_column = 0
                cell_block = lowest_cell_block
            elif (cell_column + 1) % 3 == 0 and cell_column != 8:
                cell_block += 1
                cell_column += 1
            else:
                cell_column += 1
        self.cell_objects = cell_objects

    def get_possible_value(self):
        for cell in self.cell_objects:
            # x + y*3
            if cell.value != 0:
                continue
            possible_values = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            for cell_compare in self.cell_objects:
                if cell == cell_compare or cell_compare.value == 0:
                    continue
                if cell.row == cell_compare.row or cell.column == cell_compare.column\
                        or cell.block == cell_compare.block:
                    try:
                        possible_values.remove(cell_compare.value)
                    except:
                        pass
                    if len(possible_values) == 0:
                        return False
            cell.possible_values = possible_values
        return True

    def fill_in_certainties(self):
        unsolved_cells = 0
        for i in range(len(self.cell_objects)):
            # print(self.cell_objects[i].possible_values)
            if len(self.cell_objects[i].possible_values) == 1:
                self.cell_objects[i].value = self.cell_objects[i].possible_values[0]
                self.cell_objects[i].possible_values = []
                continue
            if len(self.cell_objects[i].possible_values) > 0:
                unsolved_cells += 1
        return unsolved_cells

    def solve_puzzle(self):
        valid_board = self.get_possible_value()
        if not valid_board:
            raise "Invalid board, there is a cell without a valid solution"
        unsolved = self.fill_in_certainties()
        unsolved_previous = 0
        while unsolved != 0 and valid_board:
            valid_board = self.get_possible_value()
            unsolved = self.fill_in_certainties()
            if unsolved == unsolved_previous:
                print('No certain moves left ...')
                print(unsolved)
            unsolved_previous = unsolved
        self.util.annotate_board(self.cell_objects)



