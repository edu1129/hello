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
#  Configuration & Safety Switch
# ==============================================================================
# ⚠️ WARNING: Set this to True ONLY if you understand the risk.
# It will execute all commands from the AI without asking for permission.
AUTO_EXECUTE_ACTIONS = False

ENV_FILE = ".env"
MODEL_NAME = "gemini-1.5-pro-latest" # Using the latest powerful model

# System Prompt to guide the AI Co-pilot
SYSTEM_PROMPT = """
You are "Termux Co-pilot", a super-intelligent AI assistant for the Termux environment. Your instructions MUST be followed precisely.

1.  **Command Format:** ANY shell command you provide MUST be wrapped in double plus signs. Example: `++pkg update -y++`.
2.  **File Creation Format:** To write a file, you MUST use the `nano` block format. The `++EOF++` marker is MANDATORY.
    ```
    ++nano FILENAME.EXT++
    CODE_CONTENT
    ++EOF++
    ```
3.  **Multiple Steps:** You can provide multiple commands and file operations in a single response. I will execute them sequentially.
4.  **Analyze Output:** After a series of commands are run, I will provide you their combined output. You must analyze this output (stdout/stderr) to decide the next steps. If there was an error, help the user fix it.
5.  **Be an Expert:** Act as a true Termux expert. Use `pkg` for installations. Be concise, clear, and efficient.
"""

console = Console()

def setup_api_key():
    """Sets up and loads the API Key."""
    load_dotenv(dotenv_path=ENV_FILE)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        console.print(Panel("[bold yellow]Aapki Gemini API Key nahi mili.[/bold yellow]", title="Setup", border_style="yellow"))
        api_key = Prompt.ask("[green]Apna Gemini API Key yahan paste karein[/green]")
        with open(ENV_FILE, "w") as f:
            f.write(f"GEMINI_API_KEY={api_key}\n")
        console.print(Panel("[bold green]API Key save ho gayi hai.[/bold green]", title="Success", border_style="green"))
        os.environ["GEMINI_API_KEY"] = api_key
    return api_key

def parse_response_for_actions(response_text):
    """Parses AI response to find all text, commands, and file operations in order."""
    
    # Combined pattern to find all action blocks
    pattern = re.compile(
        r'(\+\+nano\s+(?P<filename>[\w\.\-\/]+)\+\+\n(?P<content>.*?)\n\+\+EOF\+\+)|(\+\+(?P<command>.*?)\+\+)',
        re.DOTALL
    )
    
    actions = []
    last_end = 0
    
    for match in pattern.finditer(response_text):
        # Add the text before this match
        start, end = match.span()
        if start > last_end:
            actions.append({'type': 'text', 'content': response_text[last_end:start].strip()})
        
        # Add the matched action
        if match.group('filename'): # It's a file operation
            actions.append({
                'type': 'file',
                'filename': match.group('filename').strip(),
                'content': match.group('content').strip()
            })
        elif match.group('command'): # It's a command
             # Ensure it's not part of a nano block
            if "nano " not in match.group('command') and "EOF" not in match.group('command'):
                actions.append({'type': 'command', 'command': match.group('command').strip()})

        last_end = end
        
    # Add any remaining text after the last match
    if last_end < len(response_text):
        actions.append({'type': 'text', 'content': response_text[last_end:].strip()})
        
    return [action for action in actions if action.get('content') or action.get('command')]

def execute_actions(actions):
    """Displays and executes a list of actions (commands/files)."""
    
    execution_plan = [a for a in actions if a['type'] in ('command', 'file')]
    combined_output_log = ""

    if not execution_plan:
        for action in actions:
            if action['type'] == 'text':
                console.print(Panel(Markdown(action['content']), title="Termux Co-pilot", border_style="magenta"))
        return ""

    # Display plan
    console.print(Panel("[bold yellow]Co-pilot in kaamo ko anjaam dena chahta hai:[/bold yellow]", title="Execution Plan", border_style="yellow"))
    for i, action in enumerate(execution_plan):
        if action['type'] == 'file':
            console.print(f"{i+1}. 📝 [cyan]File Banayein:[/cyan] {action['filename']}")
        elif action['type'] == 'command':
            console.print(f"{i+1}. 🚀 [cyan]Command Chalayein:[/cyan] {action['command']}")

    # Confirmation
    confirmed = False
    if AUTO_EXECUTE_ACTIONS:
        console.print("\n[bold orange_red1]AUTO-EXECUTION MODE: Bina pooche commands run kiye jaa rahe hain...[/bold orange_red1]")
        confirmed = True
    else:
        confirm_prompt = Prompt.ask("\n[bold red]Kya aap in sabhi kaamo ko anjaam dene ki ijazat dete hain? (y/n)[/bold red]", default="n")
        if confirm_prompt.lower() == 'y':
            confirmed = True

    # Execution
    if confirmed:
        console.print("\n--- [bold green]Execution Shuru[/bold green] ---")
        for action in execution_plan:
            try:
                if action['type'] == 'file':
                    console.print(f"\n📝 Creating file: [cyan]{action['filename']}[/cyan]")
                    with open(action['filename'], 'w') as f:
                        f.write(action['content'])
                    log_msg = f"✅ File '{action['filename']}' safaltapoorvak ban gayi."
                    console.print(f"[green]{log_msg}[/green]")
                    combined_output_log += log_msg + "\n"

                elif action['type'] == 'command':
                    command = action['command']
                    console.print(f"\n🚀 Executing command: [cyan]{command}[/cyan]")
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    
                    if result.stdout:
                        console.print(Panel(result.stdout.strip(), title="Output (stdout)", border_style="green", expand=False))
                    if result.stderr:
                        console.print(Panel(result.stderr.strip(), title="Error (stderr)", border_style="red", expand=False))
                    
                    log_entry = f"Command: `{command}`\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\n"
                    combined_output_log += log_entry

            except Exception as e:
                log_msg = f"❌ Action fail ho gaya: {e}"
                console.print(f"[bold red]{log_msg}[/bold red]")
                combined_output_log += log_msg + "\n"
        console.print("--- [bold green]Execution Poora Hua[/bold green] ---\n")
    else:
        log_msg = "User ne execution se mana kar diya."
        console.print(f"[yellow]{log_msg}[/yellow]")
        combined_output_log = log_msg

    return combined_output_log

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
    last_execution_summary = ""

    while True:
        user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
        if user_input.lower() in ["exit", "quit", "bye"]: break
        if not user_input.strip(): continue

        if first_user_prompt is None: first_user_prompt = user_input

        contextual_prompt = f"""
        [Main Goal (First Request): "{first_user_prompt}"]
        
        [Summary of Last Execution:
        {last_execution_summary if last_execution_summary else "Nothing has been executed yet."}]
        
        [User's New Instruction: "{user_input}"]
        
        Based on all this, provide the next set of commands or file operations needed.
        """

        try:
            with console.status("[bold green]Co-pilot soch raha hai...[/bold green]", spinner="dots"):
                response = chat.send_message(contextual_prompt)
            
            actions = parse_response_for_actions(response.text)
            
            # Print initial text from AI before showing execution plan
            for action in actions:
                if action['type'] == 'text':
                    console.print(Panel(Markdown(action['content']), title="Termux Co-pilot", border_style="magenta"))

            # Execute commands and files
            last_execution_summary = execute_actions(actions)

        except Exception as e:
            console.print(f"[bold red]An error occurred: {e}[/bold red]")
            break
            
    console.print("[bold yellow]Alvida! Fir milenge.[/bold yellow]")

if __name__ == "__main__":
    main()
