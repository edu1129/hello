#!/bin/bash

# Welcome message
echo "=========================================="
echo "    Hello - Termux AI Co-pilot Installer"
echo "=========================================="
echo "Yeh script zaroori packages install karegi aur command set karegi."
echo

# System-specific installation
if [[ -d /data/data/com.termux ]]; then
    # --- TERMUX SECTION ---
    echo "[*] Termux environment detect hua."
    echo "[*] Termux ke liye zaroori packages install kiye jaa rahe hain..."
    pkg update -y && pkg upgrade -y
    pkg install python git python-grpcio python-cryptography libjpeg-turbo libffi -y
    INSTALL_DIR="/data/data/com.termux/files/usr/bin"
else
    # --- STANDARD LINUX SECTION ---
    echo "[*] Standard Linux environment detect hua."
    echo "[*] Zaroori packages install kiye jaa rahe hain..."
    if ! command -v sudo &> /dev/null; then
        echo "[Error] 'sudo' command nahi mila. Kripya 'sudo' install karein."
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

# Create a symbolic link to make it a global command.
# YAHAN BADLAAV KIYA GAYA HAI:
echo "[*] 'hello' command set ki jaa rahi hai..."
SCRIPT_PATH=$(realpath gemini_chatbot.py)

if [[ -d /data/data/com.termux ]]; then
    ln -sf "$SCRIPT_PATH" "$INSTALL_DIR/hello"
else
    sudo ln -sf "$SCRIPT_PATH" "$INSTALL_DIR/hello"
fi

if [ $? -ne 0 ]; then
    echo "[Error] Command banane me fail. Kripya check karein ki aapke paas permissions hain."
    exit 1
fi

echo
echo "=========================================="
echo "   Installation Poora Hua! 🎉"
echo "=========================================="
echo "Ab aap naya terminal session shuru karke neeche di gayi command chala sakte hain:"
echo
# YAHAN BHI BADLAAV KIYA GAYA HAI:
echo "    hello"
echo
