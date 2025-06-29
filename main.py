import os
import sys
# Third party import 
from llama_cpp import Llama 

from todo_module import parse_args, TodoContext, Prompt

def main():
    # Parse CLI
    if parse_args():
        todo_paths, answers_path, model_path, instruction = parse_args()
        print(f"Answers: {answers_path}")
        print(f"Model: {model_path}")
        print(f"Instruction: {instruction}")

    # If return was 0 -> exit script
    else:
        sys.exit("Successful end of script.")

    # Assuming validated parameters from here on

    # Load model
    llm = Llama(
        model_path=model_path,
        # Context length
        n_ctx=4096, # max: 4096, 2048, 1024, 512, ...
        verbose=False,
    )

    for i, todo_path in enumerate(todo_paths):
        for j, code_block in enumerate(todo_path.code_blocks):
            user_input = "```rust\n...\n" + "".join(code_block[2]) + "\n...\n```"
            print("\nRequest:\n")
            print(user_input)


            print("\nInit new prompt...")
            sysprom = Prompt(instruction)
            sysprom.from_user(user_input)
            prompt = sysprom.get_prompt()

            print("\nGenerating answer...\n")
            output = llm(
                prompt,
                max_tokens=1_200, # roughly: max_tokens/4 = max_words for response
                temperature=0.4, # bound between 1: Highly creative; 0: on point
                top_p=0.9, # top tokens: perspective from percentage
                top_k=60, # top tokens: perspective from total
                repeat_penalty=1.1, # Penalty on repition of tokens
                stop=["<|user|>", "<|system|>"],
             )
            text_output = output["choices"][0]["text"]
            print(text_output)

            print("\nWriting file with answer...")
            file_name = f"f{i:02n}l{todo_path.line_numbers[j]:04n}.md"
            file_path = os.path.join(answers_path, file_name)

            with open(file_path, "w") as f:
                f.write(f"'{todo_path.path}'\n")
                f.write(f"'{todo_path.line_numbers[j]}'\n")
                f.write(f"'{todo_path.descriptions[j]}'\n")

                f.write("Answer:\n")
                f.write("```plaintext\n" + text_output + "\n```\n")

                f.write("\nPassed prompt:\n")
                f.write(user_input)

if __name__ == "__main__":
    main()
