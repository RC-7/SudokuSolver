import numpy as np
from src.Util import Util
from src.Util import view_image
from src.DigitClassifier import DigitClassifier
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

    def predict_puzzle(self):
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

    def view_cells(self):
        for cell in self.cell_images:
            view_image(cell)
