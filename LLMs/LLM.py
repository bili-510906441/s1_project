import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue
import time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import psutil

class ChatGUI(tk.Tk):
    """主聊天界面，整合所有优化功能"""
    
    def __init__(self, model_name="gpt2"):
        super().__init__()
        self.title("智能助手 (优化版)")
        self.geometry("800x600")
        
        # 初始化模型组件
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        
        # 线程控制变量
        self.generating = False
        self.stop_event = threading.Event()
        self.output_queue = queue.Queue()
        
        # 初始化界面组件
        self._create_widgets()
        self._setup_bindings()
        
        # 启动队列处理循环
        self.after(100, self._process_output_queue)
        
        # 延迟加载模型（避免界面冻结）
        self.after(500, self._load_model)

    def _create_widgets(self):
        """创建界面组件"""
        # 历史对话区域
        self.history_area = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            font=("微软雅黑", 12),
            padx=10,
            pady=10,
            state='disabled'
        )
        self.history_area.tag_config("user", foreground="#2c7fb8")
        self.history_area.tag_config("assistant", foreground="#31a354")
        self.history_area.grid(row=0, column=0, columnspan=3, sticky="nsew")

        # 输入区域
        self.input_frame = ttk.Frame(self)
        self.input_text = ttk.Entry(
            self.input_frame,
            width=60,
            font=("微软雅黑", 12)
        )
        self.input_text.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # 功能按钮
        self.send_button = ttk.Button(
            self.input_frame,
            text="发送",
            command=self._start_generation,
            state=tk.DISABLED
        )
        self.send_button.pack(side=tk.LEFT, padx=5)
        self.input_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

        # 取消按钮（新增）
        self.cancel_button = ttk.Button(
            self,
            text="取消生成",
            command=self._cancel_generation,
            state=tk.DISABLED
        )
        self.cancel_button.grid(row=2, column=2, padx=5, sticky="e")

        # 配置网格布局权重
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def _setup_bindings(self):
        """设置事件绑定"""
        self.input_text.bind("<Return>", lambda e: self._start_generation())
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _load_model(self):
        """异步加载模型"""
        threading.Thread(target=self._async_load_model, daemon=True).start()

    def _async_load_model(self):
        """后台加载模型"""
        try:
            self._update_status("正在加载模型...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map="auto",
                torch_dtype=torch.float16,
                max_memory={0: "6GiB"}
            )
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.send_button.config(state=tk.NORMAL)
            self._update_status("就绪")
        except Exception as e:
            self._update_status(f"模型加载失败: {str(e)}")

    def _start_generation(self):
        """启动生成线程"""
        if not self.model or self.generating:
            return
        
        # 获取用户输入
        user_input = self.input_text.get().strip()
        if not user_input:
            return
        
        # 更新界面状态
        self.generating = True
        self.send_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.input_text.delete(0, tk.END)
        
        # 显示用户消息
        self._append_message(f"用户: {user_input}\n", "user")
        
        # 启动生成线程
        threading.Thread(
            target=self._async_generate,
            args=(user_input,),
            daemon=True
        ).start()

    def _async_generate(self, prompt):
        """异步生成线程"""
        try:
            # 初始化流处理器
            streamer = EnhancedStreamer(
                self.output_queue,
                self.stop_event,
                self.tokenizer
            )
            
            # 生成参数配置
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            generation_args = {
                **inputs,
                "max_new_tokens": 4096,
                "streamer": streamer,
                "temperature": 0.7,
                "pad_token_id": self.tokenizer.eos_token_id,
                "num_return_sequences": 1  # 确保单批次输出
            }
            
            # 启动生成线程
            gen_thread = threading.Thread(
                target=self.model.generate,
                kwargs=generation_args,
                daemon=True
            )
            gen_thread.start()
            
            # 等待生成完成或取消
            while gen_thread.is_alive():
                if self.stop_event.is_set():
                    gen_thread.join(timeout=1)
                    break
                time.sleep(0.1)
            
            # 最终处理
            streamer.end()
            
        except Exception as e:
            self.output_queue.put((f"生成错误: {str(e)}", True))
        finally:
            self.generating = False
            self.stop_event.clear()

    def _cancel_generation(self):
        """取消生成操作"""
        self.stop_event.set()
        self.cancel_button.config(state=tk.DISABLED)
        self.send_button.config(state=tk.NORMAL)
        self._append_message("[生成已取消]\n", "system")

    def _process_output_queue(self):
        """处理输出队列（主线程定时调用）"""
        while not self.output_queue.empty():
            text, end_flag = self.output_queue.get()
            self._update_stream(text, end_flag)
        self.after(100, self._process_output_queue)

    def _update_stream(self, text, stream_end):
        """增强版流式更新（带分块处理）"""
        self.history_area.configure(state='normal')
        try:
            # 删除临时行（兼容多行内容）
            start_pos = self.history_area.index("end-2l linestart")
            end_pos = self.history_area.index("end-1l")
            self.history_area.delete(start_pos, end_pos)
            
            # 分块插入避免界面卡顿
            chunk_size = 500  # 每500字符分割一次
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i+chunk_size]
                self.history_area.insert("end-1l", f"助手: {chunk}", "assistant")
                self.history_area.see(tk.END)
                self.update_idletasks()  # 强制刷新
                
            # 最终换行处理
            if stream_end:
                self.history_area.insert("end", "\n")
                self.history_area.see(tk.END)
                
        except tk.TclError as e:
            print(f"界面更新异常: {str(e)}")
            self._reset_display()
        finally:
            self.history_area.configure(state='disabled')

    def _append_message(self, text, role):
        """安全添加消息"""
        self.history_area.configure(state='normal')
        self.history_area.insert("end", text, role)
        self.history_area.configure(state='disabled')
        self.history_area.see(tk.END)

    def _reset_display(self):
        """界面异常恢复"""
        self.history_area.configure(state='normal')
        self.history_area.delete(1.0, tk.END)
        self.history_area.insert(tk.END, "显示异常，已重置对话记录\n")
        self.history_area.configure(state='disabled')

    def _update_status(self, message):
        """更新状态栏"""
        self.history_area.configure(state='normal')
        self.history_area.insert("end", f"系统: {message}\n", "system")
        self.history_area.configure(state='disabled')
        self.history_area.see(tk.END)

    def _on_close(self):
        """窗口关闭时的清理"""
        self.stop_event.set()
        if self.model:
            del self.model
            torch.cuda.empty_cache()
        self.destroy()

class EnhancedStreamer:
    """增强版流式处理器，支持取消操作"""
    
    def __init__(self, queue, stop_event, tokenizer):
        self.output_queue = queue
        self.stop_event = stop_event
        self.tokenizer = tokenizer
        self.buffer = []
        self.last_update = time.time()
        
    def put(self, token_ids):
        """处理接收到的token"""
        if self.stop_event.is_set():
            raise StopIteration("生成已取消")
        
        if isinstance(token_ids, torch.Tensor):
            token_ids = token_ids.cpu().tolist()
        
        # 处理批次维度（假设单批次）
        if isinstance(token_ids, list) and len(token_ids) > 0:
            if isinstance(token_ids[0], list):  # 多批次情况
                token_ids = token_ids[0]  # 取第一个批次

        # 解码文本
        text = self.tokenizer.decode(token_ids, skip_special_tokens=True)
        self.buffer.append(text)
        
        # 限流处理（每秒最多更新2次）
        if time.time() - self.last_update > 0.5:
            self._send_update()
            self.last_update = time.time()
            
    def end(self):
        """结束处理"""
        self._send_update(final=True)
        
    def _send_update(self, final=False):
        """发送更新到主线程"""
        if not self.buffer:
            return
            
        full_text = "".join(self.buffer)
        if final:
            # 最终处理
            self.output_queue.put((full_text, True))
            self.buffer.clear()
        else:
            # 发送当前缓冲内容
            self.output_queue.put((full_text, False))
            # 保留最后50个字符作为上下文缓存
            if len(full_text) > 50:
                self.buffer = [full_text[-50:]]

if __name__ == "__main__":
    # 启动应用
    app = ChatGUI(model_name=r"E:\reee\DeepSeek-R1-Distill-Qwen-1_5B")  # 可替换为实际模型名称
    app.mainloop()