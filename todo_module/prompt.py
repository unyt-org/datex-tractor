class Prompt():
    def __init__(self, instruction):
        self.system_instruction = instruction
        self.chat = [instruction]

    def from_user(self, text: str):
        self.chat.append("<|user|>" + text)
        self.chat.append("<|assistant|>")

    def from_assistant(self, text: str):
        self.chat[-1] += text

    def get_prompt(self):
        prompt = ""
        for line in self.chat:
            prompt += line
        return prompt

if __name__ == "__main__":
    print("This file contains the Prompt class definition for todo-extractor.")
