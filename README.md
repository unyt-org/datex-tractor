# Todo exctractor
---
CLI tool for generation of todo lists.

## Dependencies
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

## Usage
---
Call for help...
```bash
python main.py -h
```

### Create list of todos
---
```bash
python main.py --src path_to_repo --answers path_to_answers
```
Creates a todo list at `path_to_answers/todo_list.md`.

### Generate advice regarding todos
---
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

