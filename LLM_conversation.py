from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# 初始化模型和分词器
model_name = "D:\Deepseek-R1"  # 可替换为您选择的模型
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# 设置设备（优先使用GPU）
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# 对话历史管理类
class ChatHistory:
    def __init__(self, tokenizer, max_length=1000):
        self.history = []
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def add_user_input(self, text):
        self.history.append(f"用户: {text}")
    
    def add_bot_response(self, text):
        self.history.append(f"助手: {text}")
    
    def get_full_history(self):
        return "\n".join(self.history[-self.max_length:])  # 保留最近的对话
    
    def generate_prompt(self):
        return self.get_full_history() + "\n助手: "

# 生成参数配置
generation_config = {
    "max_length": 4096,        # 最大生成长度
    "min_length": 16,          # 最小生成长度
    "temperature": 0.6,        # 生成温度（0-1，越高越随机）
    "top_k": 50,               # top-k采样
    "top_p": 0.9,              # nucleus采样
    "repetition_penalty": 1.2, # 重复惩罚因子
    "num_beams": 5,            # beam search数量
    "early_stopping": True     # 提前停止生成
}

def generate_response(history):
    # 准备输入
    prompt = history.generate_prompt()
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    # 生成响应
    with torch.no_grad():
        outputs = model.generate(
            inputs.input_ids,
            attention_mask=inputs.attention_mask,
            **generation_config
        )
    
    # 解码响应
    response = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True,
        clean_up_tokenization_spaces=True
    )
    
    # 提取最新回复
    response = response[len(prompt):].strip()
    return response.split("用户:")[0].split("助手:")[0].strip()

# 主对话循环
def chat():
    print("开始对话（输入'退出'结束）")
    history = ChatHistory(tokenizer)
    
    while True:
        user_input = input("用户: ")
        
        if user_input.lower() in ["退出", "exit", "quit"]:
            print("对话结束，按Enter退出。")
            break
            
        history.add_user_input(user_input)
        
        # 生成回复
        response = generate_response(history)
        print(f"助手: {response}")
        
        # 更新历史记录
        history.add_bot_response(response)

if __name__ == "__main__":
    chat()
