from tkinter.filedialog import askopenfilename
import tkinter as tk
from PIL import ImageTk, Image

from src.SudokuPuzzle import SudokuPuzzle


class GUI:
    def __init__(self, root):

        self.solution = False
        self.hint = False
        self.request_file = False
        self.filename = ""
        self.hints = 0
        self.sp = None

        self.window = root
        self.label = tk.Label(text="Select a mode and image to continue")
        self.label.pack()
        self.solution_button = tk.Button(self.window, text="Get full solution", command=self.set_solution_request)
        self.solution_button.pack(padx=5, pady=5, side=tk.RIGHT)
        self.hint_button = tk.Button(self.window, text="Get Hint", command=self.set_hint_request)
        self.hint_button.pack(padx=5, pady=5, side=tk.RIGHT)
        next_hint = self.hints + 1
        self.label_hint = tk.Label(text="Next hint will show %d hints" % next_hint)
        self.label_hint.pack(padx=5, pady=5, side=tk.RIGHT)
        self.image_button = tk.Button(self.window, text="Select Image", command=self.get_file)
        self.image_button.pack(padx=5, pady=5, side=tk.RIGHT)
        self.imageLabel = tk.Label(self.window)
        self.imageLabel.pack()

    def set_solution_request(self):
        self.solution = True
        self.hint = False
        self.solution_button.config(bg="red")
        self.hint_button.config(bg='#f0f0f0')
        self.label.config(fg='black')
        if not self.filename == '':
            self.get_solution(-1)

    def set_hint_request(self):
        self.solution = False
        self.hint = True
        self.hint_button.config(bg="red")
        self.solution_button.config(bg='#f0f0f0')
        self.hints += 1
        next_hint = self.hints + 1
        self.label_hint.config(text="Next hint will show %d hints" % next_hint)
        self.label.config(fg='black')
        if not self.filename == '':
            self.get_solution(self.hints)

    def get_solution(self, solutions_to_display):
        self.label.config(text="Press Get Hint to increase number of hints viewed or press Get full solution to"
                               " get the full solution", fg='black')
        if self.sp is None:
            self.sp = SudokuPuzzle(self.filename, False)
            self.sp.create_board()
            self.sp.solve_puzzle()
        solution = self.sp.view_puzzle(solutions_to_display)
        im = Image.fromarray(solution)
        imgtk = ImageTk.PhotoImage(image=im)
        self.imageLabel.config(image=imgtk)
        self.window.mainloop()

    def get_file(self):
        self.filename = askopenfilename()
        self.sp = None
        if not self.solution and not self.hint:
            self.label.config(text="Select a mode to proceed", fg="red")
        else:
            if self.hint:
                self.get_solution(self.hints)
            else:
                self.get_solution(-1)
