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


def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def distance(pt1, pt2):
    return np.sqrt(((pt1[0] - pt2[0]) ** 2) + ((pt1[1] - pt2[1]) ** 2))


def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    width_bottom = distance(br, bl)
    width_top = distance(tr, tl)
    max_width = max(int(width_bottom), int(width_top))

    height_right = distance(tr, br)
    height_left = distance(tl, bl)
    max_height = max(int(height_right), int(height_left))

    dst = np.array([
        [0, 0],
        [max_width, 0],
        [max_width, max_height],
        [0, max_height]], dtype="float32")

    m = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, m, (max_width, max_height))
    return warped


class Util:
    def __init__(self, debug, puzzle_name='Puzzle1'):
        self.contoursOriginal = []
        self.cells = []
        self.contoursBoard = []
        self.original = []
        self.board = []
        self.labels = []
        self.board_area = 0
        self.debug = debug
        self.puzzle_name = puzzle_name
        print(cv2.__file__)

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

    def process_image(self):
        self.board = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(self.board, (5, 5), 0)
        # using adaptive thresh to account for variability in pictures:
        # With a gaussian adaptive method, binary thresholding, 5 pixel groups
        self.board = cv2.adaptiveThreshold(gray, 255, 1, 0, 191, 0)
        if self.debug:
            view_image(self.board)

    def order_cells(self, cell_contours, sort_method='Vertical'):
        if sort_method == 'Vertical':
            axis = 1
        elif sort_method == 'Horizontal':
            axis = 0
        else:
            raise "Incorrect sort_method"

        bounding_rects = [cv2.boundingRect(c) for c in cell_contours]
        (cell_contours, bounding_rects) = zip(*sorted(zip(cell_contours, bounding_rects), key=lambda b: b[1][axis]))
        ordered_cells = ()
        for i in range(9):
            start_index = i*9
            slice1 = cell_contours[start_index: start_index + 9]
            slice2 = bounding_rects[start_index: start_index + 9]
            (test, _) = zip(*sorted(zip(slice1, slice2), key=lambda b: b[1][0]))
            ordered_cells = ordered_cells + test
        self.cells = ordered_cells

    def get_cell_images(self):
        cell_images = []

        gray = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        gray = cv2.adaptiveThreshold(gray, 255, 1, cv2.THRESH_BINARY_INV, 21, 15)

        for c in self.cells:
            if self.debug:
                img_copy_board = self.original.copy()
                img_copy_board = cv2.drawContours(img_copy_board, c, -1, (255, 255, 0), 3)
                view_image(img_copy_board)

            perimeter = cv2.arcLength(c, True)
            approx_poly = cv2.approxPolyDP(c, 0.08 * perimeter, True)

            pts = np.array(approx_poly.reshape(4, 2))
            # TODO look at using a less aggressively thresholded image for this
            cell = four_point_transform(gray, pts)
            cell = cv2.resize(cell, (28, 28), interpolation=cv2.INTER_AREA)
            cell_images.append(cell)
            if self.debug:
                view_image(cell)
        return cell_images

    def get_contours(self):
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
        self.order_cells(self.cells)

        if self.debug:
            print(len(self.cells))
            img_copy_cells = self.original.copy()
            img_copy_board = self.original.copy()
            img_copy_cells = cv2.drawContours(img_copy_cells, self.cells, -1, (255, 255, 0), 3)
            img_copy_board = cv2.drawContours(img_copy_board, self.contoursBoard, -1, (255, 255, 0), 3)
            # img_copy = cv2.putText(img_copy,"YES", (max_x, max_y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0))
            view_image(img_copy_cells)
            view_image(img_copy_board)
            view_image(self.board)
        return [self.contoursBoard, self.cells]
