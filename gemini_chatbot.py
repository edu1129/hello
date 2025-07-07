#!/usr/bin/env python3
import os
import re
import subprocess
import google.generativeai as genai
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.syntax import Syntax

# ==============================================================================
#  Configuration
# ==============================================================================
ENV_FILE = ".env"
MODEL_NAME = "gemini-2.5-pro" # Sabse naya aur powerful model

# System Prompt jo AI ko guide karta hai
SYSTEM_PROMPT = """
You are "Termux Co-pilot", a highly advanced AI assistant for the Termux environment. Your instructions MUST be followed precisely.

1.  **Command Format:** ANY shell command you provide MUST be wrapped in double plus signs. Example: `++pkg update && pkg upgrade -y++`.
2.  **File Creation Format:** To write a file, you MUST use the `nano` block format. The `++EOF++` marker is MANDATORY.
    ```
    ++nano FILENAME.EXT++
    CODE_CONTENT
    ++EOF++
    ```
3.  **One Step at a Time:** Provide only ONE command or ONE file operation at a time. Wait for the user to execute it before providing the next step.
4.  **Analyze Output:** After a command is run, I will provide you its output. You must analyze this output (stdout/stderr) to decide the next step. If there was an error, help the user fix it. If it was successful, proceed to the next logical step.
5.  **Be an Expert:** Act as a true Termux expert. Use `pkg` for installations. Be concise and clear.
"""

# Console setup for beautiful UI
console = Console()

def setup_api_key():
    """API Key ko setup aur load karta hai."""
    load_dotenv(dotenv_path=ENV_FILE)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        console.print(Panel("[bold yellow]Aapki Gemini API Key nahi mili.[/bold yellow]", title="Setup", border_style="yellow"))
        api_key = Prompt.ask("[green]Apna Gemini API Key yahan paste karein[/green]")
        with open(ENV_FILE, "w") as f:
            f.write(f"GEMINI_API_KEY={api_key}\n")
        console.print(Panel("[bold green]API Key save ho gayi hai. Ab aap chat kar sakte hain.[/bold green]", title="Success", border_style="green"))
        os.environ["GEMINI_API_KEY"] = api_key
    return api_key

def print_ai_response(text):
    """AI ke response ko ek sundar panel me print karta hai."""
    console.print(Panel(
        Markdown(text),
        title="Termux Co-pilot",
        border_style="magenta",
        padding=(1, 2)
    ))

def execute_action(action_type, content):
    """Ek command ya file operation ko execute karta hai."""
    output_log = ""
    try:
        if action_type == 'file':
            filename, file_content = content
            confirm = Prompt.ask(
                f"[bold yellow]AI file [cyan]'{filename}'[/cyan] banana chahta hai. Ijazat hai? (y/n)[/bold yellow]",
                default="n"
            )
            if confirm.lower() == 'y':
                with open(filename, 'w') as f:
                    f.write(file_content)
                success_msg = f"✅ File '{filename}' safaltapoorvak ban gayi."
                console.print(f"[green]{success_msg}[/green]")
                output_log = success_msg
            else:
                output_log = f"User ne file '{filename}' banane se mana kar diya."
                console.print(f"[yellow]{output_log}[/yellow]")

        elif action_type == 'command':
            command = content
            console.print(Panel(Syntax(command, "bash"), title="Command to Execute", border_style="cyan"))
            confirm = Prompt.ask(
                "[bold yellow]Upar diye gaye command ko run karne ki ijazat hai? (y/n)[/bold yellow]",
                default="n"
            )
            if confirm.lower() == 'y':
                console.print(f"▶️ Executing: [cyan]{command}[/cyan]")
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                if result.stdout:
                    console.print(Panel(result.stdout.strip(), title="Output (stdout)", border_style="green"))
                if result.stderr:
                    console.print(Panel(result.stderr.strip(), title="Error (stderr)", border_style="red"))
                output_log = f"Command: {command}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            else:
                output_log = f"User ne command '{command}' run karne se mana kar diya."
                console.print(f"[yellow]{output_log}[/yellow]")

    except Exception as e:
        output_log = f"Action execute karte waqt error aaya: {e}"
        console.print(f"[bold red]{output_log}[/bold red]")
    
    return output_log

def parse_and_run(response_text):
    """AI ke response ko parse karke step-by-step actions run karta hai."""
    
    # Regex to find command or file blocks
    command_pattern = r'\+\+(.*?)\+\+'
    file_pattern = r'\+\+nano\s+([\w\.\-\/]+)\+\+\n(.*?)\n\+\+EOF\+\+'
    
    # Split text by action blocks to process it sequentially
    parts = re.split(f"({file_pattern}|{command_pattern})", response_text, flags=re.DOTALL)
    
    last_action_output = ""

    for part in parts:
        if not part or part.isspace():
            continue

        file_match = re.match(file_pattern, part, re.DOTALL)
        command_match = re.match(command_pattern, part, re.DOTALL)

        if file_match:
            filename = file_match.group(1).strip()
            content = file_match.group(2).strip()
            last_action_output = execute_action('file', (filename, content))
        elif command_match and "nano" not in command_match.group(1) and "EOF" not in command_match.group(1):
            command = command_match.group(1).strip()
            last_action_output = execute_action('command', command)
        else:
            # This is plain text from the AI
            print_ai_response(part.strip())
            
    return last_action_output


def main():
    console.print(Panel(
        "[bold green]Termux AI Co-pilot me aapka swagat hai![/bold green]\n"
        "Type 'exit', 'quit', ya 'bye' to end the chat.",
        title="Welcome",
        border_style="green"
    ))
    
    try:
        api_key = setup_api_key()
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_PROMPT)
        chat = model.start_chat(history=[])
    except Exception as e:
        console.print(f"[bold red]Initialization Error: {e}[/bold red]")
        return

    first_user_prompt = None
    last_action_output = ""

    while True:
        user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")

        if user_input.lower() in ["exit", "quit", "bye"]:
            console.print("[bold yellow]Alvida! Fir milenge.[/bold yellow]")
            break
        
        if not user_input.strip():
            continue

        if first_user_prompt is None:
            first_user_prompt = user_input

        # AI ke liye context taiyar karna
        contextual_prompt = f"""
        [Main Goal (First thing user said): "{first_user_prompt}"]
        
        [Output/Result of my last instruction:
        {last_action_output if last_action_output else "Nothing has been executed yet."}]
        
        [User's new message: "{user_input}"]
        
        Based on all this, provide the very next single step.
        """

        try:
            with console.status("[bold green]Co-pilot soch raha hai...[/bold green]", spinner="dots"):
                response = chat.send_message(contextual_prompt)
            
            # AI ke response ko parse karo aur actions execute karo
            last_action_output = parse_and_run(response.text)

        except Exception as e:
            console.print(f"[bold red]An error occurred: {e}[/bold red]")
            break

if __name__ == "__main__":
    main()
