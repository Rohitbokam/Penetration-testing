#!/bin/bash

# ThreatLens Installation Script
# Automated setup for the penetration testing platform

set -e  # Exit on error

echo "======================================"
echo "  ThreatLens Installation Script"
echo "======================================"
echo ""
echo "⚠️  WARNING: This tool is for authorized security testing only!"
echo "   Only use on systems you have permission to test."
echo ""
read -p "Do you agree to use this tool responsibly? (yes/no): " agreement

if [ "$agreement" != "yes" ]; then
    echo "Installation cancelled."
    exit 1
fi

echo ""
echo "Starting installation..."
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "⚠️  Warning: This script is designed for Linux systems."
    echo "   Installation may not work correctly on other operating systems."
    read -p "Continue anyway? (yes/no): " continue_install
    if [ "$continue_install" != "yes" ]; then
        exit 1
    fi
fi

# Check if running with sudo
if [ "$EUID" -eq 0 ]; then 
    echo "⚠️  Please do not run this script as root/sudo"
    echo "   The script will ask for sudo when needed"
    exit 1
fi

# Update package lists
echo "📦 Updating package lists..."
sudo apt-get update -qq

# Install system tools
echo "🔧 Installing system tools..."

# Install Nmap
if ! command -v nmap &> /dev/null; then
    echo "  Installing Nmap..."
    sudo apt-get install -y nmap > /dev/null 2>&1
    echo "  ✅ Nmap installed"
else
    echo "  ✅ Nmap already installed"
fi

# Install Nikto
if ! command -v nikto &> /dev/null; then
    echo "  Installing Nikto..."
    sudo apt-get install -y nikto > /dev/null 2>&1
    echo "  ✅ Nikto installed"
else
    echo "  ✅ Nikto already installed"
fi

# Install Python and pip
echo "🐍 Setting up Python environment..."
if ! command -v python3 &> /dev/null; then
    echo "  Installing Python 3..."
    sudo apt-get install -y python3 python3-pip python3-venv > /dev/null 2>&1
    echo "  ✅ Python 3 installed"
else
    echo "  ✅ Python 3 already installed"
fi

# Create backend virtual environment
echo "📦 Setting up Python backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
    echo "  ✅ Virtual environment created"
else
    echo "  ✅ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "  Installing Python dependencies..."
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "  ✅ Python dependencies installed"

cd ..

# Create start scripts
echo "📝 Creating start scripts..."

# Backend start script
cat > start-backend.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting ThreatLens Backend Server..."
cd backend
source venv/bin/activate
python app.py
EOF

chmod +x start-backend.sh
echo "  ✅ Created start-backend.sh"

# Frontend start script
cat > start-frontend.sh << 'EOF'
#!/bin/bash
echo "🌐 Starting ThreatLens Frontend Server..."
echo "📡 Frontend will be available at: http://localhost:8080/tool.html"
python3 -m http.server 8080
EOF

chmod +x start-frontend.sh
echo "  ✅ Created start-frontend.sh"

# Create combined start script
cat > start-all.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting ThreatLens Platform..."
echo ""
echo "Starting backend server..."
./start-backend.sh &
BACKEND_PID=$!

sleep 3

echo ""
echo "Starting frontend server..."
./start-frontend.sh &
FRONTEND_PID=$!

echo ""
echo "======================================"
echo "  ThreatLens is now running!"
echo "======================================"
echo ""
echo "Backend:  http://localhost:5000"
echo "Frontend: http://localhost:8080/tool.html"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF

chmod +x start-all.sh
echo "  ✅ Created start-all.sh"

# Create stop script
cat > stop-all.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping ThreatLens servers..."
pkill -f "python app.py"
pkill -f "python3 -m http.server 8080"
echo "✅ All servers stopped"
EOF

chmod +x stop-all.sh
echo "  ✅ Created stop-all.sh"

# Installation complete
echo ""
echo "======================================"
echo "  ✅ Installation Complete!"
echo "======================================"
echo ""
echo "🚀 Quick Start:"
echo ""
echo "  Option 1 - Start both servers:"
echo "    ./start-all.sh"
echo ""
echo "  Option 2 - Start servers separately:"
echo "    Terminal 1: ./start-backend.sh"
echo "    Terminal 2: ./start-frontend.sh"
echo ""
echo "  Then open: http://localhost:8080/tool.html"
echo ""
echo "  To stop: ./stop-all.sh"
echo ""
echo "📖 For more information, see README.md"
echo ""
echo "⚠️  Remember: Only test systems you have permission to scan!"
echo ""
