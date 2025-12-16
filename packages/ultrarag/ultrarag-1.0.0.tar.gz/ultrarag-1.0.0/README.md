# 🚀 UltraRAG - Complete Unified Package

**The ONLY RAG package you need!**

✅ Revolutionary RAG engine  
✅ Built-in Ollama integration  
✅ Built-in FastAPI + Swagger UI  
✅ **ONE command to start!**  
✅ Zero configuration needed!

---

## 🎯 Quick Start (2 Commands!)

### Step 1: Install

```bash
pip install ultrarag[server]
```

### Step 2: Start Server

```bash
ultrarag serve --ollama-host localhost --ollama-model llama3.2
```

**Open Swagger UI:**
```
http://localhost:8000/docs
```

🎉 **DONE! RAG chatbot ready!**

---

## 📚 Three Ways to Use

### Method 1: Web Server (with Swagger UI)

```bash
# Start server
ultrarag serve --ollama-host localhost --ollama-model llama3.2

# Open browser → http://localhost:8000/docs
# Upload documents, ask questions via Swagger!
```

### Method 2: Python Code (Simple)

```python
from ultrarag import RAG

# Create RAG
rag = RAG()

# Add document
rag.add("Python is a programming language created by Guido van Rossum.")

# Ask question
answer = rag.ask("Who created Python?")
print(answer)
# Output: "Python is a programming language created by Guido van Rossum."
```

### Method 3: Python Code (with Ollama)

```python
from ultrarag import RAG, OllamaLLM

# Initialize Ollama
llm = OllamaLLM(host="localhost", port=11434, model="llama3.2")

# Create RAG
rag = RAG()

# Add document
rag.add("Python is used for AI, web development, and data science.")

# Get context
query = "What is Python used for?"
query_analysis = rag.query_processor.analyze(query)
chunks = rag.retriever.retrieve(rag.chunks, query_analysis, top_k=3)
context = " ".join([c.text for c in chunks])

# Generate with LLM
prompt = f"Based on: {context}\n\nQuestion: {query}\n\nAnswer:"
answer = llm.generate(prompt)
print(answer)
```

---

## 🎯 Complete Example (CLI Server)

### Prerequisites

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama
ollama serve

# Pull model (in another terminal)
ollama pull llama3.2
```

### Install UltraRAG

```bash
pip install ultrarag[server]
```

### Start Server

```bash
ultrarag serve --ollama-host localhost --ollama-model llama3.2
```

**Output:**
```
🚀 Starting UltraRAG Server...
📡 Ollama: localhost:11434
🤖 Model: llama3.2
📚 Swagger UI: http://localhost:8000/docs
```

### Use Swagger UI

1. **Open:** `http://localhost:8000/docs`

2. **Upload document:**
   - Click `POST /upload`
   - Choose file
   - Execute

3. **Ask question:**
   - Click `POST /query`
   - Enter:
     ```json
     {
       "question": "Your question?",
       "use_llm": true
     }
     ```
   - Execute

4. **Get answer!** ✅

---

## 🔧 Configuration Options

### Server Command

```bash
ultrarag serve \
  --ollama-host localhost \      # Ollama IP
  --ollama-port 11434 \          # Ollama port
  --ollama-model llama3.2 \      # Model name
  --port 8000                     # Server port
```

### Different Ollama Machine

```bash
ultrarag serve --ollama-host 192.168.1.100 --ollama-model llama3.2
```

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/docs` | GET | Swagger UI |
| `/upload` | POST | Upload file |
| `/upload-text` | POST | Upload text |
| `/query` | POST | Ask question |
| `/stats` | GET | Statistics |
| `/clear` | DELETE | Clear documents |

---

## 💻 Python API

### Basic Usage

```python
from ultrarag import RAG

rag = RAG()
rag.add("document text...")
answer = rag.ask("question?")
```

### With Ollama

```python
from ultrarag import RAG, OllamaLLM

llm = OllamaLLM(host="localhost", model="llama3.2")
rag = RAG()

# Test Ollama
if llm.test():
    print("✅ Ollama connected")
else:
    print("❌ Ollama not available")

# Add documents
rag.add("Your documents...")

# Generate answer
chunks = rag.retriever.retrieve(rag.chunks, query_analysis, top_k=3)
context = " ".join([c.text for c in chunks])
answer = llm.generate(f"Context: {context}\n\nQuestion: {question}")
```

### Advanced Usage

```python
# Custom configuration
rag = RAG(
    min_chunk_completeness=0.85,
    min_grounding_score=0.85
)

# Add with metadata
rag.add("text...", metadata={"source": "doc1.pdf"})

# Detailed response
response = rag.ask("question?", explain=True)
print(f"Answer: {response.answer}")
print(f"Confidence: {response.confidence}")
print(f"Grounding: {response.grounding_score}")
print(f"Verdict: {response.metadata['verdict']}")

# Statistics
stats = rag.get_stats()
print(f"Total chunks: {stats['total_chunks']}")
```

---

## 🎯 Installation Options

### Minimal (RAG only)

```bash
pip install ultrarag
```

**Use in Python code only (no web server)**

### Full (RAG + Web Server)

```bash
pip install ultrarag[server]
```

**Includes FastAPI + Swagger UI**

### From Source

```bash
git clone https://github.com/kumar123ips/ultrarag
cd ultrarag
pip install -e .[server]
```

---

## 🔥 Features

### Revolutionary RAG Components

✅ **AtomicChunk** - Guaranteed completeness (ICS ≥ 0.75)  
✅ **QueryDNA** - Multi-dimensional query analysis  
✅ **AdaptiveRetriever** - Intent-based retrieval  
✅ **ProvenAnswer** - Mathematical validation  
✅ **Zero Dependencies** - Core package is pure Python!

### Built-in Integrations

✅ **Ollama** - Local LLM support  
✅ **FastAPI** - Production web server  
✅ **Swagger UI** - Interactive API docs  
✅ **CLI** - One command to start!

---

## 📝 License

MIT License - see [LICENSE](LICENSE)

---

## 👤 Author

**Abhishek Kumar**  
Email: ipsabhi420@gmail.com  
GitHub: [@kumar123ips](https://github.com/kumar123ips)

---

## 🎉 Success!

**The ONLY RAG package you need!**

```bash
pip install ultrarag[server]
ultrarag serve --ollama-model llama3.2
```

**That's it!** 🚀

---

**Made with ❤️ by Abhishek Kumar**
