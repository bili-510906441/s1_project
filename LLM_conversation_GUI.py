import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, filedialog, simpledialog
import threading
import psutil
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer
import torch

DEFAULT_MODELS = {
    "Deepseek-R1": "deepseek-ai/deepseek-r1",
    "Llama2-7B": "meta-llama/Llama-2-7b-chat-hf",
    "ChatGLM3": "THUDM/chatglm3-6b",
    "Qwen": "E:\LLM_models\Qwen2_5-0_5B-Instruct",  # Qwen2.5-0.5B-Instruct
}

class ChatGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI对话助手 v3.0")
        self.geometry("1200x800")
        
        # 初始化配置
        self.current_model = "Qwen"
        self.model = None
        self.tokenizer = None
        self.chat_history = ChatHistory()
        self.generating = False
        self.input_tokens = 0
        self.generated_tokens = 0
        
        # 创建界面
        self._create_widgets()
        self._setup_menu()
        
        # 加载初始模型
        self.load_model(DEFAULT_MODELS[self.current_model])
        
        # 启动监控
        self.update_ram_usage()

    def _create_widgets(self):
        """创建界面组件"""
        # 状态栏
        self.status_bar = ttk.Frame(self)
        
        # 模型信息
        self.model_label = ttk.Label(self.status_bar, text=f"当前模型: {self.current_model}")
        self.model_label.pack(side=tk.LEFT, padx=10)
        
        # 内存信息
        self.ram_label = ttk.Label(self.status_bar, text="内存占用: 计算中...")
        self.ram_label.pack(side=tk.RIGHT, padx=10)
        
        # Token统计
        self.token_label = ttk.Label(self.status_bar, text="输入Token: 0 | 生成Token: 0")
        self.token_label.pack(side=tk.RIGHT, padx=10)
        
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 对话历史区域
        self.history_area = scrolledtext.ScrolledText(
            self, 
            wrap=tk.WORD, 
            state='disabled', 
            font=('Microsoft YaHei', 12),
            padx=15,
            pady=15
        )
        self.history_area.tag_config('user', foreground='#1E90FF', lmargin1=20, lmargin2=20)
        self.history_area.tag_config('assistant', foreground='#228B22', lmargin1=20, lmargin2=20)
        self.history_area.tag_config('stat', foreground='gray', font=('Microsoft YaHei', 9))
        self.history_area.pack(fill=tk.BOTH, expand=True)

        # 输入区域
        input_frame = ttk.Frame(self)
        input_frame.pack(fill=tk.X, padx=15, pady=15)
        
        self.input_entry = ttk.Entry(
            input_frame, 
            font=('Microsoft YaHei', 12)
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.bind("<Return>", lambda event: self.send_message())
        
        self.send_btn = ttk.Button(
            input_frame, 
            text="发送", 
            command=self.send_message
        )
        self.send_btn.pack(side=tk.RIGHT, padx=10)
        
        self.clear_btn = ttk.Button(
            input_frame,
            text="清空",
            command=self.clear_history
        )
        self.clear_btn.pack(side=tk.RIGHT)

    def _setup_menu(self):
        """配置菜单栏"""
        menubar = tk.Menu(self)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="保存历史", command=self.save_history)
        file_menu.add_command(label="加载历史", command=self.load_history)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_close)
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 模型菜单
        model_menu = tk.Menu(menubar, tearoff=0)
        model_menu.add_command(label="切换模型", command=self.switch_model)
        menubar.add_cascade(label="模型", menu=model_menu)
        
        self.config(menu=menubar)

    def update_ram_usage(self):
        """更新内存使用显示"""
        process = psutil.Process()
        mem = process.memory_info().rss / 1024**2  # 转换为MB
        self.ram_label.config(text=f"内存占用: {mem:.1f} MB")
        self.after(1000, self.update_ram_usage)

    def load_model(self, model_path: str):
        """加载新模型"""
        if self.generating:
            messagebox.showwarning("操作冲突", "请等待当前响应生成完成")
            return
        
        # 显示加载进度
        self.progress = ttk.Progressbar(
            self.status_bar, 
            mode='indeterminate',
            length=150
        )
        self.progress.pack(side=tk.LEFT, padx=10)
        self.progress.start()
        
        # 释放旧模型资源
        if self.model is not None:
            del self.model
            del self.tokenizer
            torch.cuda.empty_cache()
        
        def _load_task():
            try:
                # 加载模型和分词器
                new_model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto",
                    trust_remote_code=True
                ).to("cuda" if torch.cuda.is_available() else "cpu")
                
                new_tokenizer = AutoTokenizer.from_pretrained(
                    model_path,
                    trust_remote_code=True,
                    pad_token='<|endoftext|>'
                )
                
                # 更新UI
                self.after(0, lambda: self._finalize_model_load(
                    new_model, new_tokenizer, Path(model_path).name))
                
            except Exception as e:
                self.after(0, lambda e=e: messagebox.showerror(
                    "生成错误", 
                    f"发生错误: {str(e)}\n模型: {self.current_model}"
                    ))
        
        threading.Thread(target=_load_task).start()

    def _finalize_model_load(self, model, tokenizer, model_name):
        """完成模型加载"""
        self.model = model
        self.tokenizer = tokenizer
        self.current_model = model_name
        self.model_label.config(text=f"当前模型: {model_name} (加载中)")
        self.progress.stop()
        self.progress.destroy()
        self.model_label.config(text=f"当前模型: {model_name} (加载成功)")

    def _handle_load_error(self, error):
        """处理加载错误"""
        self.progress.stop()
        self.progress.destroy()
        messagebox.showerror("加载失败", f"错误信息:\n{str(error)}")

    def switch_model(self):
        """切换模型对话框"""
        choice = messagebox.askyesno("选择方式", "使用预置模型(Y)或本地模型(N)?")
        
        if choice:  # 预置模型
            model_list = "\n".join(DEFAULT_MODELS.keys())
            selected = simpledialog.askstring(
                "切换模型", 
                f"可选模型:\n{model_list}\n\n请输入模型名称:",
                parent=self
            )
            if selected and selected in DEFAULT_MODELS:
                self.load_model(DEFAULT_MODELS[selected])
        else:  # 本地模型
            path = filedialog.askdirectory(title="选择模型目录")
            if path:
                if self._validate_model_dir(path):
                    self.load_model(path)
                else:
                    messagebox.showerror("错误", "无效的模型目录")

    def _validate_model_dir(self, path):
        """验证模型目录有效性"""
        required_files = ["config.json", "pytorch_model.bin"]
        return all((Path(path)/f).exists() for f in required_files)

    def send_message(self):
        """处理用户输入"""
        if self.generating or not self.model:
            return
        
        user_input = self.input_entry.get().strip()
        if not user_input:
            return
        
        self.input_entry.delete(0, tk.END)
        self._append_message(user_input, "user")
        self.chat_history.add_query(user_input)
        
        threading.Thread(target=self.generate_response).start()

    def generate_response(self):
        """生成响应"""
        self.generating = True
        self.send_btn.config(state=tk.DISABLED)
        
        try:
            # 准备输入
            prompt = self.chat_history.generate_prompt()
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            self.input_tokens = inputs.input_ids.shape[1]
            
            # 生成配置
            torch.cuda.empty_cache()
            generation_config = {
                "max_new_tokens": 4096,
                "temperature": 0.6,
                "top_p": 0.9,
                "repetition_penalty": 1.2,
                "do_sample": True,
                "eos_token_id": self.tokenizer.eos_token_id or 151643,
                "pad_token_id": self.tokenizer.pad_token_id or 151643,
                "streamer": self.GUIStreamer(
                    self.tokenizer,
                    self.chat_history,
                    self._update_stream
                )
            }
            
            # 执行生成
            outputs = self.model.generate(**inputs, **generation_config)
            
            # 计算token统计
            self.generated_tokens = outputs[0].shape[0] - self.input_tokens
            self._update_token_stats()   
        except Exception as e:
            # 添加更详细的错误日志
            error_msg = f"{str(e)}\nDevice: {self.model.device}\nMemory: {torch.cuda.memory_allocated()/1e9:.1f}GB"
            self.after(0, lambda: messagebox.showerror("生成错误", error_msg))
        finally:
            self.generating = False
            self.send_btn.config(state=tk.NORMAL)

    class GUIStreamer(TextStreamer):
        """自定义流式处理器"""
        def __init__(self, tokenizer, chat_history, update_callback):
            super().__init__(tokenizer)
            self.buffer = []
            self.chat_history = chat_history
            self.update_callback = update_callback

        def on_finalized_text(self, text: str, stream_end: bool = False):
            # 更精确处理Qwen的特殊标记
            text = text.replace("<|im_end|>", "").strip()
            if "<|im_start|>" in text:
                text = text.split("<|im_start|>")[0]
            
            if text:
                # 添加去重逻辑
                new_text = text[len(''.join(self.buffer)):]
                if new_text:
                    self.buffer.append(text)
                    self.update_callback("".join(self.buffer))
            
            if stream_end:
                full_response = "".join(self.buffer).replace("<|endoftext|>", "").strip()
                self.chat_history.add_response(full_response)
                self.buffer = []

    def _update_stream(self, text):
        """更新流式输出"""
        try:
            self.history_area.configure(state='normal')
            last_line_start = self.history_area.index("end-2l linestart")
            self.history_area.delete(last_line_start, "end-1l")
        
            # 插入新内容
            self.history_area.insert("end-1l", f"助手: {text}\n", "assistant")
            '''
            self.history_area.delete("current_line", tk.END)
            self.history_area.insert(tk.END, f"助手: {text}\n", "assistant")
            self.history_area.tag_add("current_line", "end-2l", "end-1l")
            '''
            self.history_area.configure(state='disabled')
            self.history_area.see(tk.END)
            self.update_idletasks()
        except tk.TclError as e:
            print(f"界面更新错误: {str(e)}")
            self.history_area.delete(1.0, tk.END)
            self.history_area.insert(tk.END, "界面状态异常，已重置显示\n")

    def _update_token_stats(self):
        """更新token统计信息"""
        self.token_label.config(
            text=f"输入Token: {self.input_tokens} | 生成Token: {self.generated_tokens}"
        )
        self._append_message(
            f"[本次消耗] 输入Token: {self.input_tokens} | 生成Token: {self.generated_tokens}",
            "stat"
        )

    def _append_message(self, text, role):
        """添加消息到历史区域"""
        self.history_area.configure(state='normal')
        self.history_area.insert(tk.END, f"{'用户' if role == 'user' else '助手'}: {text}\n", role)
        self.history_area.configure(state='disabled')
        self.history_area.see(tk.END)

    def clear_history(self):
        """清空对话历史"""
        if messagebox.askyesno("确认", "确定要清空对话历史吗？"):
            self.chat_history = ChatHistory()
            self.history_area.configure(state='normal')
            self.history_area.delete(1.0, tk.END)
            self.history_area.configure(state='disabled')

    def save_history(self):
        """保存对话历史"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    content = self.history_area.get(1.0, tk.END)
                    f.write(content)
                messagebox.showinfo("保存成功", "对话历史已保存")
            except Exception as e:
                messagebox.showerror("保存失败", f"错误信息:\n{str(e)}")

    def load_history(self):
        """加载对话历史"""
        filepath = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                self.history_area.configure(state='normal')
                self.history_area.delete(1.0, tk.END)
                self.history_area.insert(tk.END, content)
                self.history_area.configure(state='disabled')
                messagebox.showinfo("加载成功", "对话历史已加载")
            except Exception as e:
                messagebox.showerror("加载失败", f"错误信息:\n{str(e)}")

    def on_close(self):
        """处理关闭事件"""
        if self.generating:
            if messagebox.askokcancel("退出", "正在生成响应，确定要强制退出吗？"):
                self.destroy()
        else:
            self.destroy()

class ChatHistory:
    """对话历史管理器"""
    def __init__(self):
        self.history = []
    
    def add_query(self, query: str):
        self.history.append(f"用户: {query}")
        self._trim_history()
    
    def add_response(self, response: str):
        self.history.append(f"助手: {response}")
        self._trim_history()
    
    def generate_prompt(self) -> str:
        # 适配Qwen的对话格式
        prompt = ""
        for msg in self.history:
            role = "user" if msg.startswith("用户:") else "assistant"
            content = msg.split(": ", 1)[1]
            prompt += f"<|im_start|>{role}\n{content}<|im_end|>\n"
        prompt += "<|im_start|>assistant\n"
        return prompt
    
    def _trim_history(self):
        """智能截断历史记录"""
        full_text = "\n".join(self.history)
        while len(full_text) > 2000 and len(self.history) > 2:
            self.history = self.history[2:]
            full_text = "\n".join(self.history)

if __name__ == "__main__":
    app = ChatGUI()
    app.mainloop()