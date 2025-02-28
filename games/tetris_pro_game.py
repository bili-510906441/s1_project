import tkinter as tk
import random
from collections import deque

# 游戏参数
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BLOCK_SIZE = 30
COLORS = ['black', 'cyan', 'blue', 'orange', 'yellow', 'green', 'purple', 'red']

# 方块形状
SHAPES = [
    [[1, 1, 1, 1]],                # I
    [[2, 2], [2, 2]],               # O
    [[0, 3, 0], [3, 3, 3]],         # T
    [[4, 4, 0], [0, 4, 4]],         # Z
    [[0, 5, 5], [5, 5, 0]],         # S
    [[6, 6, 6], [6, 0, 0]],         # L
    [[7, 7, 7], [0, 0, 7]]          # J
]

class Tetris:
    def __init__(self, master):
        self.master = master
        self.master.title("俄罗斯方块 PRO")
        self.board = [[0]*BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        
        # 创建游戏界面
        self.canvas = tk.Canvas(master, width=BOARD_WIDTH*BLOCK_SIZE, 
                              height=BOARD_HEIGHT*BLOCK_SIZE, bg='white')
        self.canvas.pack(side=tk.LEFT)
        
        # 信息面板
        self.info_panel = tk.Frame(master)
        self.info_panel.pack(side=tk.RIGHT, padx=20)
        
        # 预览区域
        self.preview_canvas = tk.Canvas(self.info_panel, width=5*BLOCK_SIZE, 
                                      height=5*BLOCK_SIZE, bg='white')
        self.preview_canvas.pack(pady=10)
        tk.Label(self.info_panel, text="下一个：").pack()
        
        # 等级和分数显示
        self.level_label = tk.Label(self.info_panel, 
                                   text=f"等级: {self.level}", 
                                   font=('Arial', 12))
        self.level_label.pack(pady=5)
        self.score_label = tk.Label(self.info_panel, 
                                   text=f"得分: {self.score}", 
                                   font=('Arial', 12))
        self.score_label.pack(pady=5)
        
        # 初始化方块队列
        self.bag = deque()
        self.current_piece = None
        self.next_piece = None
        self.init_bag()
        
        self.current_x = 0
        self.current_y = 0
        
        # 按键绑定
        self.master.bind("<Left>", lambda e: self.move(-1))
        self.master.bind("<Right>", lambda e: self.move(1))
        self.master.bind("<Up>", self.rotate)
        self.master.bind("<Down>", self.drop)
        self.master.bind("<space>", self.hard_drop)
        
        self.game_loop()
    
    def init_bag(self):
        """使用7-bag随机生成算法"""
        self.bag = deque(random.sample(SHAPES, 7))
        self.next_piece = self.bag.popleft()
        if not self.bag:
            self.bag.extend(random.sample(SHAPES, 7))
    
    def new_piece(self):
        """生成新方块"""
        self.current_piece = self.next_piece
        self.current_x = BOARD_WIDTH // 2 - len(self.current_piece[0])//2
        self.current_y = 0
        
        # 填充下一个方块
        if not self.bag:

            self.bag.extend(random.sample(SHAPES, 7))
        self.next_piece = self.bag.popleft()
        
        if self.check_collision(self.current_x, self.current_y, self.current_piece):
            self.game_over()
            return False
        return True
    
    def draw_preview(self):
        """绘制预览方块"""
        self.preview_canvas.delete("all")
        if self.next_piece:
            # 计算居中位置
            shape = self.next_piece
            start_x = (5 - len(shape[0]))/2 * BLOCK_SIZE
            start_y = (5 - len(shape))/2 * BLOCK_SIZE
            
            for y, row in enumerate(shape):
                for x, color in enumerate(row):
                    if color:
                        x0 = start_x + x * BLOCK_SIZE
                        y0 = start_y + y * BLOCK_SIZE
                        x1 = x0 + BLOCK_SIZE
                        y1 = y0 + BLOCK_SIZE
                        self.preview_canvas.create_rectangle(
                            x0, y0, x1, y1, 
                            fill=COLORS[color], 
                            outline="white"
                        )
    
    def update_speed(self):
        """根据等级调整下落速度"""
        base_speed = 500  # 初始速度
        speed = max(50, base_speed - (self.level-1)*50)  # 每级加速50ms，最后这个50是每级加速量
        return speed
    
    def update_level(self):
        """更新等级系统"""
        # 每消除10行升一级
        new_level = self.lines_cleared // 10 + 1  # 10表示每消除10行升一级
        if new_level > self.level:
            self.level = new_level
            self.level_label.config(text=f"等级: {self.level}")
    
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
        
        # 绘制预览
        self.draw_preview()
    
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
    
    def hard_drop(self, event=None):
        """一键到底"""
        while not self.check_collision(self.current_x, self.current_y + 1, self.current_piece):
            self.current_y += 1
        self.merge_piece()
        self.clear_lines()

        self.new_piece()
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
            lines = len(full_lines)
            self.lines_cleared += lines
            self.score += lines * 100 * self.level  # 等级倍率，100是基础分值
            self.score_label.config(text=f"得分: {self.score}")
            self.update_level()
    
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
        self.master.after(self.update_speed(), self.game_loop)

if __name__ == "__main__":
    root = tk.Tk()
    game = Tetris(root)
    root.mainloop()
