import random

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
        self.guesses = []

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

    def check_board(self):
        for cell in self.cell_objects:
            if cell.value == 0:
                continue
            for cell_compare in self.cell_objects:
                if cell == cell_compare or cell_compare.value == 0:
                    continue
                if cell.row == cell_compare.row or cell.column == cell_compare.column\
                        or cell.block == cell_compare.block:
                    if cell.value == cell_compare.value:
                        return False
        return True

    def check_cells(self):
        self.get_possible_value()
        for cell in self.cell_objects:
            if cell.value != 0:
                continue
            for cell_compare in self.cell_objects:
                if cell_compare.value != 0:
                    continue
                if cell == cell_compare:
                    continue
                if cell.row == cell_compare.row or cell.column == cell_compare.column\
                        or cell.block == cell_compare.block:
                    if len(cell.possible_values) == 1 and len(cell_compare.possible_values) == 1:
                        if cell.possible_values[0] == cell_compare.possible_values[0]:
                            return False
        return True

    def fill_in_certainties(self, pencil=False):
        unsolved_cells = 0
        solved_indexes = []
        for i in range(len(self.cell_objects)):
            if len(self.cell_objects[i].possible_values) == 1:
                self.cell_objects[i].value = self.cell_objects[i].possible_values[0]
                self.cell_objects[i].possible_values = []
                solved_indexes.append(i)
                continue
            if len(self.cell_objects[i].possible_values) > 0 and self.cell_objects[i].value == 0:
                unsolved_cells += 1

        if pencil:
            return [unsolved_cells, solved_indexes]
        return unsolved_cells

    def guess_value(self):
        index_to_guess = 0
        lowest_uncertainty = 9
        indices = list(range(len(self.cell_objects)))
        random.shuffle(indices)
        for i in indices:
            uncertainty = len(self.cell_objects[i].possible_values)
            if not self.cell_objects[i].guessing and self.cell_objects[i].value == 0 and uncertainty > 1:
                if uncertainty == 2:
                    index_to_guess = i
                    break
                if uncertainty < lowest_uncertainty:
                    index_to_guess = i
                    lowest_uncertainty = uncertainty
        self.cell_objects[index_to_guess].value = self.cell_objects[index_to_guess].possible_values[0]
        self.cell_objects[index_to_guess].guessing = True
        return [index_to_guess, self.cell_objects[index_to_guess].possible_values, 0]

    def iterate_guess(self):
        self.get_possible_value()
        index = self.guesses[len(self.guesses) - 1][0]
        new_guess_number = self.guesses[len(self.guesses) - 1][2] + 1
        if new_guess_number >= len(self.guesses[len(self.guesses) - 1][1]):
            self.guesses[len(self.guesses) - 1][2] += 1
            return False
        new_guess = self.guesses[len(self.guesses) - 1][1][new_guess_number]
        self.guesses[len(self.guesses) - 1][2] = new_guess_number
        self.cell_objects[index].value = new_guess
        valid_board = self.get_possible_value() and self.check_board() and self.check_cells()
        return valid_board

    def erase_solutions_from_guess(self, indices):
        for solved in indices:
            for solved_index in solved:
                self.cell_objects[solved_index].value = 0
        self.get_possible_value()
        return []

    # Checks if cleanup is needed and cleans last guess made
    def erase_guess(self):
        index = len(self.guesses) - 1
        if self.guesses[index][2] >= len(self.guesses[len(self.guesses) - 1][1]):
            self.cell_objects[self.guesses[index][0]].value = 0
            self.cell_objects[self.guesses[index][0]].guessing = False
            self.guesses.pop()
            self.get_possible_value()
            return True
        else:
            return False

    def solve_with_pencil(self):
        solved_for_guess = []
        guess_information = self.guess_value()
        self.guesses.append(guess_information)
        unsolved_previous = 0
        unsolved = 50

        while unsolved != 0:
            valid_board = self.get_possible_value()
            valid_board = valid_board and self.check_board() and self.check_cells()
            if not valid_board:
                while not valid_board:
                    solved_for_guess = self.erase_solutions_from_guess(solved_for_guess)
                    valid_board = self.iterate_guess()
                    if self.erase_guess():
                        return False
            self.get_possible_value()
            [unsolved, solved_indexes] = self.fill_in_certainties(True)
            if len(solved_indexes) >= 1:
                solved_for_guess.append(solved_indexes)
            if unsolved == unsolved_previous:
                self.get_possible_value()
                solved = self.solve_with_pencil()
                if not solved:
                    solved_for_guess = self.erase_solutions_from_guess(solved_for_guess)
                    self.iterate_guess()
                    if self.erase_guess():
                        return False
                    unsolved_previous = 100
                if solved and unsolved == 0:
                    return True
            else:
                unsolved_previous = unsolved
        self.guesses.pop()
        return True

    def determine_number_permutations(self):
        permutations = 1
        for i in range(len(self.cell_objects)):
            if self.cell_objects[i].value == 0:
                permutations *= len(self.cell_objects[i].possible_values)
        return permutations

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
                solved = self.solve_with_pencil()
                if solved:
                    break
            unsolved_previous = unsolved
        self.util.annotate_board(self.cell_objects, True)



