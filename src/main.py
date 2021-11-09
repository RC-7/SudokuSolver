from src.SudokuPuzzle import SudokuPuzzle


def main():
    sp = SudokuPuzzle('200', False)
    sp.create_board()
    sp.solve_puzzle()


if __name__ == "__main__":
    main()
