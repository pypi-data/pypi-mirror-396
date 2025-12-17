# m8-core

**The Official Python Client & CLI for the M8P Hypervisor.**

> **Accelerate Intelligence. Maximize FLOPs. Optimize CAPEX.**

M8P is a unified execution engine for AI Agents, combining Vector Storage, Logic, and Inference into a single high-performance runtime. It eliminates the "Microservice Tax" of legacy stacks by running logic and data in a shared memory space (**Zero-Copy Execution**).

## Key Features

* **🚀 18% Lower Latency:** Optimized internal bus eliminates HTTP/JSON overhead.
* **📦 75% Less Complexity:** Replaces the typical stack (FastAPI + LangChain + FAISS + Llama.cpp) with a single binary.
* **🧠 Unified Memory:** Logic executes directly on data registers without network hops.
* **⚡ Native Streaming:** First-class opcode support for real-time token generation.

## Installation

```bash
pip install m8-core
````

Optional: For syntax highlighting in the CLI, install the toolkit:

```bash
pip install prompt_toolkit
```

# CLI Utility

You can use the command line tool to manage sessions and run scripts directly.

## Start a Session:

```
m8-core start my_session_v1
```

## Run a Script:

```
m8-core run myscript.m8 --session my_session_v1
```


## Stop/Cleanup:

```
m8-core stop my_session_v1
```


# API Usage 

```python
from m8_core import M8
SESSION_ID = "my_agent_v1"
```

## 1. Initialize Memory
```python
init_script = """
vdb_instance AGENT_MEM dim=4096 max_elements=10000
return "Ready"
"""
M8.EnsureExists(SESSION_ID, code=init_script)
```

## 2. Run Inference
```python
script = """
store <prompt> Why is the sky blue?
llm_openai <prompt> instance_name n_predict=75 force=true temperature=0.1
llm_instancestatus instance_name <out> #result of inference is stored in <out> by the instancestatus call
return <out>
"""
response = M8.RunSession(SESSION_ID, script)
print(response)
```

## 2. Streamming Inference

```python
script = """
store <prompt> Why is the sky blue?
llm_openai <prompt> instance_name n_predict=75 force=true temperature=0.1 stream=true
llm_instancestatus instance_name <out> 
#stream <out> # stream will just duplicate what llm_openai sent
return <out>
"""
response = M8.RunSession(SESSION_ID, script)
print(response)
```

## Requirements

```
Python 3.8+
requests
```