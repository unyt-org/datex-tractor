import os
from llama_cpp import Llama


class Prompt():
    def __init__(self, instruction):
        self.system_instruction = instruction
        self.chat = [instruction]

    def from_user(self, text: str):
        self.chat.append("<|im_start|>user\n" + text + "<|im_end|>")
        self.chat.append("<|im_start|>assistant\n")

    def from_assistant(self, text: str):
        self.chat[-1] += text

    def get_prompt(self):
        prompt = ""
        for line in self.chat:
            prompt += line
        return prompt

    @staticmethod
    def load_model():
        # Try loading model
        model_path = os.getenv("MODEL_PATH")
        prompt_path = os.getenv("PROMPT_PATH")
        try:
            llm = Llama(
                model_path=model_path,
                n_ctx=32768,  # 4096,
                verbose=False,
            )
        except Exception:
            print("Model not found.")
            raise FileNotFoundError("Unresolved model path")

        try:
            with open(prompt_path) as f:
                instruction = f.read().strip()
        except Exception:
            print("Prompt not found.")
            raise FileNotFoundError("Unresolved prompt path")

        return llm, instruction

    @staticmethod
    def gen_advice(llm, instruction: str, code_block: str):
        user_input = "```rust\n" + code_block + "\n```"

        # print("Init new prompt...")
        sysprom = Prompt(instruction)
        sysprom.from_user(user_input)
        prompt = sysprom.get_prompt()

        # print("Generating answer...")
        output = llm(

            prompt,
            max_tokens=1024,
            temperature=0.4,
            top_p=0.92,
            top_k=50,
            repeat_penalty=1.1,
            stop=["<|im_end|>"],
        )

        text_output = output["choices"][0]["text"]
        return text_output
