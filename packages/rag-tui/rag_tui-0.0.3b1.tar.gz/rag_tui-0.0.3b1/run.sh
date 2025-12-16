#!/bin/bash

# RAG-TUI v2.0 Launch Script
# Enterprise Chunking Debugger

echo "🚀 RAG-TUI v2.0 - Enterprise Chunking Debugger"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

# Check for Ollama (optional)
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama detected - full features available"
else
    echo "⚠️  Ollama not running - Search/Chat features disabled"
    echo "   To enable: ollama serve"
fi

echo ""
echo "📦 Starting RAG-TUI..."
echo ""

# Run the app
python3 -m rag_tui.app
