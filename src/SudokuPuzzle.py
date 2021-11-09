import itertools
import random

import numpy as np
from src.Util import Util
from src.Util import view_image
from src.DigitClassifier import DigitClassifier
from src.Cell import Cell
from tensorflow.keras.preprocessing.image import img_to_array
from itertools import chain, combinations


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
            if cell.value != 0:
                continue
            for cell_compare in self.cell_objects:
                if cell == cell_compare or cell_compare.value == 0:
                    continue
                if cell.row == cell_compare.row or cell.column == cell_compare.column\
                        or cell.block == cell_compare.block:
                    if cell.value == cell_compare.value:
                        print('Oh no')
                        return False
        return True

    def check_cells(self):
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
                    # print('---------------')
                    # print(cell.possible_values)
                    # print(cell_compare.possible_values)
                    # print('---------------')
                    if len(cell.possible_values) == 1 and len(cell_compare.possible_values) == 1:
                        if cell.possible_values[0] == cell_compare.possible_values[0]:
                            print('Oh no')
                            return False
        return True

    def fill_in_certainties(self, pencil=False):
        unsolved_cells = 0
        solved_indexes = []
        # Need to account for multiple in same row/column!
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
        # lowest_uncertainty = 2
        index_to_guess = 0
        lowest_uncertainty = 9
        # valid_board = self.get_possible_value()
        indices = list(range(len(self.cell_objects)))
        random.shuffle(indices)
        for i in indices:
            uncertainty = len(self.cell_objects[i].possible_values)
            # print('index inside ' + str(i))
            # print('index inside ' + str(self.cell_objects[i].guessing))
            # print('index inside ' + str(self.cell_objects[i].value))
            # print('index inside ' + str(uncertainty))
            if not self.cell_objects[i].guessing and self.cell_objects[i].value == 0 and uncertainty > 1:
                if uncertainty == 2:
                    index_to_guess = i
                    # print('index inside' + str(index_to_guess))
                    break
                if uncertainty < lowest_uncertainty:
                    index_to_guess = i
                    # print('index inside' + str(index_to_guess))
                    lowest_uncertainty = uncertainty
            # print('index' + str(index_to_guess))
        self.cell_objects[index_to_guess].value = self.cell_objects[index_to_guess].possible_values[0]
        self.cell_objects[index_to_guess].guessing = True
        # remove possible value
        return [index_to_guess, self.cell_objects[index_to_guess].possible_values, 0]
        # return False

    def iterate_guess(self):
        print('guesses iterate')
        self.get_possible_value()
        print(self.guesses)
        index = self.guesses[len(self.guesses) - 1][0]
        new_guess_number = self.guesses[len(self.guesses) - 1][2] + 1
        print('iterating')
        # print(self.guesses)
        # print(self.guesses[len(self.guesses) - 1])
        # print(self.cell_objects[index].possible_values)
        # print(len(self.cell_objects[index].possible_values))
        # self.guesses[len(self.guesses) - 1][2] += 1
        # guess_number += 1
        # Need to update the possible values with the value ...
        # self.get_possible_value()
        if new_guess_number >= len(self.cell_objects[index].possible_values):
            self.guesses[len(self.guesses) - 1][2] += 1
            return False
        print('here.....' + str(self.guesses[len(self.guesses) - 1][1]))
        print('here GN.....' + str(new_guess_number))
        new_guess = self.guesses[len(self.guesses) - 1][1][new_guess_number]
        self.guesses[len(self.guesses) - 1][2] = new_guess_number
        self.cell_objects[index].value = new_guess
        # self.guesses[len(self.guesses) - 1][1] = self.cell_objects[index].value
        valid_board = self.get_possible_value() and self.check_board() and self.check_cells()
        print(valid_board)
        return valid_board


    # Sometimes get's in a weird loop when the base guess or one of them is wrong when backtracking, but then works fine other times, commit a version and look at the recursion
    def solve_pencil(self):
        print('beginning solve')
        solved_for_guess = []
        return_value = self.guess_value()
        # while not return_value:
        #     lowest_uncertainty += 1
        #     return_value = self.guess_value(lowest_uncertainty)
        self.guesses.append(return_value)
        print('guesses entry')
        print(self.guesses)

        unsolved_previous = 0
        # valid_board = self.get_possible_value()
        # [unsolved, solved_indexes] = self.fill_in_certainties(True)
        # self.util.annotate_board(self.cell_objects)
        unsolved = 50
        # if len(solved_indexes) > 0:
        #     # print("solved" + str(solved_indexes))
        #     solved_for_guess.append(solved_indexes)
        # solved_for_guess.append(solved_indexes)
        while unsolved != 0:
            # self.util.annotate_board(self.cell_objects)
            valid_board = self.get_possible_value()
            print('here inside unsolved')
            test = self.check_cells()
            valid_board = valid_board and self.check_board() and test
            print('valid_board')
            print(valid_board)
            if not valid_board:
                while not valid_board:
                    # self.util.annotate_board(self.cell_objects)
                    print('inside not valid')
                    # self.util.annotate_board(self.cell_objects)
                    for solved in solved_for_guess:
                        for solved_index in solved:
                            # print(solved_index)
                            self.cell_objects[solved_index].value = 0
                    print('clearing')
                    # self.util.annotate_board(self.cell_objects)
                    solved_for_guess = []

                    valid_board = self.iterate_guess()
                    # self.util.annotate_board(self.cell_objects)
                    # self.cell_objects[self.guesses[len(self.guesses) - 1][0]].value = 0
                    # self.util.annotate_board(self.cell_objects)
                    index = self.guesses[len(self.guesses) - 1][0]
                    # if self.guesses[len(self.guesses) - 1][2] >= len(self.cell_objects[index].possible_values):
                    if self.guesses[len(self.guesses) - 1][2] >= len(self.guesses[len(self.guesses) - 1][1]):
                        self.cell_objects[self.guesses[len(self.guesses) - 1][0]].value = 0
                        self.cell_objects[self.guesses[len(self.guesses) - 1][0]].guessing = False
                        self.guesses.pop()
                        print('ending one level of recursion')
                        # self.util.annotate_board(self.cell_objects)
                        return False
            # self.util.annotate_board(self.cell_objects)
            [unsolved, solved_indexes] = self.fill_in_certainties(True)
            # self.util.annotate_board(self.cell_objects)
            if len(solved_indexes) > 1:
                solved_for_guess.append(solved_indexes)
            print('Solved for guesses')
            print(solved_for_guess)
            print(unsolved)
            if unsolved == unsolved_previous:
                print('No certain moves left ...')
                print(unsolved)
                print(self.guesses)
                print(solved_for_guess)
                print('inside recursion')
                # self.util.annotate_board(self.cell_objects)
                # print(self.guesses)
                solved = self.solve_pencil()
                print(self.guesses)
                print(solved)
                if not solved:
                    self.iterate_guess()
                    index = self.guesses[len(self.guesses) - 1][0]
                    # if self.guesses[len(self.guesses) - 1][2] >= len(self.cell_objects[index].possible_values):
                    if self.guesses[len(self.guesses) - 1][2] >= len(self.guesses[len(self.guesses) - 1][1]):
                        self.cell_objects[self.guesses[len(self.guesses) - 1][0]].value = 0
                        self.cell_objects[self.guesses[len(self.guesses) - 1][0]].guessing = False
                        self.guesses.pop()
                        print('ending one level of recursion')
                        # self.util.annotate_board(self.cell_objects)
                        return False
                    unsolved_previous = 100
                    print('Iterating base guess')
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
                print('No certain moves left ...')
                print(unsolved)
                print('in solve puzzle')
                solved = self.solve_pencil()
                print(solved)
                if solved:
                    # for cell in self.cell_objects:
                    #     cell.value = cell.pencil_value
                    # self.util.annotate_board(self.cell_objects)
                    # self.util.annotate_board(self.cell_objects)
                    break
            unsolved_previous = unsolved
        print('here')
        self.util.annotate_board(self.cell_objects, True)



