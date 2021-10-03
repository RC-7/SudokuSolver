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
    # cv2.destroyAllWindows()


class Util:
    def __init__(self, debug=False):
        self.contoursOriginal = []
        self.cells = []
        self.contoursBoard = []
        self.original = []
        self.board = []
        self.labels = []
        self.board_area = 0
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
        self.original = cv2.resize(original, (700, 960), interpolation=cv2.INTER_AREA)
        if self.debug:
            view_image(self.original)

    def process_image(self):
        self.board = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(self.board, (5, 5), 0)
        # using adaptive thresh to account for variability in pictures:
        # With a gaussian adaptive method, binary thresholding, 5 pixel groups
        self.board = cv2.adaptiveThreshold(gray, 255, 1, 0, 13, 10)
        if self.debug:
            view_image(self.board)

    def get_cells(self):
        # TODO get contour to see all squares
        pass

    def get_board(self):
        contours, hierarchy  = cv2.findContours(image=self.board, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
        max_area = 0
        # only look at top four contours, remove the outer most contour as it is most likely the image border
        top_contours = sorted(contours, key=cv2.contourArea, reverse=True)[1:5]
        # for contour in top_contours:
        #     perimeter = cv2.arcLength(contour, True)
        #     # approximates the contour's shape
        #     approx_shape = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        #     if len(approx_shape) == 4:
        #         area = cv2.contourArea(contour)
        #         if area > max_area:
        #             max_area = area
        #             board_edge = contour
        board_edge = top_contours[0]
        self.contoursBoard = board_edge
        self.board_area = max_area

        board_contour_index = contours.index(board_edge)
        cells = []

        for i in range(len(contours)):
            if(hierarchy[0][i][3]) == board_contour_index:
                cells.append((contours[i]))

        if self.debug:
            img_copy = self.original.copy()
            img_copy = cv2.drawContours(img_copy, cells, -1, (255, 255, 0), 3)
            view_image(img_copy)
