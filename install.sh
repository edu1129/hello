#!/bin/bash

# Welcome message
echo "=========================================="
echo "    Gemini AI Chatbot Installer"
echo "=========================================="
echo "Yeh script zaroori packages install karegi aur command set karegi."
echo

# Check for Termux
if [[ -d /data/data/com.termux ]]; then
    echo "Termux environment detect hua."
    # Termux-specific commands
    pkg update -y && pkg upgrade -y
    pkg install python git -y
    INSTALL_DIR="/data/data/com.termux/files/usr/bin"
else
    echo "Standard Linux environment detect hua."
    # Standard Linux (Debian/Ubuntu) commands
    sudo apt update -y && sudo apt upgrade -y
    sudo apt install python3 python3-pip git -y
    INSTALL_DIR="/usr/local/bin"
fi

# Install Python dependencies
echo
echo "Python libraries install ki jaa rahi hain..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Python libraries install nahi ho payi. Kripya 'pip' check karein."
    exit 1
fi

# Make the main script executable
chmod +x gemini_chatbot.py

# Create a command to run the script
# Isse user 'gemini-chatbot' type karke script chala payega
SCRIPT_PATH=$(pwd)/gemini_chatbot.py
ln -sf "$SCRIPT_PATH" "$INSTALL_DIR/gemini-chatbot"
if [ $? -ne 0 ]; then
    echo "Error: Command banane me fail. Kripya check karein ki aapke paas permissions hain ya nahi."
    exit 1
fi

echo
echo "=========================================="
echo "   Installation Poora Hua! 🎉"
echo "=========================================="
echo "Ab aap naya terminal session shuru karke neeche di gayi command chala sakte hain:"
echo
echo "    gemini-chatbot"
echo
