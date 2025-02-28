import tkinter as tk
from tkinter import messagebox
import base64
import os
import threading
from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

class ClassApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("班级信息接收端")
        
        # 配置文件路径（需修改）
        self.file_path = r"Z:\班级消息\message.dat"
        self.history_file = "message_history.txt"
        self.public_key_path = "teacher_public_key.pem"
        
        # 加载公钥
        try:
            with open(self.public_key_path, "rb") as key_file:
                self.public_key = serialization.load_pem_public_key(
                    key_file.read(),
                    backend=default_backend()
                )
        except Exception as e:
            messagebox.showerror("错误", f"公钥加载失败：{str(e)}")
            self.window.destroy()
        
        self.setup_ui()
        self.running = True
        self.start_checking()
        
        # 初始化历史文件
        try:
            if not os.path.exists(self.history_file):
                with open(self.history_file, "w", encoding='utf-8') as f:
                    f.write("=== 加密消息历史记录 ===\n")
        except Exception as e:
            self.show_error(f"初始化历史文件失败：{str(e)}")

    def setup_ui(self):
        self.status_label = tk.Label(self.window, text="等待接收加密消息...")
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
                    # 读取加密文件
                    with open(self.file_path, "r", encoding='utf-8') as f:
                        content = f.read().splitlines()
                    
                    if len(content) >= 2:
                        encoded_data, encoded_signature = content[:2]
                        
                        # 解码数据
                        data = base64.b64decode(encoded_data.encode('utf-8'))
                        signature = base64.b64decode(encoded_signature.encode('utf-8'))
                        
                        # 验证签名
                        try:
                            self.public_key.verify(
                                signature,
                                data,
                                padding.PSS(
                                    mgf=padding.MGF1(hashes.SHA256()),
                                    salt_length=padding.PSS.MAX_LENGTH
                                ),
                                hashes.SHA256()
                            )
                            
                            # 解析原始数据
                            message, timestamp = data.decode('utf-8').split('|', 1)
                            
                            # 更新显示
                            self.msg_display.delete(1.0, tk.END)
                            self.msg_display.insert(tk.END, f"[{timestamp}]\n{message}")
                            self.status_label.config(text="收到验证通过的消息")
                            
                            # 记录历史
                            try:
                                with open(self.history_file, "a", encoding='utf-8') as hist:
                                    hist.write(f"[{timestamp}] {message}\n")
                            except Exception as e:
                                self.show_error(f"历史记录失败：{str(e)}")
                            
                            # 删除消息文件
                            os.remove(self.file_path)
                            
                        except Exception as e:
                            self.status_label.config(text="签名验证失败")
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