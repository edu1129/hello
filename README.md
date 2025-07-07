# Nexus AI Co-pilot 🚀

Welcome to **Nexus AI Co-pilot**, a powerful, universal command-line assistant powered by Google's Gemini Pro. This isn't just a chatbot; it's an interactive co-pilot designed to help you with DevOps tasks, coding, file management, and general system administration directly from your terminal.

It's built to be environment-aware, providing tailored commands for environments like **Termux**, **Ubuntu**, **Debian**, and other Linux distributions.

## ✨ Advanced Features

-   **🤖 Intelligent Co-pilot:** More than a chatbot, Nexus can understand your goals, suggest commands, and execute them for you.
-   **⚡ Command Execution:** Nexus can run shell commands. It wraps commands in `++command++` which you can then approve for execution.
-   **📝 File Manipulation:** Create and edit files directly from the chat interface using a simple `++nano path/to/file.txt++` syntax.
-   **🧠 Context-Aware:** Nexus remembers the output of previous commands. If a command fails, it will analyze the error and suggest a fix in its next response.
-   **🛡️ Safety First:** By default, Nexus will ask for your confirmation before running any command or writing any file. An auto-execute mode is available for advanced users.
-   **🎨 Rich Interface:** A beautiful and user-friendly interface powered by the `rich` library, with syntax highlighting and clear panels.
-   **🔑 Secure API Key:** Your Google Gemini API key is stored locally and securely in a `.env` file.
-   **🔧 Easy Installation:** A simple `install.sh` script handles all dependencies and setup for you.

## 📋 Prerequisites

Before you begin, you need to get a **Google Gemini API Key**.
1.  Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Click on "**Create API key**".
3.  Copy the generated key. You will need to paste it during the first run of the script.

## ⚙️ Installation

Open your Termux or Linux terminal and run the following commands:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/edu1129/hello.git
    ```

2.  **Navigate into the directory:**
    ```bash
    cd hello
    ```

3.  **Run the installation script:**
    ```bash
    bash install.sh
    ```
    The script will install all necessary packages and set up the `hello` command.

## 🚀 How to Use

After the installation is complete, open a **new terminal session** and simply run:

```bash
hello
```

The first time you run it, the script will ask for your Gemini API Key. Paste your key and press Enter. It will be saved for future sessions.

### Example Interaction

Here's how you can interact with Nexus:

**You:**
> `update my system and then install neofetch`

**Nexus AI:**
> ```
> Okay, I will first update your system's package lists and then install neofetch.
> 
> ++sudo apt update && sudo apt upgrade -y++
> ++sudo apt install neofetch -y++
> ```

You will then be prompted to confirm the execution of these commands.

## ⚠️ Disclaimer

This tool gives an AI the ability to execute commands on your system. While there is a confirmation prompt for safety, be extremely cautious. **Always review the commands** suggested by the AI before granting permission to execute them. The author is not responsible for any damage caused by the execution of AI-generated commands. Use at your own risk.
