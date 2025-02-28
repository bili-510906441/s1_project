import tkinter as tk
from tkinter import messagebox
import base64
import os
from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

class TeacherApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("教师信息发送端")
        
        # 配置文件路径（需修改）
        self.file_path = r"E:\班级消息\message.dat"
        self.private_key_path = "teacher_private_key.pem"
        
        # 加载私钥
        try:
            with open(self.private_key_path, "rb") as key_file:
                self.private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                    backend=default_backend()
                )
        except Exception as e:
            messagebox.showerror("错误", f"密钥加载失败：{str(e)}")
            self.window.destroy()
        
        self.setup_ui()
        
    def setup_ui(self):
        tk.Label(self.window, text="输入要发送的消息：").pack(pady=5)
        self.msg_entry = tk.Entry(self.window, width=40)
        self.msg_entry.pack(pady=5)
        
        send_btn = tk.Button(self.window, text="加密发送", command=self.send_message)
        send_btn.pack(pady=10)
        
    def send_message(self):
        message = self.msg_entry.get()
        if not message:
            messagebox.showerror("错误", "消息内容不能为空")
            return
        
        try:
            # 生成时间戳
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 构建签名数据（消息+时间戳）
            data = f"{message}|{timestamp}".encode('utf-8')
            
            # 生成数字签名
            signature = self.private_key.sign(
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # 编码数据
            encoded_data = base64.b64encode(data).decode('utf-8')
            encoded_signature = base64.b64encode(signature).decode('utf-8')
            
            # 写入文件
            with open(self.file_path, "w", encoding='utf-8') as f:
                f.write(f"{encoded_data}\n{encoded_signature}")
                
            messagebox.showinfo("成功", "加密消息已安全发送")
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