from src.Util import Util
from src.SudokuPuzzle import SudokuPuzzle

sp = SudokuPuzzle('ZoomTest', False)
# sp.viewCells()

# util = Util(False)
# # util.set_puzzle('ZoomTest')
# util.set_puzzle('4')
# util.read_image()
# util.process_image()
# util.get_contours()
#

# cells = util.get_cell_images()
for cell in sp.util.cells:
    sp.util.get_cell_images(cell)
