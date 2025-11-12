#!/bin/bash

# OmniSync Setup Script
# This script sets up the OmniSync project

set -e

echo "🚀 OmniSync Setup Script"
echo "========================"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Setup Python SDK
echo "🐍 Setting up Python SDK..."
cd sdk/python
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
deactivate
cd ../..
echo "✅ Python SDK setup complete"
echo ""

# Setup JavaScript SDK (optional)
echo "📦 Setting up JavaScript SDK..."
cd sdk/js
if [ ! -d "node_modules" ]; then
    npm install
fi
cd ../..
echo "✅ JavaScript SDK setup complete"
echo ""

# Setup Hub Frontend
echo "⚛️  Setting up Hub Frontend..."
cd hub/frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
cd ../..
echo "✅ Hub Frontend setup complete"
echo ""

# Start Docker services
echo "🐳 Starting Docker services..."
docker-compose up -d
echo "✅ Docker services started"
echo ""

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running"
else
    echo "⚠️  Some services may not be running. Check with: docker-compose ps"
fi
echo ""

echo "🎉 Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Start Ollama (optional): ollama pull gpt-oss:120b-cloud"
echo "   2. Run an example: cd examples && python simple_agent_test.py"
echo "   3. View Hub UI: http://localhost:3001"
echo "   4. View API docs: http://localhost:8080/docs"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Full documentation"
echo "   - QUICKSTART.md - Quick start guide"
echo "   - PROJECT_SUMMARY.md - Project overview"
echo ""

