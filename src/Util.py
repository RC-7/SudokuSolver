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
        # if self.debug:
        #     view_image(self.original)

    def process_image(self):
        self.board = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(self.board, (5, 5), 0)
        # using adaptive thresh to account for variability in pictures:
        # With a gaussian adaptive method, binary thresholding, 5 pixel groups
        self.board = cv2.adaptiveThreshold(gray, 255, 1, 0, 191, 0)
        if self.debug:
            view_image(self.board)

    def get_board(self):
        contours, hierarchy = cv2.findContours(image=self.board, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
        # only look at top four contours, remove the outer most contour as it is most likely the image border
        top_contours = sorted(contours, key=cv2.contourArea, reverse=True)[1:5]
        board_edge = top_contours[0]
        self.contoursBoard = board_edge
        self.board_area = cv2.contourArea(board_edge)

        x, y, w, h = cv2.boundingRect(board_edge)
        max_x = x + w
        max_y = y + h
        for contour in contours:
            try:
                area = cv2.contourArea(contour)
                if self.board_area / 20 > area > self.board_area / 250:
                    m = cv2.moments(contour)
                    cx = int(m['m10'] / m['m00'])
                    cy = int(m['m01'] / m['m00'])
                    area = cv2.contourArea(contour)
                    if area < self.board_area and x <= cx <= max_x and y <= cy <= max_y:
                        self.cells.append(contour)
            except:
                pass

        if self.debug:
            print(len(self.cells))
            img_copy_cells = self.original.copy()
            img_copy_board = self.original.copy()
            img_copy_cells = cv2.drawContours(img_copy_cells, self.cells, -1, (255, 255, 0), 3)
            img_copy_board = cv2.drawContours(img_copy_board, self.contoursBoard, -1, (255, 255, 0), 3)
            # img_copy = cv2.putText(img_copy,"YES", (max_x, max_y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0))
            view_image(img_copy_cells)
            view_image(img_copy_board)
