# ============== 教师发送端 TeacherSender.py ==============
import tkinter as tk
from tkinter import messagebox
import base64
import hashlib
import os
from datetime import datetime

class TeacherApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("教师信息发送端")
        
        # 配置网络文件路径（需修改为实际路径）
        self.file_path = r"E:\班级消息\message.dat"
        
        self.setup_ui()
        
    def setup_ui(self):
        tk.Label(self.window, text="输入要发送的消息：").pack(pady=5)
        self.msg_entry = tk.Entry(self.window, width=40)
        self.msg_entry.pack(pady=5)
        
        send_btn = tk.Button(self.window, text="发送消息", command=self.send_message)
        send_btn.pack(pady=10)
        
    def send_message(self):
        message = self.msg_entry.get()
        if not message:
            messagebox.showerror("错误", "消息内容不能为空")
            return
        
        try:
            # 生成时间戳
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Base64编码
            encoded = base64.b64encode(message.encode('utf-8')).decode('utf-8')
            
            # 计算哈希值（包含时间戳）
            data_to_hash = f"{encoded}{timestamp}".encode('utf-8')
            sha256_hash = hashlib.sha256(data_to_hash).hexdigest()
            
            # 写入文件
            with open(self.file_path, "w", encoding='utf-8') as f:
                f.write(f"{encoded}\n{sha256_hash}\n{timestamp}")
                
            messagebox.showinfo("成功", "消息已安全发送")
            self.msg_entry.delete(0, tk.END)
            
        except Exception as e:
            error_msg = f"发送失败：\n{str(e)}"
            messagebox.showerror("错误", error_msg)
            print(f"DEBUG - 异常详情：\n{repr(e)}")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = TeacherApp()
    app.run()