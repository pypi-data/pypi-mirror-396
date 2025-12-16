# leet/auth.py
import json
import os
from rich.console import Console
from rich.prompt import Prompt
import requests

console = Console()

SESSION_FILE = "session.json"


class LeetAuth:
    def __init__(self):
        self.session = requests.Session()
        self.load_session()

        # Set absolutely required browser headers (Chrome)
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0.0.0 Safari/537.36"
            ),
            "Referer": "https://leetcode.com",
            "Origin": "https://leetcode.com",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
        })

    # -----------------------------
    # Load saved session cookie
    # -----------------------------
    def load_session(self):
        if not os.path.exists(SESSION_FILE):
            return

        try:
            with open(SESSION_FILE, "r") as f:
                data = json.load(f)

            cookie = data.get("LEETCODE_SESSION", "")
            csrftoken = data.get("csrftoken", "")

            if cookie:
                self.session.cookies.set("LEETCODE_SESSION", cookie, domain="leetcode.com")
            if csrftoken:
                self.session.cookies.set("csrftoken", csrftoken, domain="leetcode.com")

        except Exception:
            pass

    # -----------------------------
    # Save session cookie
    # -----------------------------
    def save_session(self, cookie, csrftoken):
        with open(SESSION_FILE, "w") as f:
            json.dump({
                "LEETCODE_SESSION": cookie,
                "csrftoken": csrftoken
            }, f, indent=2)

    # -----------------------------
    # Manual login using browser cookie
    # -----------------------------
    def login(self):
        console.print("🔑 [bold yellow]LeetCode Login[/bold yellow] — paste LEETCODE_SESSION cookie")

        cookie = Prompt.ask("LEETCODE_SESSION", password=True)

        # csrftoken required for GraphQL & REST
        csrftoken = "dummycsrf123456789"  # works fine

        # Apply cookies
        self.session.cookies.set("LEETCODE_SESSION", cookie, domain="leetcode.com")
        self.session.cookies.set("csrftoken", csrftoken, domain="leetcode.com")

        # Check login by hitting /api/problems/all/ (works without GraphQL)
        resp = self.session.get("https://leetcode.com/api/problems/all/")

        if resp.status_code == 200:
            console.print("✅ [green]Login successful![/green]")
            self.save_session(cookie, csrftoken)
        else:
            console.print(f"❌ [red]Login failed — Status {resp.status_code}[/red]")

    # -----------------------------
    # Logout
    # -----------------------------
    def logout(self):
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)

        console.print("Logged out.")

    # -----------------------------
    # Return session for use in API
    # -----------------------------
    def get_session(self):
        return self.session
