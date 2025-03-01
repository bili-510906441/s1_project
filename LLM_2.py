import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue
import time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, StoppingCriteria
import numpy as np


class RepetitionDetector(StoppingCriteria):
    """智能重复检测终止器"""
    def __init__(self, max_ngram=3, repeat_threshold=2, max_history=512):
        self.ngram_history = []
        self.max_ngram = max_ngram
        self.repeat_threshold = repeat_threshold
        self.max_history = max_history
        self.repeat_count = 0
        
    def __call__(self, input_ids, scores, **kwargs):
        current_ngrams = self._extract_ngrams(input_ids[0], n=self.max_ngram)
        
        # 检测重复模式
        if self._has_repetition(current_ngrams):
            self.repeat_count += 1
            if self.repeat_count >= self.repeat_threshold:
                return True  # 触发终止
        else:
            self.repeat_count = 0
            
        # 维护历史记录
        self.ngram_history.extend(current_ngrams)
        if len(self.ngram_history) > self.max_history:
            self.ngram_history = self.ngram_history[-self.max_history:]
            
        return False

    def _extract_ngrams(self, token_ids, n=3):
        """提取n-gram特征"""
        return [tuple(token_ids[i:i+n].tolist()) for i in range(len(token_ids)-n+1)]

    def _has_repetition(self, current_ngrams):
        """判断是否出现重复模式"""
        if not self.ngram_history:
            return False
            
        # 计算重复率
        match_count = 0
        for ngram in current_ngrams[-5:]:  # 检查最后5个ngram
            if ngram in self.ngram_history:
                match_count += 1
                
        return match_count / len(current_ngrams) > 0.3  # 30%重复视为异常



class ChatGUI(tk.Tk):
    """支持长文本稳定流式输出的聊天界面"""
    
    def __init__(self, model_name="gpt2"):
        super().__init__()
        self.title("智能助手 (稳定流式版)")
        self.geometry("1000x800")
        
        # 初始化模型
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        
        # 流式控制组件
        self.stop_event = threading.Event()
        self.output_queue = queue.Queue()
        self.generating = False
        
        # 初始化界面
        self._create_widgets()
        self._setup_bindings()
        
        # 启动队列处理器
        self.after(100, self._process_queue)
        
        # 延迟加载模型
        self.after(500, self._load_model)

    def _create_widgets(self):
        """创建界面组件"""
        # 历史对话区域
        self.history_area = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            font=("微软雅黑", 12),
            padx=15,
            pady=15,
            state='disabled'
        )
        self.history_area.tag_config("user", foreground="#1f77b4")
        self.history_area.tag_config("assistant", foreground="#2ca02c")
        self.history_area.grid(row=0, column=0, columnspan=3, sticky="nsew")

        # 输入区域
        self.input_frame = ttk.Frame(self)
        self.input_text = ttk.Entry(
            self.input_frame,
            width=80,
            font=("微软雅黑", 12)
        )
        self.input_text.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # 控制按钮
        self.send_button = ttk.Button(
            self.input_frame,
            text="发送",
            command=self._start_generation,
            state=tk.DISABLED
        )
        self.send_button.pack(side=tk.LEFT, padx=5)
        self.input_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

        # 取消按钮
        self.cancel_button = ttk.Button(
            self,
            text="取消生成",
            command=self._cancel_generation,
            state=tk.DISABLED
        )
        self.cancel_button.grid(row=2, column=2, padx=10, sticky="e")

        # 布局配置
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def _setup_bindings(self):
        """事件绑定"""
        self.input_text.bind("<Return>", lambda e: self._start_generation())
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _load_model(self):
        """后台加载模型"""
        threading.Thread(target=self._async_load_model, daemon=True).start()

    def _async_load_model(self):
        """模型加载线程"""
        try:
            self._update_status("正在加载模型...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map="auto",
                torch_dtype=torch.float16,
                max_memory={0: "20GiB"}
            )
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.send_button.config(state=tk.NORMAL)
            self._update_status("就绪")
        except Exception as e:
            self._update_status(f"模型加载失败: {str(e)}")

    def _start_generation(self):
        """启动生成流程"""
        if not self.model or self.generating:
            return
        
        user_input = self.input_text.get().strip()
        if not user_input:
            return
        
        # 初始化状态
        self.generating = True
        self.send_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.input_text.delete(0, tk.END)
        self._append_message(f"用户: {user_input}\n", "user")
        
        # 启动生成线程
        threading.Thread(
            target=self._async_generate,
            args=(user_input,),
            daemon=True
        ).start()

    def _async_generate(self, prompt):
        """生成线程"""
        try:
            # 初始化重复检测器
            repetition_detector = RepetitionDetector(
                max_ngram=3,
                repeat_threshold=20
            )

            streamer = SafeStreamer(
                self.output_queue,
                self.stop_event,
                self.tokenizer
            )
            
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            generation_args = {
                **inputs,
                "max_new_tokens": 2048,
                "streamer": streamer,
                "temperature": 0.75,
                "repetition_penalty": 1.3,  # 添加重复惩罚
                "stopping_criteria": [repetition_detector],
                "pad_token_id": self.tokenizer.eos_token_id,
                "num_return_sequences": 1
            }
            
            gen_thread = threading.Thread(
                target=self.model.generate,
                kwargs=generation_args,
                daemon=True
            )
            gen_thread.start()
            
            # 监控生成状态
            while gen_thread.is_alive():
                if self.stop_event.is_set():
                    gen_thread.join(timeout=1)
                    break
                time.sleep(0.1)
                if repetition_detector.repeat_count > 0:
                    self.output_queue.put(("\n[检测到重复，已终止生成]", True))
            
            streamer.end()
            
        except Exception as e:
            self.output_queue.put((f"生成错误: {str(e)}", True))
        finally:
            self.generating = False
            self.stop_event.clear()

    def _cancel_generation(self):
        """取消生成"""
        self.stop_event.set()
        self.cancel_button.config(state=tk.DISABLED)
        self.send_button.config(state=tk.NORMAL)
        self._append_message("[生成已取消]\n", "system")

    def _process_queue(self):
        """处理输出队列"""
        while not self.output_queue.empty():
            text, end_flag = self.output_queue.get()
            self._update_stream(text, end_flag)
        self.after(100, self._process_queue)

    def _update_stream(self, text, stream_end):
        """单行更新式流式输出"""
        self.history_area.configure(state='normal')
        if "[检测到重复" in text:
            self.history_area.tag_add("warning", "end-2l", "end")
            self.history_area.tag_config("warning", foreground="red")
        try:
            # 获取当前行位置
            last_line_start = self.history_area.index("end-2l linestart")
            current_line_end = self.history_area.index("end-1l")

            # 删除当前行内容（保留"助手: "前缀）
            prefix_length = len("助手: ")
            keep_position = f"{last_line_start}+{prefix_length}c"
            self.history_area.delete(keep_position, current_line_end)

            # 插入新内容（自动换行处理）
            max_line_length = 120  # 每行最大字符数
            formatted_text = self._wrap_text(text, max_line_length, prefix_length)
            
            # 分段插入避免界面卡顿
            for i in range(0, len(formatted_text), 200):
                chunk = formatted_text[i:i+200]
                self.history_area.insert("end-1l", chunk, "assistant")
                self.history_area.see(tk.END)
                if i % 400 == 0:
                    self.update_idletasks()

            # 最终处理
            if stream_end:
                self.history_area.insert("end", "\n")  # 生成完成换行
        except tk.TclError as e:
            print(f"更新异常: {str(e)}")
            self._reset_display()
        finally:
            self.history_area.configure(state='disabled')

    def _wrap_text(self, text, max_length, prefix_len):
        """自动换行格式化"""
        wrapped = []
        current_line = ""
        for char in text:
            if len(current_line) - prefix_len >= max_length and char in ('，', '。', '！', '？', ' '):
                wrapped.append(current_line + char)
                current_line = ""
            else:
                current_line += char
        if current_line:
            wrapped.append(current_line)
        return "\n".join(wrapped)

    def _append_message(self, text, role):
        """安全添加消息"""
        self.history_area.configure(state='normal')
        self.history_area.insert("end", text, role)
        self.history_area.configure(state='disabled')
        self.history_area.see(tk.END)

    def _reset_display(self):
        """界面恢复"""
        self.history_area.configure(state='normal')
        self.history_area.delete(1.0, tk.END)
        self.history_area.insert(tk.END, "对话显示已重置\n", "system")
        self.history_area.configure(state='disabled')

    def _update_status(self, message):
        """状态更新"""
        self._append_message(f"系统: {message}\n", "system")

    def _on_close(self):
        """关闭清理"""
        self.stop_event.set()
        if self.model:
            del self.model
            torch.cuda.empty_cache()
        self.destroy()

class SafeStreamer:
    """稳定流式处理器"""
    
    def __init__(self, queue, stop_event, tokenizer):
        self.output_queue = queue
        self.stop_event = stop_event
        self.tokenizer = tokenizer
        self.byte_buffer = bytearray()  # 字节缓冲区
        self.text_buffer = []
        self.lock = threading.Lock()
        self.last_update = time.time()
        
    def put(self, token_ids):
        """处理token"""
        with self.lock:
            if self.stop_event.is_set():
                raise StopIteration("生成已取消")
            
            # 转换格式
            if isinstance(token_ids, torch.Tensor):
                token_ids = token_ids.cpu().tolist()
                
            # 处理批次维度
            if isinstance(token_ids, list) and len(token_ids) > 0:
                if isinstance(token_ids[0], list):
                    token_ids = token_ids[0]
            
            # 转换为字节数据
            bytes_data = self.tokenizer.decode(token_ids, skip_special_tokens=False).encode('utf-8')
            self.byte_buffer.extend(bytes_data)
            
            # 尝试解码
            try:
                decoded = self.byte_buffer.decode('utf-8')
                self.text_buffer.append(decoded)
                self.byte_buffer.clear()
            except UnicodeDecodeError:
                # 保留最多3字节（UTF8字符最大长度）
                keep_bytes = min(3, len(self.byte_buffer))
                self.byte_buffer = self.byte_buffer[-keep_bytes:]
            
            # 限流发送（每秒最多10次）
            if time.time() - self.last_update > 0.1:
                self._send_update()
                self.last_update = time.time()
                
    def end(self):
        """结束处理"""
        with self.lock:
            self._send_update(final=True)
        
    def _send_update(self, final=False):
        """发送更新"""
        if not self.text_buffer:
            return
            
        full_text = self._clean_text("".join(self.text_buffer))
        
        if final:
            self.output_queue.put((full_text, True))
            self.text_buffer.clear()
        else:
            self.output_queue.put((full_text, False))
            # 智能保留上下文
            if len(full_text) > 100:
                last_sep = max(
                    full_text.rfind('。', -100),
                    full_text.rfind('！', -100),
                    full_text.rfind('？', -100),
                    full_text.rfind('\n', -100),
                    -100
                )
                self.text_buffer = [full_text[last_sep+1:]] if last_sep != -1 else [full_text[-100:]]
    
    def _clean_text(self, text):
        """文本清洗"""
        markers = ["<|im_end|>", "<|im_start|>", "<|endoftext|>"]
        for marker in markers:
            text = text.replace(marker, "")
        return text.encode('utf-8', 'ignore').decode('utf-8')

if __name__ == "__main__":
    app = ChatGUI(model_name=r"E:\LLM_models\Qwen2_5-0_5B-Instruct")  # 替换实际模型
    app.mainloop()