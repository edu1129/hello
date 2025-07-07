#!/usr/bin/env python3
import os
import google.generativeai as genai
from dotenv import load_dotenv, set_key
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

# Professional look ke liye Rich Console
console = Console()

# Environment file ka naam
ENV_FILE = ".env"

def setup_api_key():
    """API Key ko setup karta hai. Agar .env file me nahi hai, to user se puchta hai."""
    load_dotenv(dotenv_path=ENV_FILE)
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        console.print("[bold yellow]Gemini API Key nahi mili.[/bold yellow]")
        api_key = Prompt.ask("[bold green]Apna Gemini API Key yahan paste karein[/bold green]")
        
        # .env file banakar usme key save karein
        with open(ENV_FILE, "w") as f:
            f.write(f"GEMINI_API_KEY={api_key}\n")
        
        console.print(f"[bold green]API Key ko {ENV_FILE} file me save kar diya gaya hai.[/bold green]\n")
        os.environ["GEMINI_API_KEY"] = api_key
    
    return api_key

def main():
    """Main function jahan se chat shuru hogi."""
    console.print(Markdown("# Gemini AI Chatbot me aapka swagat hai!"))
    
    try:
        api_key = setup_api_key()
        genai.configure(api_key=api_key)
    except Exception as e:
        console.print(f"[bold red]API Key configure karne me error: {e}[/bold red]")
        console.print("[bold yellow]Kripya sahi API key enter karein aur script dobara chalayein.[/bold yellow]")
        return

    # Model select karne ke liye
    console.print("\n[bold cyan]Uplabdh Models:[/bold cyan]")
    console.print("- gemini-pro (chat ke liye recommended)")
    console.print("- gemini-pro-vision (image-based prompts ke liye, is script me text only hai)")
    
    model_name = Prompt.ask(
        "[bold green]Kaun sa model use karna chahte hain?[/bold green]",
        default="gemini-pro"
    )

    try:
        model = genai.GenerativeModel(model_name)
        chat = model.start_chat(history=[])
        console.print(f"[bold green]'{model_name}' model se chat shuru ho gayi hai.[/bold green]")
        console.print("[yellow]Chat se bahar aane ke liye 'exit', 'quit', ya 'bye' type karein.[/yellow]\n")

    except Exception as e:
        console.print(f"[bold red]Model load karne me error: {e}[/bold red]")
        console.print("[bold yellow]Kripya model ka naam sahi dalein (jaise 'gemini-pro').[/bold yellow]")
        return
    
    # Chat loop
    while True:
        user_input = Prompt.ask("[bold cyan]Aap[/bold cyan]")

        if user_input.lower() in ["exit", "quit", "bye"]:
            console.print("[bold yellow]Alvida! Fir milenge.[/bold yellow]")
            break

        if not user_input.strip():
            continue

        try:
            with console.status("[bold green]AI soch raha hai...[/bold green]", spinner="dots"):
                response = chat.send_message(user_input)
            
            # Markdown me response ko render karein
            console.print(Markdown(response.text, style="bold magenta"))

        except Exception as e:
            console.print(f"[bold red]Ek error aa gaya: {e}[/bold red]")
            console.print("[bold yellow]Kripya apni API key ya internet connection check karein.[/bold yellow]")
            break

if __name__ == "__main__":
    main()
