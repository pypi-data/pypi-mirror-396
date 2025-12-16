# leet/submit.py
import time
import json
from rich.console import Console
from .api import LeetCodeAPI

console = Console()


def submit_code(api: LeetCodeAPI, slug: str, lang: str, code: str, poll_interval: float = 1.0):
    """
    Submit solution using LeetCode old REST API.
    Colorized with rich.console.
    """

    lang_map_rest = {
        "python3": "python3",
        "cpp": "cpp",
        "java": "java",
        "javascript": "javascript",
        "js": "javascript",
        "go": "golang",
    }

    if lang not in lang_map_rest:
        console.print(f"[red]Unsupported language: {lang}[/red]")
        return

    rest_lang = lang_map_rest[lang]

    question_id = api.get_question_id(slug)
    if not question_id:
        console.print("[red]Failed to get question ID[/red]")
        return

    csrf = api.session.cookies.get("csrftoken")
    if not csrf:
        console.print("[red]Missing csrftoken — login first[/red]")
        return

    # ----- Submit -----
    submit_url = f"https://leetcode.com/problems/{slug}/submit/"

    payload = {
        "lang": rest_lang,
        "question_id": question_id,
        "typed_code": code
    }

    headers = {
        "X-CSRFToken": csrf,
        "Referer": f"https://leetcode.com/problems/{slug}/submit/",
        "Content-Type": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0 Safari/537.36"
        ),
    }

    try:
        res = api.session.post(submit_url, data=json.dumps(payload), headers=headers)
    except Exception as e:
        console.print("[red]Submit request failed:[/red]", e)
        return

    if res.status_code not in (200, 201):
        console.print(f"[red]Submit failed HTTP {res.status_code}[/red]")
        console.print(res.text[:300])
        return

    sub_id = res.json().get("submission_id")
    if not sub_id:
        console.print("[red]Missing submission ID[/red]")
        console.print(res.text)
        return

    console.print("[yellow]Submitted. Polling for result...[/yellow]")

    # ----- Poll -----
    check_url = f"https://leetcode.com/submissions/detail/{sub_id}/check/"

    while True:
        time.sleep(poll_interval)
        r = api.session.get(check_url)

        if r.status_code != 200:
            console.print("[red]Polling failed[/red]:", r.status_code)
            console.print(r.text[:300])
            return

        result = r.json()
        state = result.get("state")

        if state in ("PENDING", "STARTED", None):
            continue

        # ------------- Final Result -------------
        status = result.get("status_msg")
        console.print(f"[bold]Status:[/bold] {status}")

        if result.get("status_runtime"):
            console.print(f"Runtime: {result['status_runtime']}")

        if result.get("status_memory"):
            console.print(f"Memory: {result['status_memory']}")

        # Errors
        if result.get("compile_error"):
            console.print("\n[red]Compile Error:[/red]")
            console.print(result["compile_error"])

        if result.get("runtime_error"):
            console.print("\n[red]Runtime Error:[/red]")
            console.print(result["runtime_error"])

        # Failed testcase
        if result.get("last_testcase"):
            console.print("\n[red]Failed Testcase:[/red]")
            console.print(result["last_testcase"])

        # ----- YOUR OUTPUT -----
        user_output = (
            result.get("code_output")
            or result.get("std_output")
            or result.get("code_answer")
        )

        expected_output = (
            result.get("expected_output")
            or result.get("correct_answer")
        )

        if user_output is not None:
            console.print("\n[red]Your Output:[/red]")
            console.print(user_output)

        if expected_output is not None:
            console.print("\n[green]Expected Output:[/green]")
            console.print(expected_output)

        break
