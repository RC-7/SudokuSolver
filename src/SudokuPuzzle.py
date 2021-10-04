from src.Util import Util
from src.Util import view_image


class SudokuPuzzle:
    def __init__(self, puzzle_name, debug=False):
        self.util = Util(debug)
        self.util.set_puzzle('1')
        self.puzzle_image = self.util.read_image()
        self.util.process_image()
        [self.board_contours, self.cell_contours] = self.util.get_contours()
        # self.cell_images = self.util.get_cell_images()

    def viewCells(self):
        for cell in self.cell_images:
            view_image(cell)
