#!/bin/bash

# OmniSync Python SDK Installation and Test Script

echo "🚀 Installing OmniSync Python SDK..."
echo ""

# Navigate to SDK directory
cd "$(dirname "$0")/sdk/python" || exit 1

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

echo ""
echo "✅ Installation complete!"
echo ""

# Verify installation
echo "🔍 Verifying installation..."
python3 -c "import omnisync; print(f'OmniSync version: {omnisync.__version__}')" || echo "⚠️  Import check failed"

echo ""
echo "🧪 Running simple agent test..."
echo ""

# Navigate to examples directory
cd ../../examples || exit 1

# Run the simple test
python3 simple_agent_test.py

echo ""
echo "✅ Test complete!"
echo ""
echo "📝 Next steps:"
echo "   1. View Hub UI: http://localhost:3001"
echo "   2. View API Docs: http://localhost:8080/docs"
echo "   3. Run multi-agent demo: python3 ollama_multi_agent.py"
echo ""

