# Installing ChromaDB on Windows

ChromaDB requires Microsoft Visual C++ Build Tools to compile on Windows.

## Option 1: Install C++ Build Tools (Recommended)

1. **Download Microsoft C++ Build Tools:**

   - Visit: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Download "Build Tools for Visual Studio"

2. **Install:**

   - Run the installer
   - Select "C++ build tools" workload
   - Install (this may take a while)

3. **Install ChromaDB:**
   ```bash
   pip install chromadb
   ```

## Option 2: Use Pre-built Wheel (If Available)

Try installing a specific version that might have pre-built wheels:

```bash
pip install chromadb==0.4.22
```

## Option 3: Skip ChromaDB (RAG Optional)

ChromaDB is **optional** for basic functionality. The symptom checker will still work without it, just without RAG-enhanced context retrieval.

To skip ChromaDB:

- The RAG service will work in fallback mode
- Symptom analysis will still work, just without vector search
- You can add ChromaDB later when needed

## Verify Installation

After installing, test:

```python
import chromadb
print("ChromaDB installed successfully!")
```

