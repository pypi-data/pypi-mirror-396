import time
from typing import Dict
from .api import LeetCodeAPI
from rich.console import Console

console = Console()


def execute_code(api: LeetCodeAPI, slug: str, lang: str, code: str, sample_input: str, expected: str) -> Dict:
    """
    Execute user code on LeetCode using the REAL interpreter endpoint.
    Works for Python, C++, Java, JavaScript, Go, etc.
    Handles rate limits (HTTP 429) and retries with backoff.
    Returns output, expected, status, errors, runtime info.
    """
    lang_map = {
        "python3": "python3",
        "cpp": "cpp",
        "java": "java",
        "javascript": "javascript",
        "js": "javascript",
        "go": "golang",
    }
    lc_lang = lang_map.get(lang.lower())
    if not lc_lang:
        return {"error": f"Unsupported language: {lang}"}

    # ---------------- Handle cookies explicitly ----------------
    csrf = None
    session_cookie = None
    for c in api.session.cookies:
        if c.name == "csrftoken":
            csrf = c.value
        elif c.name == "LEETCODE_SESSION":
            session_cookie = c.value

    if not csrf or not session_cookie:
        return {"error": "Not logged in. Missing csrftoken or LEETCODE_SESSION."}

    url = f"https://leetcode.com/problems/{slug}/interpret_solution/"
    payload = {
        "lang": lc_lang,
        "question_id": api.slug_to_id(slug),
        "typed_code": code,
        "data_input": (sample_input,
                        expected)
    }

    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "content-type": "application/json",
        "origin": "https://leetcode.com",
        "referer": f"https://leetcode.com/problems/{slug}/",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "x-csrftoken": csrf,
        "x-requested-with": "XMLHttpRequest",
    }

    # ---------------- Send request with retry for 429 ----------------
    for attempt in range(5):
        r = api.session.post(url, json=payload, headers=headers)
        if r.status_code == 429:
            wait = 1.5 * (attempt + 1)
            console.print(f"[yellow]Rate limited (429). Retrying in {wait:.1f}s...[/yellow]")
            time.sleep(wait)
            continue
        if r.status_code != 200:
            return {"error": f"HTTP {r.status_code}", "text": r.text[:500]}
        break
    else:
        return {"error": "Too many 429 responses from LeetCode."}

    res = r.json()
    console.print("[blue]Interpret response:[/blue]", res)  # <-- Print full response

    interpret_id = res.get("interpret_id")
    if not interpret_id:
        return {"error": "No interpret_id returned.", "response": res}

    # ---------------- Poll for result ----------------
    check_url = f"https://leetcode.com/submissions/detail/{interpret_id}/check/"
    poll_attempts = 0
    while True:
        time.sleep(0.8)  # slower polling to reduce 429
        poll_attempts += 1
        rr = api.session.get(check_url, headers=headers)
        if rr.status_code == 429:
            wait = 1.5 * poll_attempts
            console.print(f"[yellow]Polling rate limited (429). Waiting {wait:.1f}s...[/yellow]")
            time.sleep(wait)
            continue
        if rr.status_code != 200:
            return {"error": f"Polling HTTP {rr.status_code}"}

        data = rr.json()
        console.print("[green]Polling response:[/green]", data)  # <-- Print full polling response

        state = data.get("state")
        if state in ("PENDING", "STARTED", None):
            continue

        # ---------------- Done ----------------
        # Some languages use 'interpret_output', some use 'code_output'
        user_output = (
            (data.get("interpret_output") or "")
            or (data.get("code_output") or "")
            or (data.get("stdout") or "")
        )

        return {
            "output": user_output.strip(),
            "expected": data.get("expected_output", "").strip(),
            "status": data.get("status_msg", ""),
            "runtime": data.get("status_runtime", ""),
            "memory": data.get("status_memory", ""),
            "compile_error": data.get("compile_error", ""),
            "runtime_error": data.get("runtime_error", ""),
        }
