import tkinter as tk
import random
from time import sleep

# 游戏参数
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BLOCK_SIZE = 30
COLORS = ['black', 'cyan', 'blue', 'orange', 'yellow', 'green', 'purple', 'red']

# 方块形状
SHAPES = [
    [[1, 1, 1, 1]],                        # I
    [[2, 2], [2, 2]],                       # O
    [[0, 3, 0], [3, 3, 3]],                 # T
    [[4, 4, 0], [0, 4, 4]],                 # Z
    [[0, 5, 5], [5, 5, 0]],                 # S
    [[6, 6, 6], [6, 0, 0]],                 # L
    [[7, 7, 7], [0, 0, 7]]                  # J
]

class Tetris:
    def __init__(self, master):
        self.master = master
        self.master.title("俄罗斯方块")
        self.board = [[0]*BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.score = 0
        
        # 创建游戏界面
        self.canvas = tk.Canvas(master, width=BOARD_WIDTH*BLOCK_SIZE, 
                              height=BOARD_HEIGHT*BLOCK_SIZE, bg='white')
        self.canvas.pack(side=tk.LEFT)
        
        # 信息面板
        self.info_panel = tk.Frame(master)
        self.info_panel.pack(side=tk.RIGHT)
        
        self.score_label = tk.Label(self.info_panel, text="得分: 0", font=('Arial', 14))
        self.score_label.pack(pady=20)
        
        # 初始化游戏
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        
        self.master.bind("<Left>", lambda e: self.move(-1))
        self.master.bind("<Right>", lambda e: self.move(1))
        self.master.bind("<Up>", self.rotate)
        self.master.bind("<Down>", self.drop)
        
        self.game_loop()
    
    def new_piece(self):
        shape = random.choice(SHAPES)
        self.current_piece = shape
        self.current_x = BOARD_WIDTH // 2 - len(shape[0])//2
        self.current_y = 0
        
        if self.check_collision(self.current_x, self.current_y, self.current_piece):
            self.game_over()
            return False
        return True
    
    def draw(self):
        self.canvas.delete("all")
        
        # 绘制已固定的方块
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.board[y][x]:
                    self.draw_block(x, y, self.board[y][x])
        
        # 绘制当前方块
        if self.current_piece:
            for y, row in enumerate(self.current_piece):
                for x, color in enumerate(row):
                    if color:
                        self.draw_block(self.current_x + x, self.current_y + y, color)
    
    def draw_block(self, x, y, color):
        x0 = x * BLOCK_SIZE
        y0 = y * BLOCK_SIZE
        x1 = x0 + BLOCK_SIZE
        y1 = y0 + BLOCK_SIZE
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=COLORS[color], outline="white")
    
    def move(self, dx):
        if self.current_piece and not self.check_collision(self.current_x + dx, self.current_y, self.current_piece):
            self.current_x += dx
            self.draw()

    def drop(self, event=None):
        if self.current_piece and not self.check_collision(self.current_x, self.current_y + 1, self.current_piece):
            self.current_y += 1
            self.draw()
    
    def rotate(self, event=None):
        if self.current_piece:
            rotated = list(zip(*self.current_piece[::-1]))
            if not self.check_collision(self.current_x, self.current_y, rotated):
                self.current_piece = rotated
                self.draw()
    
    def check_collision(self, x, y, piece):
        for py, row in enumerate(piece):
            for px, color in enumerate(row):
                if color:
                    nx = x + px
                    ny = y + py
                    if nx < 0 or nx >= BOARD_WIDTH or ny >= BOARD_HEIGHT:
                        return True
                    if ny >= 0 and self.board[ny][nx]:
                        return True
        return False
    
    def merge_piece(self):
        for y, row in enumerate(self.current_piece):
            for x, color in enumerate(row):
                if color:
                    self.board[self.current_y + y][self.current_x + x] = color
    
    def clear_lines(self):
        full_lines = []
        for y in range(BOARD_HEIGHT):
            if all(self.board[y]):
                full_lines.append(y)
        
        for y in full_lines:
            del self.board[y]
            self.board.insert(0, [0]*BOARD_WIDTH)
        
        if full_lines:
            self.score += len(full_lines) * 100
            self.score_label.config(text=f"得分: {self.score}")
    
    def game_over(self):
        self.canvas.create_text(BOARD_WIDTH*BLOCK_SIZE/2, BOARD_HEIGHT*BLOCK_SIZE/2,
                               text="游戏结束!", fill="red", font=('Arial', 24))
        self.current_piece = None
    
    def game_loop(self):
        if self.current_piece is None:
            if not self.new_piece():
                return
        
        self.drop()
        if self.check_collision(self.current_x, self.current_y + 1, self.current_piece):
            self.merge_piece()
            self.clear_lines()
            self.new_piece()
        
        self.draw()
        self.master.after(500, self.game_loop)

if __name__ == "__main__":
    root = tk.Tk()
    game = Tetris(root)
    root.mainloop()
