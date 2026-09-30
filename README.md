# 🏛️ 42 Project Archives & Technical Documentation

This repository serves as a centralized hub for the technical documentation, architectural breakdowns, and source code for the projects I build throughout the 42 curriculum.

While I do not share the proprietary 42 curriculum subjects or internal assets to respect the school's intellectual property, **I am providing the raw source code for my implementations** alongside comprehensive `README.md` files. These breakdowns focus on the core system engineering, algorithmic logic, and memory management strategies behind the software.

> **⚠️ Disclaimer for Active 42 Students:** The source code in this repository is provided for portfolio and educational purposes only. Do not copy or use this code for your own projects. Doing so violates the strict academic integrity policies of the 42 network and will result in severe penalties for plagiarism.

---

## Active Project Breakdowns

Below are the initial technical breakdowns. Each section links to an in-depth explanation of the system architecture, algorithms used, and the actual source code implementation.

### 🤖 [Rag against the machine](./Rag-against-the-machine/README.md)
* **Domain:** RAG & Information Retrieval
* **Core Focus:** Implementation of a retrieval-augmented generation pipeline using BM25 & faiss for hybrid search (lexical & semantic)  and local LLM inference (via llama.cpp/Transformers) to answer questions over a codebase and documentation corpus.
* **Documentation Link:** [Read the Rag against the machine Teardown](./Rag-against-the-machine/README.md)
* **Source Code:** [View Rag against the machine Source](./Rag-against-the-machine/src)

### 📞 [Call Me Maybe (Function Calling)](./call_me_maybe/README.md)
* **Domain:** LLM Inference & Structured Output Engineering
* **Core Focus:** Turning natural-language prompts into guaranteed-valid JSON function calls using a local 0.6B-parameter LLM (`Qwen3-0.6B`) and **constrained decoding** — masking token logits at every generation step so only schema-compliant tokens can be selected, making hallucinated or malformed output structurally impossible.
* **Documentation Link:** [Read the Call Me Maybe Teardown](./call_me_maybe/README.md)
* **Source Code:** [View Call Me Maybe Source](./call_me_maybe/src)

### 🐳 [Inception (System Administration)](./Inception/README.md)
* **Domain:** Containerization & DevOps Infrastructure
* **Core Focus:** Orchestration of a secure, multi-tier microservice architecture using Docker Compose, custom Dockerfiles, and persistent local volumes.
* **Documentation Link:** [Read the Inception Teardown](./Inception/README.md)
* **Source Code:** [View Inception Source](./Inception/src)

### 🎮 [Pacman Engine](./Pacman/README.md)
* **Domain:** Game Architecture & State Systems
* **Core Focus:** Implementation of real-time game loops, strict entity collision handling, and deterministic state management using Python.
* **Documentation Link:** [Read the Pacman Teardown](./Pacman/README.md)
* **Source Code:** [View Pacman Source](./Pacman/src)

### 🧩 [Amazing (Maze Gen)](./A_maz_ing/README.md)
* **Domain:** Graph Theory & Procedural Generation
* **Core Focus:** Advanced maze generation logic, grid traversal, and pathfinding heuristics packaged as a clean, modular Python utility.
* **Documentation Link:** [Read the Amazing Teardown](./A_maz_ing/README.md)
* **Source Code:** [View Amazing Source](./A_maz_ing/src)

---

*This documentation will update repeatedly as I progress through the curriculum.*
