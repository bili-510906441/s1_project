import tkinter as tk
from tkinter import messagebox

class Gobang:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("五子棋")
        
        # 游戏参数
        self.board_size = 15  # 棋盘15x15格
        self.cell_size = 30   # 每格30像素
        self.margin = 30      # 边距
        
        # 初始化棋盘数据（0=空，1=黑，2=白）
        self.board = [[0]*self.board_size for _ in range(self.board_size)]
        self.current_player = 1  # 黑方先手
        
        # 创建界面组件
        self.canvas = tk.Canvas(self.window, 
                              width=self.margin*2 + self.cell_size*(self.board_size-1),
                              height=self.margin*2 + self.cell_size*(self.board_size-1))
        self.canvas.pack()
        
        self.label = tk.Label(self.window, text="黑方回合", font=("Arial", 14))
        self.label.pack()
        
        # 绑定事件
        self.canvas.bind("<Button-1>", self.click_handler)
        
        # 绘制棋盘
        self.draw_board()
        
    def draw_board(self):
        """绘制棋盘网格"""
        for i in range(self.board_size):
            # 水平线
            self.canvas.create_line(
                self.margin, 
                self.margin + i*self.cell_size,
                self.margin + (self.board_size-1)*self.cell_size,
                self.margin + i*self.cell_size
            )
            # 垂直线
            self.canvas.create_line(
                self.margin + i*self.cell_size, 
                self.margin,
                self.margin + i*self.cell_size,
                self.margin + (self.board_size-1)*self.cell_size
            )
    
    def click_handler(self, event):
        """处理鼠标点击事件"""
        # 将物理坐标转换为棋盘坐标
        x = event.x - self.margin
        y = event.y - self.margin
        col = round(x / self.cell_size)
        row = round(y / self.cell_size)
        
        # 检查落子是否合法
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            if self.board[row][col] == 0:
                self.place_piece(row, col)
                if self.check_win(row, col):
                    winner = "黑方" if self.current_player == 1 else "白方"
                    messagebox.showinfo("游戏结束", f"{winner}获胜！")
                    self.reset_game()
                    return
                self.switch_player()
    
    def place_piece(self, row, col):
        """在指定位置落子"""
        color = "black" if self.current_player == 1 else "white"
        x = self.margin + col * self.cell_size
        y = self.margin + row * self.cell_size
        self.canvas.create_oval(x-10, y-10, x+10, y+10, fill=color)
        self.board[row][col] = self.current_player
    
    def switch_player(self):
        """切换玩家"""
        self.current_player = 2 if self.current_player == 1 else 1
        self.label.config(text="黑方回合" if self.current_player == 1 else "白方回合")
    
    def check_win(self, row, col):
        """检查是否获胜"""
        directions = [
            (0, 1),   # 水平
            (1, 0),   # 垂直
            (1, 1),   # 主对角线
            (1, -1)   # 副对角线
        ]
        
        for dr, dc in directions:
            count = 1
            # 向正方向检查
            i, j = row + dr, col + dc
            while 0 <= i < self.board_size and 0 <= j < self.board_size and self.board[i][j] == self.current_player:
                count += 1
                i += dr
                j += dc
            # 向反方向检查
            i, j = row - dr, col - dc
            while 0 <= i < self.board_size and 0 <= j < self.board_size and self.board[i][j] == self.current_player:
                count += 1
                i -= dr
                j -= dc
            # 判断是否五连
            if count >= 5:
                return True
        return False
    
    def reset_game(self):
        """重置游戏"""
        self.canvas.delete("all")
        self.board = [[0]*self.board_size for _ in range(self.board_size)]
        self.current_player = 1
        self.label.config(text="黑方回合")
        self.draw_board()
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    game = Gobang()
    game.run()