import tkinter as tk
from tkinter import messagebox
import copy

class Gobang:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("五子棋")
        
        # 游戏参数
        self.board_size = 15
        self.cell_size = 30
        self.margin = 30
        
        # 游戏状态
        self.board = [[0]*self.board_size for _ in range(self.board_size)]
        self.current_player = 1
        self.history = []  # 悔棋记录
        
        # 计时系统
        self.time_black = 0
        self.time_white = 0
        self.timer_id = None
        
        # 界面组件
        self.create_widgets()
        self.start_timer()
        
    def create_widgets(self):
        """创建界面组件"""
        # 棋盘画布
        canvas_size = self.margin*2 + self.cell_size*(self.board_size-1)
        self.canvas = tk.Canvas(self.window, width=canvas_size, height=canvas_size)
        self.canvas.pack()
        
        # 信息显示
        self.status_label = tk.Label(self.window, text="黑方回合", font=("Arial", 14))
        self.status_label.pack()
        
        # 时间显示
        self.time_label = tk.Label(self.window, 
                                 text="黑方用时：0秒  白方用时：0秒",
                                 font=("Arial", 12))
        self.time_label.pack()
        
        # 功能按钮
        self.undo_btn = tk.Button(self.window, text="悔棋", command=self.undo)
        self.undo_btn.pack(side=tk.LEFT, padx=10)
        
        tk.Button(self.window, text="新游戏", command=self.reset_game).pack(side=tk.RIGHT, padx=10)
        
        # 事件绑定
        self.canvas.bind("<Button-1>", self.click_handler)
        self.draw_board()
    
    def draw_board(self):
        """绘制棋盘网格"""
        for i in range(self.board_size):
            self.canvas.create_line(
                self.margin, 
                self.margin + i*self.cell_size,
                self.margin + (self.board_size-1)*self.cell_size,
                self.margin + i*self.cell_size
            )
            self.canvas.create_line(
                self.margin + i*self.cell_size, 
                self.margin,
                self.margin + i*self.cell_size,
                self.margin + (self.board_size-1)*self.cell_size
            )
    
    def click_handler(self, event):
        """处理鼠标点击"""
        x = event.x - self.margin
        y = event.y - self.margin
        col = round(x / self.cell_size)
        row = round(y / self.cell_size)
        
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            if self.board[row][col] == 0:
                # 保存当前状态
                self.history.append({
                    'board': copy.deepcopy(self.board),
                    'player': self.current_player,
                    'time_black': self.time_black,
                    'time_white': self.time_white
                })
                
                self.place_piece(row, col)
                if self.check_win(row, col):
                    self.game_over()
                else:
                    self.switch_player()
    
    def place_piece(self, row, col):
        """放置棋子"""
        color = "black" if self.current_player == 1 else "white"
        x = self.margin + col * self.cell_size
        y = self.margin + row * self.cell_size
        self.canvas.create_oval(x-10, y-10, x+10, y+10, fill=color)
        self.board[row][col] = self.current_player
    
    def switch_player(self):
        """切换玩家"""
        self.current_player = 2 if self.current_player == 1 else 1
        self.status_label.config(text="黑方回合" if self.current_player == 1 else "白方回合")
    
    def check_win(self, row, col):
        """检查胜利条件"""
        directions = [(0,1), (1,0), (1,1), (1,-1)]
        for dr, dc in directions:
            count = 1
            i, j = row + dr, col + dc
            while 0 <= i < self.board_size and 0 <= j < self.board_size and self.board[i][j] == self.current_player:
                count += 1
                i += dr
                j += dc
            i, j = row - dr, col - dc
            while 0 <= i < self.board_size and 0 <= j < self.board_size and self.board[i][j] == self.current_player:
                count += 1
                i -= dr
                j -= dc
            if count >= 5:
                return True
        return False
    
    def game_over(self):
        """游戏结束处理"""
        winner = "黑方" if self.current_player == 1 else "白方"
        messagebox.showinfo("游戏结束", f"{winner}获胜！")
        self.reset_game()
    
    def undo(self):
        """悔棋功能"""
        if len(self.history) > 0:
            # 恢复历史状态
            prev_state = self.history.pop()
            self.board = prev_state['board']
            self.current_player = prev_state['player']
            self.time_black = prev_state['time_black']
            self.time_white = prev_state['time_white']
            
            # 重置界面
            self.canvas.delete("all")
            self.draw_board()
            for r in range(self.board_size):
                for c in range(self.board_size):
                    if self.board[r][c] != 0:
                        self.place_piece(r, c)
            
            # 更新显示
            self.status_label.config(text="黑方回合" if self.current_player == 1 else "白方回合")
            self.update_time_display()
    
    def start_timer(self):
        """启动计时器"""
        self.update_timer()
    
    def update_timer(self):
        """更新计时"""
        if self.current_player == 1:
            self.time_black += 1
        else:
            self.time_white += 1
        
        self.update_time_display()
        self.timer_id = self.window.after(1000, self.update_timer)
    
    def update_time_display(self):
        """更新时间显示"""
        self.time_label.config(
            text=f"黑方用时：{self.time_black}秒  白方用时：{self.time_white}秒"
        )
    
    def reset_game(self):
        """重置游戏"""
        self.canvas.delete("all")
        self.board = [[0]*self.board_size for _ in range(self.board_size)]
        self.current_player = 1
        self.time_black = 0
        self.time_white = 0
        self.history = []
        self.status_label.config(text="黑方回合")
        self.update_time_display()
        self.draw_board()
        if self.timer_id:
            self.window.after_cancel(self.timer_id)
        self.start_timer()
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    game = Gobang()
    game.run()