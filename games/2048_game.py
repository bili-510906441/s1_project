import tkinter as tk
from tkinter import messagebox
import random

class Game2048:
    def __init__(self, root):
        self.root = root
        self.root.title("2048")
        self.game_size = 4
        self.cell_size = 100
        self.colors = {
            0: "#9e948a",
            2: "#eee4da",
            4: "#ede0c8",
            8: "#f2b179",
            16: "#f59563",
            32: "#f67c5f",
            64: "#f65e3b",
            128: "#edcf72",
            256: "#edcc61",
            512: "#edc850",
            1024: "#edc53f",
            2048: "#edc22e"
        }
        self.score = 0
        self.grid = [[0]*self.game_size for _ in range(self.game_size)]
        self.init_gui()
        self.start_game()

    def init_gui(self):
        # Score display
        self.score_label = tk.Label(self.root, text="Score: 0", font=("Arial", 14))
        self.score_label.grid(row=0, column=0, columnspan=self.game_size)

        # Game grid
        self.cells = []
        for i in range(self.game_size):
            row = []
            for j in range(self.game_size):
                cell = tk.Frame(self.root, width=self.cell_size, height=self.cell_size)
                cell.grid(row=i+1, column=j, padx=5, pady=5)
                cell_label = tk.Label(cell, text="", font=("Arial", 24, "bold"), 
                                    bg=self.colors[0], width=4, height=2)
                cell_label.pack(expand=True, fill="both")
                row.append(cell_label)
            self.cells.append(row)

        # Key bindings
        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)
        self.root.bind("<Up>", self.move_up)
        self.root.bind("<Down>", self.move_down)

    def start_game(self):
        self.score = 0
        self.grid = [[0]*self.game_size for _ in range(self.game_size)]
        self.add_new_tile()
        self.add_new_tile()
        self.update_gui()

    def add_new_tile(self):
        empty_cells = [(i, j) for i in range(self.game_size) 
                      for j in range(self.game_size) if self.grid[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.grid[i][j] = 2 if random.random() < 0.9 else 4

    def update_gui(self):
        for i in range(self.game_size):
            for j in range(self.game_size):
                value = self.grid[i][j]
                color = self.colors.get(value, "#000000")
                self.cells[i][j].config(text=str(value) if value else "", 
                                      bg=color, fg="#776e65" if value < 8 else "#f9f6f2")
        self.score_label.config(text=f"Score: {self.score}")
        self.root.update()

    def move(self, direction):
        moved = False
        temp_grid = [row[:] for row in self.grid]

        if direction == "left":
            for i in range(self.game_size):
                new_row, score = self.merge(self.grid[i])
                if new_row != self.grid[i]:
                    moved = True
                    self.grid[i] = new_row
                self.score += score

        elif direction == "right":
            for i in range(self.game_size):
                new_row, score = self.merge(self.grid[i][::-1])
                if new_row != self.grid[i][::-1]:
                    moved = True
                    self.grid[i] = new_row[::-1]
                self.score += score

        elif direction == "up":
            for j in range(self.game_size):
                column = [self.grid[i][j] for i in range(self.game_size)]
                new_col, score = self.merge(column)
                if new_col != column:
                    moved = True
                    for i in range(self.game_size):
                        self.grid[i][j] = new_col[i]
                self.score += score

        elif direction == "down":
            for j in range(self.game_size):
                column = [self.grid[i][j] for i in range(self.game_size)][::-1]
                new_col, score = self.merge(column)
                if new_col != column:
                    moved = True
                    new_col = new_col[::-1]
                    for i in range(self.game_size):
                        self.grid[i][j] = new_col[i]
                self.score += score

        if moved:
            self.add_new_tile()
            self.update_gui()
            if self.check_game_over():
                messagebox.showinfo("Game Over", f"Final Score: {self.score}")
                self.start_game()
        else:
            if self.check_game_over():
                messagebox.showinfo("Game Over", f"Final Score: {self.score}")
                self.start_game()

    def merge(self, row):
        new_row = [i for i in row if i != 0]
        score = 0
        for i in range(len(new_row)-1):
            if new_row[i] == new_row[i+1]:
                new_row[i] *= 2
                score += new_row[i]
                new_row.pop(i+1)
                new_row.append(0)
        new_row = [i for i in new_row if i != 0]
        new_row += [0] * (len(row) - len(new_row))
        return new_row, score

    def check_game_over(self):
        # Check for empty cells
        if any(0 in row for row in self.grid):
            return False
        
        # Check for possible merges
        for i in range(self.game_size):
            for j in range(self.game_size-1):
                if self.grid[i][j] == self.grid[i][j+1]:
                    return False
        for j in range(self.game_size):
            for i in range(self.game_size-1):
                if self.grid[i][j] == self.grid[i+1][j]:
                    return False
        return True

    def move_left(self, event):
        self.move("left")

    def move_right(self, event):
        self.move("right")

    def move_up(self, event):
        self.move("up")

    def move_down(self, event):
        self.move("down")

if __name__ == "__main__":
    root = tk.Tk()
    game = Game2048(root)
    root.mainloop()
