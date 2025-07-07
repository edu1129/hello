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
from rich.spinner import Spinner

# ==============================================================================
#  Configuration & Safety Switch
# ==============================================================================
# ⚠️ WARNING: Set this to True ONLY if you understand and accept the risk of
# running AI-generated commands automatically without confirmation.
AUTO_EXECUTE_ACTIONS = False

ENV_FILE = ".env"
MODEL_NAME = "gemini-2.5-pro"

# Enhanced System Prompt for a more versatile AI
SYSTEM_PROMPT = """
You are "Nexus", a universal command-line and DevOps AI assistant. Your primary function is to help users with tasks on any shell environment, including Termux, Ubuntu, etc.

**Your Core Instructions:**
1.  **Command Syntax:** ALL executable shell commands MUST be wrapped in double plus signs. Example: `++pip install requests -U++`.
2.  **File Syntax:** To create or edit a file, you MUST use the `nano` block format. The `++EOF++` marker is mandatory.
    ```
    ++nano path/to/your/file.txt++
    File content goes here.
    Line by line.
    ++EOF++
    ```
3.  **Tool Awareness:** Be smart about the environment. If the user mentions Termux, prefer `pkg`. If they mention Ubuntu/Debian, use `apt`. If you're not sure, you can use a command like `++command -v apt || command -v pkg++` to check for an available package manager.
4.  **Sequential Logic:** Provide a logical sequence of commands. You can provide multiple commands in one response. I will execute them in order.
5.  **Analyze & Adapt:** I will feed you the full output (STDOUT and STDERR) of your last set of commands. Analyze this output to determine if the commands were successful and decide the next logical step. If an error occurred, your next step should be to help fix that error.
"""

console = Console()

def setup_api_key():
    """Sets up and loads the API Key with a better UI."""
    load_dotenv(dotenv_path=ENV_FILE)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        console.print(Panel("[bold yellow]Aapki Gemini API Key nahi mili.[/bold yellow]", title="[bold red]Setup Required[/bold red]", border_style="yellow"))
        api_key = Prompt.ask("[green]Apna Gemini API Key yahan paste karein[/green]")
        with open(ENV_FILE, "w") as f:
            f.write(f"GEMINI_API_KEY={api_key}\n")
        console.print(Panel("[bold green]API Key safaltapoorvak save ho gayi hai.[/bold green]", title="[bold green]Success[/bold green]", border_style="green"))
        os.environ["GEMINI_API_KEY"] = api_key
    return api_key

def parse_response_for_actions(response_text):
    """Parses AI response to find all text, commands, and file operations in order."""
    # This regex finds nano blocks OR any command wrapped in ++...++
    pattern = re.compile(
        r'(\+\+nano\s+(?P<filename>[\w\.\-\/]+)\+\+\n(?P<content>.*?)\n\+\+EOF\+\+)|'
        r'(\+\+(?P<command>.*?)\+\+)',
        re.DOTALL
    )
    actions = []
    last_end = 0
    for match in pattern.finditer(response_text):
        start, end = match.span()
        # Add any text between the last action and this one
        if start > last_end:
            actions.append({'type': 'text', 'content': response_text[last_end:start].strip()})

        # Check if it's a file creation block
        if match.group('filename'):
            actions.append({
                'type': 'file',
                'filename': match.group('filename').strip(),
                'content': match.group('content').strip()
            })
        # Check if it's a command, but filter out parts of the file block syntax
        elif match.group('command'):
            command_text = match.group('command').strip()
            # This check prevents parts of the 'nano' block from being treated as commands
            if not command_text.startswith('nano ') and command_text != 'EOF':
                actions.append({'type': 'command', 'command': command_text})
        
        last_end = end

    # Add any remaining text after the last action
    if last_end < len(response_text):
        actions.append({'type': 'text', 'content': response_text[last_end:].strip()})
        
    # Filter out empty actions
    return [action for action in actions if action.get('content') or action.get('command')]

def execute_actions(actions):
    """Displays and robustly executes a list of actions."""
    execution_plan = [a for a in actions if a['type'] in ('command', 'file')]
    combined_output_log = ""
    if not execution_plan:
        for action in actions:
            if action['type'] == 'text':
                console.print(Panel(Markdown(action['content']), title="Nexus AI", border_style="magenta", expand=False))
        return ""

    console.print(Panel("[bold yellow]Nexus AI in kaamo ko anjaam dena chahta hai:",_renderable=...))
    for i, action in enumerate(execution_plan):
        if action['type'] == 'file':
            console.print(f"  {i+1}. 📝 [cyan]File Banayein:[/cyan] {action['filename']}")
        elif action['type'] == 'command':
            console.print(f"  {i+1}. 🚀 [cyan]Command Chalayein:[/cyan] `{action['command']}`")

    confirmed = AUTO_EXECUTE_ACTIONS or Prompt.ask("\n[bold red]Kya aap in sabhi kaamo ko anjaam dene ki ijazat dete hain? (y/n)[/bold red]", default="n").lower() == 'y'
    
    if confirmed:
        if AUTO_EXECUTE_ACTIONS:
            console.print("\n[bold orange_red1]AUTO-EXECUTION MODE: Bina pooche commands run kiye jaa rahe hain...[/bold orange_red1]")
        console.print("\n--- [bold green]Execution Shuru[/bold green] ---")
        for action in execution_plan:
            log_entry = ""
            try:
                if action['type'] == 'file':
                    filename, content = action['filename'], action['content']
                    console.print(f"\n📝 Writing file: [cyan]{filename}[/cyan]")
                    with open(filename, 'w') as f: f.write(content)
                    log_entry = f"✅ File '{filename}' successfully created."
                    console.print(f"[green]{log_entry}[/green]")
                
                elif action['type'] == 'command':
                    command = action['command']
                    console.print(f"\n🚀 Executing: [cyan]'{command}'[/cyan]")
                    with console.status("[bold yellow]Running command...[/bold yellow]", spinner="dots") as status:
                        # The most robust way to run any shell command
                        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)
                    
                    if result.stdout:
                        console.print(Panel(Syntax(result.stdout.strip(), "bash"), title="Output (stdout)", border_style="green", expand=False))
                    if result.stderr:
                        console.print(Panel(Syntax(result.stderr.strip(), "bash"), title="Error (stderr)", border_style="red", expand=False))
                    
                    log_entry = f"Command: `{command}`\nExit Code: {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\n"
            
            except Exception as e:
                log_entry = f"❌ Python script error during action: {e}"
                console.print(f"[bold red]{log_entry}[/bold red]")
            
            combined_output_log += log_entry
        console.print("--- [bold green]Execution Poora Hua[/bold green] ---\n")
    else:
        combined_output_log = "User ne execution se mana kar diya."
        console.print(f"[yellow]{combined_output_log}[/yellow]")
    return combined_output_log

def main():
    console.print(Panel(
        "[bold green]Nexus AI Co-pilot me aapka swagat hai![/bold green]\n"
        "Aapka universal command-line assistant. Type 'exit' to quit.",
        title="[bold]Welcome[/bold]",
        border_style="green"
    ))
    try:
        api_key = setup_api_key()
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_PROMPT)
        chat = model.start_chat(history=[])
    except Exception as e:
        console.print(Panel(f"Initialization Error: {e}", title="[bold red]Critical Error[/bold red]", border_style="red"))
        return

    last_execution_summary = ""
    while True:
        user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
        if user_input.lower() in ["exit", "quit", "bye"]: break
        if not user_input.strip(): continue
        
        contextual_prompt = f"""
        [Summary of Last Execution's Result:
        {last_execution_summary if last_execution_summary else "No commands have been executed yet."}]
        
        [User's New Instruction: "{user_input}"]
        
        Based on the previous results and the new instruction, provide the next logical step(s).
        """
        try:
            with console.status("[bold green]Nexus AI soch raha hai...[/bold green]", spinner="dots"):
                response = chat.send_message(contextual_prompt)
            
            actions = parse_response_for_actions(response.text)
            last_execution_summary = execute_actions(actions)
        except Exception as e:
            console.print(Panel(f"An API or other critical error occurred: {e}", title="[bold red]Runtime Error[/bold red]", border_style="red"))
            break
            
    console.print("[bold yellow]Alvida! Fir milenge.[/bold yellow]")

if __name__ == "__main__":
    main()
