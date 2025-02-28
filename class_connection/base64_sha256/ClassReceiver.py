# ============== 班级接收端 ClassReceiver.py ==============
import tkinter as tk
from tkinter import messagebox
import base64
import hashlib
import os
import threading
from datetime import datetime

class ClassApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("班级信息接收端")
        
        # 配置路径（需与教师端一致）
        self.file_path = r"E:\班级消息\message.dat"
        self.history_file = "message_history.txt"
        
        self.setup_ui()
        self.running = True
        self.start_checking()
        
        # 初始化历史记录文件
        try:
            if not os.path.exists(self.history_file):
                with open(self.history_file, "w", encoding='utf-8') as f:
                    f.write("=== 消息历史记录 ===\n")
        except Exception as e:
            self.show_error(f"初始化历史文件失败：{str(e)}")

    def setup_ui(self):
        self.status_label = tk.Label(self.window, text="等待接收消息...")
        self.status_label.pack(pady=10)
        
        self.msg_display = tk.Text(self.window, width=40, height=10)
        self.msg_display.pack(padx=10, pady=5)
        
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="查看历史", command=self.show_history).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="退出", command=self.shutdown).pack(side=tk.RIGHT, padx=5)

    def check_messages(self):
        while self.running:
            try:
                if os.path.exists(self.file_path):
                    # 读取消息文件
                    with open(self.file_path, "r", encoding='utf-8') as f:
                        content = f.read().splitlines()
                    
                    if len(content) >= 3:
                        encoded, received_hash, timestamp = content[:3]
                        
                        # 验证哈希
                        data_to_hash = f"{encoded}{timestamp}".encode('utf-8')
                        computed_hash = hashlib.sha256(data_to_hash).hexdigest()
                        
                        if computed_hash == received_hash:
                            # 解码消息
                            try:
                                decoded_bytes = base64.b64decode(encoded)
                                decoded = decoded_bytes.decode('utf-8')
                            except UnicodeDecodeError:
                                decoded = decoded_bytes.decode('gbk', 'replace')
                            
                            # 更新显示
                            self.msg_display.delete(1.0, tk.END)
                            self.msg_display.insert(tk.END, f"[{timestamp}]\n{decoded}")
                            self.status_label.config(text="收到新消息")
                            
                            # 记录历史
                            try:
                                with open(self.history_file, "a", encoding='utf-8') as hist:
                                    hist.write(f"[{timestamp}] {decoded}\n")
                            except Exception as e:
                                self.show_error(f"历史记录失败：{str(e)}")
                            
                            # 删除消息文件
                            os.remove(self.file_path)
                        else:
                            self.status_label.config(text="消息校验失败")
                            os.remove(self.file_path)
            except Exception as e:
                error_msg = f"接收消息时出错：\n{str(e)}"
                self.show_error(error_msg)
                print(f"DEBUG - 异常详情：\n{repr(e)}")
            
            self.window.after(3000, self.check_messages)
            break

    def show_history(self):
        try:
            history_window = tk.Toplevel(self.window)
            history_window.title("历史消息记录")
            
            text_area = tk.Text(history_window, width=50, height=20)
            text_area.pack(padx=10, pady=10)
            
            if os.path.exists(self.history_file):
                with open(self.history_file, "r", encoding='utf-8', errors='replace') as f:
                    text_area.insert(tk.END, f.read())
            else:
                text_area.insert(tk.END, "暂无历史记录")
                
            text_area.config(state=tk.DISABLED)
        except Exception as e:
            self.show_error(f"打开历史记录失败：{str(e)}")

    def show_error(self, msg):
        self.window.after(0, lambda: messagebox.showerror("系统错误", msg))

    def start_checking(self):
        thread = threading.Thread(target=self.check_messages, daemon=True)
        thread.start()
        
    def shutdown(self):
        self.running = False
        self.window.destroy()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = ClassApp()
    app.run()