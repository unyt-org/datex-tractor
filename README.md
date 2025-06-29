# Todo exctractor
---
Sketch of a CLI tool for creation of todo lists from source code and optionally generation of LLM commenting on those todos.

Created to get up to speed in foreign codebases development process.

## Usage
---
Call for help...
```bash
python main.py -h
```

### Create list of todos
---
*Note*: Only python built-in libraries are used.
```bash
python main.py --src path_to_repo --answers path_to_answers
```
Creates a todo list at `path_to_answers/todo_list.md`.

### Generate advice regarding todos
---
*Note*: Requires dependencies.
```bash
python main.py --src path_to_repo --answers path_to_answers --mdl path_to_model --sys path_to_system_prompt
```
Generates **a file** named `fxxlxxxx.md` **for each** todo - containing:
- Path to the repo
- Line where todo was found
- Kind of todo was found
- Models response
- Block of code passed to the model to get that response

and stores it in `path_to_answers`.

*Developer comment*: 
Very naive integration and configuration. 

Hyperparameters, length of context and generated amount of output tokens will highly vary depending on the code base. 

The default configuration is adjusted to one specific usecase - the datex-core source code (Rust implementation)

If ran across different code bases it is possible of crashing the script by exceeding context length - this happens if the code base is too dense (or the initial systemprompt is too long). Naively this can be addressed with the adjustment of upper and lower margins of where the block of code is cut out of the file in question. On the other hand, if ran across less dense code bases those margins can be increased to prompt with more context (but what context length is useful or not will depend on the model...).

Primarily 
---
### Prerequisites from PyPI
---
```bash
pip install -r requirements.txt
```
or
```bash
pip install torch
pip install llama-cpp-python
```

### llama.cpp quickstart
---
Requirement: cmake
```bash
dnf install cmake
```

Installation:
```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
cmake -B build -DLLAMA_CURL=OFF
cmake --build build --config Release
```

The `llama.cpp` directory contains a subdirectory named `models` where the models are expected to be found. 

[Link to models](https://huggingface.co/TheBloke/deepseek-llm-7B-chat-GGUF/blob/main/README.md).

