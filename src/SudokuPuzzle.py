from src.Util import Util
from src.Util import view_image
from src.DigitClassifier import DigitClassifier


class SudokuPuzzle:
    def __init__(self, puzzle_name, debug=False):
        self.util = Util(debug)
        self.util.set_puzzle(puzzle_name)
        self.puzzle_image = self.util.read_image()
        self.util.process_image()
        [self.board_contours, self.cell_contours] = self.util.get_contours()
        self.cell_images = self.util.get_cell_images()

        self.digit_classifier = DigitClassifier(False)

    def view_cells(self):
        for cell in self.cell_images:
            view_image(cell)
