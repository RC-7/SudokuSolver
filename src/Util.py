import json
import cv2
import numpy as np


def read_label(puzzleNumber):
    filename = "../data/Labels/Puzzle" + puzzleNumber + ".json"
    label_file = open(filename)
    labels = json.load(label_file)['puzzleLabel']
    return labels

def view_image(image):
    cv2.imshow("Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


class Util:
    def __init__(self, debug=False):
        self.contoursOriginal = []
        self.cells = []
        self.contoursBoard = []
        self.original = []
        self.board = []
        self.labels = []
        self.debug = debug
        self.puzzle_name = "Puzzle1"

    def set_puzzle(self, puzzleNumber):
        self.puzzle_name = "Puzzle" + puzzleNumber

    def read_label(self):
        filename = "../data/Labels/" + self.puzzle_name + ".json"
        label_file = open(filename)
        labels = json.load(label_file)['puzzleLabel']
        self.labels = labels

    def read_image(self):
        filename = "../data/Images/" + self.puzzle_name + ".jpg"
        original = cv2.imread(filename)
        self.original = cv2.resize(original, (700, 960))
        if self.debug:
            view_image(self.original)

    def process_image(self):
        pass

    def get_cells(self):
        pass

    def get_board(self):
        pass

