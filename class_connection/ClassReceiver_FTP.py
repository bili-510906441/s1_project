# ============== 班级接收端 ClassReceiver.py ==============
import tkinter as tk
import base64
import hashlib
from ftplib import FTP
import threading

class ClassApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("班级信息接收端")
        
        # FTP配置（需要与发送端一致）
        self.ftp_config = {
            'host': '192.168.1.100',
            'user': 'student',
            'passwd': 'password',
            'filename': '/messages/class_msg.txt'
        }
        
        self.setup_ui()
        self.running = True
        self.start_checking()
        
    def setup_ui(self):
        self.status_label = tk.Label(self.window, text="等待接收消息...")
        self.status_label.pack(pady=10)
        
        self.msg_display = tk.Text(self.window, width=40, height=10)
        self.msg_display.pack(padx=10, pady=5)
        
        tk.Button(self.window, text="退出", command=self.shutdown).pack(pady=10)
        
    def check_messages(self):
        while self.running:
            try:
                with FTP(self.ftp_config['host']) as ftp:
                    ftp.login(self.ftp_config['user'], self.ftp_config['passwd'])
                    
                    # 下载文件
                    with open("temp_download.txt", "wb") as f:
                        ftp.retrbinary(f"RETR {self.ftp_config['filename']}", f.write)
                        
                    # 读取文件内容
                    with open("temp_download.txt", "r") as f:
                        content = f.read().splitlines()
                        
                    if len(content) == 2:
                        encoded, received_hash = content
                        
                        # 验证哈希
                        computed_hash = hashlib.sha256(encoded.encode()).hexdigest()
                        if computed_hash == received_hash:
                            decoded = base64.b64decode(encoded).decode()
                            self.msg_display.delete(1.0, tk.END)
                            self.msg_display.insert(tk.END, decoded)
                            self.status_label.config(text="收到新消息")
                            
                            # 删除服务器文件
                            ftp.delete(self.ftp_config['filename'])
                        else:
                            self.status_label.config(text="消息校验失败")
            except Exception as e:
                pass
            
            self.window.after(3000, self.check_messages)
            break
        
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