import tkinter as tk
import random

class SnakeGame:
    def __init__(self, master):
        self.master = master
        self.master.title("贪吃蛇游戏")
        self.master.resizable(False, False)
        
        # 游戏参数
        self.width = 500
        self.height = 500
        self.cell_size = 20
        self.speed = 200  # 初始速度（毫秒）
        self.min_speed = 80  # 最小速度
        self.score = 0
        self.direction = "Right"
        self.game_over = False

        # 创建画布
        self.canvas = tk.Canvas(self.master, width=self.width, height=self.height, 
                              highlightthickness=0, bg='black')
        self.canvas.pack()

        # 信息显示区域
        self.info_frame = tk.Frame(self.master)
        self.info_frame.pack(pady=5)
        
        # 得分显示
        self.score_label = tk.Label(self.info_frame, text=f"得分: {self.score}", 
                                   font=('Arial', 14), padx=10)
        self.score_label.pack(side=tk.LEFT)
        
        # 速度显示
        self.speed_label = tk.Label(self.info_frame, 
                                   text=f"速度: {self.calculate_speed():.1f} 格/秒",
                                   font=('Arial', 14), padx=10)
        self.speed_label.pack(side=tk.LEFT)

        # 初始化蛇和食物
        self.snake = [(10, 10), (9, 10), (8, 10)]
        self.food = self.create_food()

        # 绘制游戏边框
        self.canvas.create_rectangle(
            3, 3,
            self.width-3, self.height-3,
            outline="#555555",
            width=6
        )

        # 绑定键盘事件
        self.master.bind('<Key>', self.change_direction)

        # 开始游戏循环
        self.update()

    def create_food(self):
        """生成新的食物"""
        while True:
            x = random.randint(0, (self.width//self.cell_size)-1)
            y = random.randint(0, (self.height//self.cell_size)-1)
            if (x, y) not in self.snake:
                return (x, y)

    def calculate_speed(self):
        """将延迟时间转换为速度（格/秒）"""
        return 1000 / self.speed

    def change_direction(self, event):
        """改变蛇的移动方向"""
        key = event.keysym
        if (key == "Up" and self.direction != "Down" or
            key == "Down" and self.direction != "Up" or
            key == "Left" and self.direction != "Right" or
            key == "Right" and self.direction != "Left"):
            self.direction = key

    def update(self):
        """更新游戏状态"""
        if not self.game_over:
            # 移动蛇
            head_x, head_y = self.snake[0]
            
            if self.direction == "Up":
                new_head = (head_x, head_y - 1)
            elif self.direction == "Down":
                new_head = (head_x, head_y + 1)
            elif self.direction == "Left":
                new_head = (head_x - 1, head_y)
            elif self.direction == "Right":
                new_head = (head_x + 1, head_y)

            # 检查碰撞
            if (new_head in self.snake or
                new_head[0] < 0 or new_head[0] >= self.width//self.cell_size or
                new_head[1] < 0 or new_head[1] >= self.height//self.cell_size):
                self.game_over = True
                self.game_over_screen()
                return

            self.snake.insert(0, new_head)

            # 检查是否吃到食物
            if new_head == self.food:
                self.score += 1
                self.food = self.create_food()
                # 每得5分加速一次
                if self.score % 3 == 0 and self.speed > self.min_speed:
                    self.speed = max(self.speed - 20, self.min_speed)
                # 更新显示
                self.score_label.config(text=f"得分: {self.score}")
                self.speed_label.config(text=f"速度: {self.calculate_speed():.1f} 格/秒")
            else:
                self.snake.pop()

            # 重绘画布
            self.canvas.delete("all")
            
            # 绘制游戏边框
            self.canvas.create_rectangle(
                3, 3,
                self.width-3, self.height-3,
                outline="#555555",
                width=6
            )
            
            # 绘制蛇
            for segment in self.snake:
                x, y = segment
                self.canvas.create_rectangle(
                    x * self.cell_size, y * self.cell_size,
                    (x+1) * self.cell_size, (y+1) * self.cell_size,
                    fill="green")
            
            # 绘制食物
            x, y = self.food
            self.canvas.create_oval(
                x * self.cell_size, y * self.cell_size,
                (x+1) * self.cell_size, (y+1) * self.cell_size,
                fill="red")

            self.master.after(self.speed, self.update)

    def game_over_screen(self):
        """显示游戏结束画面"""
        self.canvas.create_text(
            self.width/2, self.height/2,
            text=f"游戏结束！得分: {self.score}",
            fill="red",
            font=('Arial', 24, 'bold'))
        self.canvas.create_text(
            self.width/2, self.height/2 + 40,
            text="按R重新开始，按Q退出",
            fill="white",
            font=('Arial', 14))

        self.master.bind('r', self.restart_game)
        self.master.bind('q', self.quit_game)

    def restart_game(self, event=None):
        """重新开始游戏"""
        self.canvas.delete("all")
        self.snake = [(10, 10), (9, 10), (8, 10)]
        self.food = self.create_food()
        self.direction = "Right"
        self.score = 0
        self.speed = 200
        self.game_over = False
        self.score_label.config(text=f"得分: {self.score}")
        self.speed_label.config(text=f"速度: {self.calculate_speed():.1f} 格/秒")
        self.master.unbind('r')
        self.master.unbind('q')
        self.update()

    def quit_game(self, event=None):
        """退出游戏"""
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()