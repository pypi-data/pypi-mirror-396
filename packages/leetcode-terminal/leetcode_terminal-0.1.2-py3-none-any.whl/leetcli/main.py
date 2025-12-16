# main.py
import re
import sys
import typer
from typing import Optional
from leet.auth import LeetAuth
from leet.api import LeetCodeAPI
from leet.problems import LeetProblems
from leet.runner import execute_code
from leet.submit import submit_code
from rich.table import Table
from rich.console import Console
import os
from rich.panel import Panel
from rich.text import Text

app = typer.Typer()
auth = LeetAuth()
console = Console()

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        print_welcome()

def require_session():
    session = auth.get_session()
    if not session:
        raise typer.Exit(code=1)
    return session

@app.command()
def login():
    """Login by pasting LEETCODE_SESSION cookie from browser."""
    auth.login()

@app.command()
def logout():
    """Logout and remove stored session."""
    auth.logout()

@app.command()
def list(limit: int = 50, skip: int = 0):
    """List problems (page)."""
    session = require_session()
    api = LeetCodeAPI(session)
    problems = LeetProblems(api)
    problems.list(limit=limit, skip=skip)

@app.command()
def search(q: str):
    """Search problems by keyword (title substring) and pick one to view."""
    session = require_session()
    api = LeetCodeAPI(session)
    problems = LeetProblems(api)
    matches = problems.search(q, limit=500)
    if not matches:
        return
    choice = typer.prompt("Enter index to view (0 to cancel)")
    try:
        idx = int(choice)
    except Exception:
        console.print("Invalid selection")
        return
    if idx <= 0 or idx > len(matches):
        console.print("Cancelled.")
        return
    sel = matches[idx-1]
    problems.view(sel["titleSlug"])

@app.command()
def view(slug: str):
    """View full problem by slug (titleSlug)."""
    session = require_session()
    api = LeetCodeAPI(session)
    problems = LeetProblems(api)
    problems.view(slug)

@app.command()
def download(slug: str, lang: Optional[str] = None, out_dir: str = "."):
    """Download starter code for slug."""
    session = require_session()
    api = LeetCodeAPI(session)
    problems = LeetProblems(api)
    path = problems.download_starter(slug, lang=lang, out_dir=out_dir)
    if path:
        console.print("Saved to:", path)


@app.command()
def run(
    slug: str,
    lang: Optional[str] = typer.Option(None, "--lang", "-l"),
    file: Optional[str] = typer.Option(None, "--file", "-f"),
):
    """
    Run your solution using LeetCode's REAL sample testcases
    from the official API endpoint.
    """
    session = require_session()
    api = LeetCodeAPI(session)

    csrf = api.session.cookies.get("csrftoken")
    if not csrf:
        console.print("[red]Missing csrftoken — login first[/red]")
        return

    headers = {
        "X-CSRFToken": csrf,
        "Referer": f"https://leetcode.com/problems/{slug}/",
        "Content-Type": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0 Safari/537.36"
        ),
    }

    # -------- Load official sample testcases via API --------
    sample_url = f"https://leetcode.com/problems/{slug}/interpret_solution/"
    try:
        # The official "sample testcases" endpoint
        q_url = f"https://leetcode.com/graphql"
        query = {
            "query": """
            query getQuestionDetail($titleSlug: String!) {
              question(titleSlug: $titleSlug) {
                sampleTestCase
              }
            }
            """,
            "variables": {"titleSlug": slug},
        }

        r = session.post(q_url, json=query, headers=headers)
        r.raise_for_status()
        question_data = r.json()
        sample_input_raw = question_data["data"]["question"]["sampleTestCase"]

        # LeetCode separates inputs/outputs by newline
        lines = sample_input_raw.strip().split("\n")
        samples = [(lines[i], lines[i+1]) for i in range(0, len(lines), 2)]
        console.print(samples)

    except Exception as e:
        console.print(f"[red]Failed to load sample testcases: {e}[/red]")
        return

    # -------- Read user code --------
    if not file or not os.path.exists(file):
        console.print("[red]Provide a valid --file path[/red]")
        return

    with open(file, "r", encoding="utf-8") as f:
        user_code = f.read()

    # -------- Detect language --------
    if not lang:
        ext = os.path.splitext(file)[1].lower()
        lang = {
            ".py": "python3",
            ".cpp": "cpp",
            ".java": "java",
            ".js": "javascript",
            ".go": "golang",
        }.get(ext, "python3")

    console.print(f"\n[bold green]Running on LeetCode sample testcases...[/bold green]\n")

    # -------- Execute --------
    for i, (inp, expected) in enumerate(samples, start=1):
        console.print(f"[bold]Testcase {i}[/bold]")

        result = execute_code(api, slug, lang, user_code, inp.strip(),expected)

        if not result or "error" in result:
            console.print(f"[red]Error:[/red] {result.get('error')}")
            continue

        user_output = (result.get("output") or "").strip()
        expected = expected.strip() or "N/A"

        ok = (user_output == expected)
        color = "green" if ok else "red"

        console.print(f"[cyan]Input:[/cyan]\n{inp.strip()}")
        console.print(f"[magenta]Expected:[/magenta] {expected}")
        console.print(f"[yellow]Your Output:[/yellow] {user_output or 'N/A'}")
        console.print(f"[bold][{color}]{'PASS' if ok else 'FAIL'}[/{color}][/bold]\n")


@app.command()
def submit(slug: str, file: str, lang: Optional[str] = None):
    """
    Submit solution to LeetCode using old REST API.
    """
    if not os.path.exists(file):
        console.print("[red]File not found:[/red]", file)
        return

    with open(file, "r", encoding="utf-8") as f:
        code = f.read()

    if not lang:
        _, ext = os.path.splitext(file)
        lang_map = {
            ".py": "python3",
            ".cpp": "cpp",
            ".java": "java",
            ".js": "javascript",
            ".go": "go"
        }
        lang = lang_map.get(ext.lower(), "python3")

    # Load session stored by login
    session = require_session()
    api = LeetCodeAPI(session)

    console.print("[yellow]Submitting...[/yellow]")
    submit_code(api, slug, lang, code)





@app.command()
def daily():
    """Show today's daily challenge."""
    session = require_session()
    api = LeetCodeAPI(session)
    problems = LeetProblems(api)
    problems.daily()

@app.command()
def stats(username: Optional[str] = None):
    """Show stats for logged-in user (or given username)."""
    session = require_session()
    api = LeetCodeAPI(session)
    problems = LeetProblems(api)
    problems.stats(username)

@app.command()
@app.command()
def help():
    """Show help table of CLI commands."""
    table = Table(title="LeetCode CLI - Commands", show_lines=True)
    table.add_column("Command", style="cyan", no_wrap=True)
    table.add_column("Syntax / Example", style="green")
    table.add_column("Description", style="yellow")

    rows = [
        ("login", "lc login", "Login by pasting LEETCODE_SESSION cookie"),
        ("logout", "lc logout", "Remove saved session"),
        ("list", "lc list --limit 50 --skip 0", "List problems with optional pagination"),
        ("search", "lc search \"two sum\"", "Search problems by keyword and pick one to view"),
        ("view", "lc view two-sum", "View full problem description by slug"),
        ("download", "lc download two-sum --lang python3", "Download starter code"),
        ("run", "lc run two-sum --file solution.py --lang python3", "Run your solution on LeetCode's official sample testcases"),
        ("submit", "lc submit two-sum solution.py", "Submit solution to LeetCode"),
        ("daily", "lc daily", "Show today's daily challenge"),
        ("stats", "lc stats", "Show stats for logged-in user or given username"),
        ("help", "lc help", "Show this help table"),
    ]

    for c, s, d in rows:
        table.add_row(c, s, d)

    console.print(table)


def print_welcome():
    console = Console()

    # ------------------ ASCII Logo ------------------
    logo_text = r"""
  .--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--. 
/ .. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \
\ \/\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ \/ /
 \/ /`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'\/ / 
 / /\   /$$      /$$         /$$                                               /$$$$$$$$             /$$                          /$$     /$$$$$$ /$$      /$$$$$$   / /\ 
/ /\ \ | $$  /$ | $$        | $$                                              |__  $$__/            | $$                         | $$    /$$__  $| $$     |_  $$_/  / /\ \
\ \/ / | $$ /$$$| $$ /$$$$$$| $$ /$$$$$$$ /$$$$$$ /$$$$$$/$$$$  /$$$$$$          | $$ /$$$$$$       | $$       /$$$$$$  /$$$$$$ /$$$$$$ | $$  \__| $$       | $$    \ \/ /
 \/ /  | $$/$$ $$ $$/$$__  $| $$/$$_____//$$__  $| $$_  $$_  $$/$$__  $$         | $$/$$__  $$      | $$      /$$__  $$/$$__  $|_  $$_/ | $$     | $$       | $$     \/ / 
 / /\  | $$$$_  $$$| $$$$$$$| $| $$     | $$  \ $| $$ \ $$ \ $| $$$$$$$$         | $| $$  \ $$      | $$     | $$$$$$$| $$$$$$$$ | $$   | $$     | $$       | $$     / /\ 
/ /\ \ | $$$/ \  $$| $$_____| $| $$     | $$  | $| $$ | $$ | $| $$_____/         | $| $$  | $$      | $$     | $$_____| $$_____/ | $$ /$| $$    $| $$       | $$    / /\ \
\ \/ / | $$/   \  $|  $$$$$$| $|  $$$$$$|  $$$$$$| $$ | $$ | $|  $$$$$$$         | $|  $$$$$$/      | $$$$$$$|  $$$$$$|  $$$$$$$ |  $$$$|  $$$$$$| $$$$$$$$/$$$$$$  \ \/ /
 \/ /  |__/     \__/\_______|__/\_______/\______/|__/ |__/ |__/\_______/         |__/\______/       |________/\_______/\_______/  \___/  \______/|________|______/   \/ / 
 / /\.--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--./ /\ 
/ /\ \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \/\ \
\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `' /
 `--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--' 
 """

    # ------------------ Description ------------------
    description = "LeetCLI – Solve, practice, and fetch LeetCode challenges directly from your terminal."

    # ------------------ Create colored texts ------------------
    colored_logo = Text(logo_text, style="bold bright_green")
    colored_description = Text(description, style="bold cyan")

    # ------------------ Print in a panel ------------------
    console.print(Panel(colored_logo, subtitle=colored_description, subtitle_align="center", border_style="bright_magenta", expand=False))

if __name__ == "__main__":
    app()
