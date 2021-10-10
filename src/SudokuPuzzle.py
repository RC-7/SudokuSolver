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

    def get_block_values(self, index):
        pass

    def get_row_values(self, row_index):
        pass


    def get_possible_value(self):
        for cell in self.cell_objects:
            # x + y*3
            if cell.value != 0:
                continue
            possible_values = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            index = self.cell_objects.index(cell)
            block = index % 9



    def view_cells(self):
        for cell in self.cell_images:
            view_image(cell)
