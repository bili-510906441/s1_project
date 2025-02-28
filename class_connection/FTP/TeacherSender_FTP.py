# ============== 教师发送端 TeacherSender.py ==============
# ======== 由于无需使用FTP进行连接，此代码不再进行维护。 =========
import tkinter as tk
from tkinter import messagebox
import base64
import hashlib
from ftplib import FTP

class TeacherApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("教师信息发送端")
        
        # FTP配置（需要根据实际修改）
        self.ftp_config = {
            'host': '192.168.1.100',
            'user': 'teacher',
            'passwd': 'password',
            'filename': '/messages/class_msg.txt'
        }
        
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
            # Base64编码
            encoded = base64.b64encode(message.encode()).decode()
            
            # 计算SHA256哈希
            sha256_hash = hashlib.sha256(encoded.encode()).hexdigest()
            
            # 创建临时文件
            with open("temp_msg.txt", "w") as f:
                f.write(f"{encoded}\n{sha256_hash}")
                
            # 上传文件到FTP
            with FTP(self.ftp_config['host']) as ftp:
                ftp.login(self.ftp_config['user'], self.ftp_config['passwd'])
                with open("temp_msg.txt", "rb") as f:
                    ftp.storbinary(f"STOR {self.ftp_config['filename']}", f)
                    
            messagebox.showinfo("成功", "消息已安全发送")
            self.msg_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("错误", f"发送失败: {str(e)}")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = TeacherApp()
    app.run()