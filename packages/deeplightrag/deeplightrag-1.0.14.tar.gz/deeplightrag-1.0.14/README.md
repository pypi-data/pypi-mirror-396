# DeepLightRAG

DeepLightRAG is a high-performance document indexing and retrieval system designed to work with any Large Language Model (LLM). It features a dual-layer graph architecture (Visual-Spatial and Entity-Relationship) to provide context-aware and visually-grounded retrieval.

## Features

- **Dual-Layer Graph**: Combines visual layout awareness with semantic entity relationships.
- **Visual-Grounded Retrieval**: Retrieves not just text, but visual regions and their spatial context.
- **Robust OCR**: Integrated with DeepSeek-OCR and EasyOCR fallback for reliable text extraction.
- **Advanced NER**: Uses GLiNER for zero-shot entity recognition.
- **Flexible LLM Support**: Compatible with OpenAI, Google Gemini, Anthropic, and local LLMs via MLX/Ollama.

## Installation

```bash
pip install deeplightrag
```

## Usage

Index a document:
```bash
deeplightrag index document.pdf
```

Query the index:
```bash
deeplightrag query "What is the main topic?"
```

## License

MIT License
