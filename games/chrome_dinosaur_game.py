import tkinter as tk
import random

class DinoGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Chrome Dino Game")
        
        # 游戏参数
        self.width = 800
        self.height = 300
        self.ground = 250
        self.dino_x = 50
        self.dino_y = self.ground
        self.gravity = 1.5
        self.jump_force = -20
        self.velocity = 0
        self.obstacles = []
        self.game_over = False
        self.score = 0
        
        # 创建画布
        self.canvas = tk.Canvas(root, width=self.width, height=self.height)
        self.canvas.pack()
        
        # 初始化恐龙
        self.dino = self.canvas.create_rectangle(
            self.dino_x, self.dino_y,
            self.dino_x + 30, self.dino_y + 50,
            fill="gray"
        )
        
        # 显示分数
        self.score_text = self.canvas.create_text(700, 50, text="Score: 0", font=("Arial", 16))
        
        # 绑定事件
        self.root.bind("<space>", self.jump)
        self.root.bind("<r>", self.restart)
        
        # 开始游戏循环
        self.game_loop()
    
    def jump(self, event):
        if not self.game_over and self.velocity == 0:
            self.velocity = self.jump_force
    
    def restart(self, event):
        self.game_over = False
        self.score = 0
        self.velocity = 0
        self.canvas.delete("obstacle")
        self.obstacles = []
        self.canvas.itemconfig(self.score_text, text="Score: 0")
        self.canvas.move(self.dino, 0, self.ground - self.dino_y)
        self.dino_y = self.ground
        self.game_loop()
    
    def create_obstacle(self):
        height = random.randint(20, 50)
        obstacle = self.canvas.create_rectangle(
            self.width, self.ground - height,
            self.width + 30, self.ground,
            fill="green",
            tags="obstacle"
        )
        self.obstacles.append(obstacle)
    
    def update_obstacles(self):
        for obstacle in self.obstacles:
            self.canvas.move(obstacle, -10, 0)
            
            # 碰撞检测
            pos = self.canvas.coords(obstacle)
            dino_pos = self.canvas.coords(self.dino)
            if pos[0] < dino_pos[2] and pos[2] > dino_pos[0]:
                if dino_pos[3] > pos[1]:
                    self.game_over = True
        
        # 移除屏幕外的障碍物并加分
        if self.obstacles and self.canvas.coords(self.obstacles[0])[2] < 0:
            self.canvas.delete(self.obstacles.pop(0))
            self.score += 1
            self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
    
    def game_loop(self):
        if not self.game_over:
            # 更新恐龙位置
            self.velocity += self.gravity
            self.dino_y += self.velocity
            if self.dino_y > self.ground:
                self.dino_y = self.ground
                self.velocity = 0
            self.canvas.move(self.dino, 0, self.velocity)
            
            # 生成障碍物
            if random.random() < 0.03:
                self.create_obstacle()
            
            # 更新障碍物
            self.update_obstacles()
            
            # 继续游戏循环
            self.root.after(50, self.game_loop)
        else:
            self.canvas.create_text(
                self.width/2, self.height/2,
                text="Game Over! Press R to restart",
                font=("Arial", 20),
                fill="red"
            )

if __name__ == "__main__":
    root = tk.Tk()
    game = DinoGame(root)
    root.mainloop()