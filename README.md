# Todo exctractor
---
Sketch of a CLI tool for creation of todo lists from source code and optionally generation of LLM commenting on those todos.

## Usage
---
Intended usecases are:
- Snapshot source into a todo list (no llm)
- Generate advice for all there is todo on the todo list (llm implementation)

Main mode of operation
```bash
python main.py -h
```

### Create list
---
- Requires just Python
- Creates a todo list at `path_to_answers/todo_list.md`.

#### Command 
```bash
python main.py --src path_to_repo --answers path_to_answers
```

### Generate advice 
---
- Requires the setup of third party dependencies. 
- The given setup and configuration are meant to run a (small) LLM via CPU (usually *much* slower than via GPU).

#### Prerequisites from PyPI
---
```bash
pip install -r requirements.txt
```
or
```bash
pip install torch
pip install llama-cpp-python
```

#### llama.cpp quickstart
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

#### Command
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

and stores it at `path_to_answers`.

# Developer Notes 
## Core problem to solve (in progress)
- Keeping up with documentation.

## Sketching a Prototype (unstable)
### Data processing pipeline (integrated)
- Repo crawler with regex scanner (simplified)
  - Scan for markers (simplified)
- Data extraction and manipulation pipeline (simplified)
  - Extract, Manipulate, Evaluate (naive)

### Feature without llm (integrated)
- Snapshot of current state (simplified)
  - Save AI independend snapshot to storage (simplified)

### Feature with llm (integrated)
- Hyperparameter adjustment (simplified)
  - Automation of I/O flow from data to model to output (naive)
  - Save AI comments to storage (naive)

#### Prototype testing (success)
*Naive testruns on full source code of datex-core source code on GPU-less Laptop*
- Naively maximised context (aimed at high detailed)
  - 1,200 max tokens
  - 75 lines as upper and lower margins
  - Highly detailed answers (seemingly)
  - Slow calculation times (8h on single test)
  - Not feasable on regular bases
- Lower context (at the cost of detail)
  - Adjustments for efficiency (naive)
    - Reduced upper and lower margins to 10 
      - Improved stability (naive)
    - Reduced max tokens to 512
  - Cut execution time (from 8h to 3h on test)
  - Feasable for weekly commented snapshot (success)
