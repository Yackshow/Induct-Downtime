#!/bin/bash
# Copy all system files to production environment
# Run this script to transfer the complete system

echo "📋 Induct Downtime Monitoring System - File Transfer Script"
echo "=========================================================="

# Production directory
PROD_DIR="/home/mackhun/PycharmProjects/Induct-Downtime"

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p "$PROD_DIR"
mkdir -p "$PROD_DIR/src"
mkdir -p "$PROD_DIR/data/raw"
mkdir -p "$PROD_DIR/data/analysis"
mkdir -p "$PROD_DIR/logs"

echo "✅ Directories created"

# Copy main files
echo "📄 Copying main files..."
cp main.py "$PROD_DIR/"
cp config.yaml "$PROD_DIR/"
cp requirements.txt "$PROD_DIR/"
cp README.md "$PROD_DIR/"
cp DEPLOYMENT_INSTRUCTIONS.md "$PROD_DIR/"

echo "✅ Main files copied"

# Copy source code
echo "🐍 Copying source code..."
cp src/__init__.py "$PROD_DIR/src/"
cp src/auth.py "$PROD_DIR/src/"
cp src/mercury_scraper.py "$PROD_DIR/src/"
cp src/downtime_analyzer.py "$PROD_DIR/src/"
cp src/data_storage.py "$PROD_DIR/src/"
cp src/slack_notifier.py "$PROD_DIR/src/"

echo "✅ Source code copied"

# Copy test files
echo "🧪 Copying test files..."
cp test_with_mock_data.py "$PROD_DIR/"
cp test_mock_offline.py "$PROD_DIR/"
cp test_system_offline.py "$PROD_DIR/"

echo "✅ Test files copied"

# Create start scripts
echo "📝 Creating start scripts..."

# Test script
cat > "$PROD_DIR/test_system.sh" << 'EOF'
#!/bin/bash
echo "🧪 Testing Induct Downtime Monitoring System"
cd /home/mackhun/PycharmProjects/Induct-Downtime
python3 main.py --test
EOF

# Start script
cat > "$PROD_DIR/start_monitoring.sh" << 'EOF'
#!/bin/bash
echo "🚀 Starting Induct Downtime Monitoring System"
cd /home/mackhun/PycharmProjects/Induct-Downtime

# Check if shift is active (1:20 AM - 8:30 AM)
current_hour=$(date +%H)
if [ $current_hour -ge 1 ] && [ $current_hour -le 8 ]; then
    echo "✅ Shift is active, starting continuous monitoring..."
    python3 main.py --continuous
else
    echo "ℹ️  Shift is not active (01:20-08:30), running single test cycle..."
    python3 main.py --single
fi
EOF

# Make scripts executable
chmod +x "$PROD_DIR/test_system.sh"
chmod +x "$PROD_DIR/start_monitoring.sh"

echo "✅ Start scripts created"

# Set permissions
echo "🔒 Setting permissions..."
chmod -R 755 "$PROD_DIR"

echo "✅ Permissions set"

# Summary
echo ""
echo "🎉 FILE TRANSFER COMPLETED!"
echo "=========================="
echo "📁 Location: $PROD_DIR"
echo "📋 Next steps:"
echo "   1. cd $PROD_DIR"
echo "   2. pip install -r requirements.txt"
echo "   3. mwinit -o"
echo "   4. ./test_system.sh"
echo "   5. ./start_monitoring.sh"
echo ""
echo "⏰ System ready for 1:20 AM shift start!"