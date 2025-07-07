#!/bin/bash

# Welcome message
echo "=========================================="
echo "    Gemini AI Chatbot Installer"
echo "=========================================="
echo "Yeh script zaroori packages install karegi aur command set karegi."
echo

# System-specific installation
if [[ -d /data/data/com.termux ]]; then
    # --- TERMUX SECTION ---
    echo "[*] Termux environment detect hua."
    echo "[*] Termux ke liye zaroori packages install kiye jaa rahe hain..."
    
    # Update package lists
    pkg update -y && pkg upgrade -y
    
    # Install build dependencies aur python.
    # python-grpcio aur python-cryptography ko pkg se install karna sabse zaroori hai
    # taaki pip ko inhe compile na karna pade.
    pkg install python git python-grpcio python-cryptography libjpeg-turbo libffi -y
    
    INSTALL_DIR="/data/data/com.termux/files/usr/bin"
else
    # --- STANDARD LINUX SECTION ---
    echo "[*] Standard Linux environment detect hua."
    echo "[*] Zaroori packages install kiye jaa rahe hain..."
    
    # Check for sudo
    if ! command -v sudo &> /dev/null; then
        echo "Error: 'sudo' command nahi mila. Kripya 'sudo' install karein ya script ko root user se chalayein."
        exit 1
    fi
    
    sudo apt update -y && sudo apt upgrade -y
    sudo apt install python3 python3-pip git -y
    INSTALL_DIR="/usr/local/bin"
fi

# Install Python dependencies from requirements.txt
echo
echo "[*] Python libraries (pip) install ki jaa rahi hain..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[Error] Python libraries install nahi ho payi. Kripya 'pip' aur internet connection check karein."
    exit 1
fi

# Make the main script executable
chmod +x gemini_chatbot.py

# Create a symbolic link to make it a global command
# Isse user 'gemini-chatbot' type karke script chala payega
echo "[*] 'gemini-chatbot' command set ki jaa rahi hai..."
SCRIPT_PATH=$(realpath gemini_chatbot.py)

# Use sudo for standard linux
if [[ -d /data/data/com.termux ]]; then
    ln -sf "$SCRIPT_PATH" "$INSTALL_DIR/gemini-chatbot"
else
    sudo ln -sf "$SCRIPT_PATH" "$INSTALL_DIR/gemini-chatbot"
fi

if [ $? -ne 0 ]; then
    echo "[Error] Command banane me fail. Kripya check karein ki aapke paas permissions hain ya nahi."
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
