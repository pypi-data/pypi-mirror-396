# leet/problems.py
import json
import os
from rich.console import Console
from rich.table import Table
from typing import List, Dict, Optional
from .api import LeetCodeAPI
from datetime import datetime, timedelta
from rich import box
from rich.style import Style
console = Console()
try:
    import html2text
except Exception:
    html2text = None

class LeetProblems:
    def __init__(self, api: LeetCodeAPI):
        self.api = api    

        
    # inside LeetProblems class (leet/problems.py)
    def get_question_data(self, title_slug: str) -> Dict:
      """
      Fetch minimal problem data (no printing): returns dict with
      'title', 'titleSlug', 'sampleTestCase', 'exampleTestcases', 'codeSnippets'
      """
      query = """
      query questionMinimal($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
          title
          titleSlug
          sampleTestCase
          exampleTestcases
          codeSnippets {
            lang
            code
          }
        }
      }
      """
      try:
          data = self.api.graphql(query, {"titleSlug": title_slug})
          q = data.get("question", {}) or {}
          return q
      except Exception as e:
          # bubble up error structure similar to other callers
          raise RuntimeError(f"Failed to fetch problem data for '{title_slug}': {e}")


    def get_logged_in_username(self) -> Optional[str]:
        """
        Works 100% — uses real browser headers + LEETCODE_SESSION + csrftoken
        to fetch logged-in user identity.
        """
        try:
            url = "https://leetcode.com/graphql/"

            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0 Safari/537.36"
                ),
                "Referer": "https://leetcode.com/problemset/all/",
                "Origin": "https://leetcode.com",
                "Accept": "*/*",
                "Content-Type": "application/json",
            }

            # Attach csrf token (LeetCode blocks if missing)
            csrf = self.api.session.cookies.get("csrftoken")
            if csrf:
                headers["X-CSRFToken"] = csrf

            query = {
                "query": """
                query {
                  userStatus {
                    username
                    isSignedIn
                  }
                }
                """
            }

            resp = self.api.session.post(url, json=query, headers=headers)

            # If blocked, print debug
            if resp.status_code != 200:
                print("DEBUG username status =", resp.status_code, resp.text[:200])
                return None

            data = resp.json()
            user = data.get("data", {}).get("userStatus", {})

            if user.get("isSignedIn"):
                return user.get("username")

            return None

        except Exception as e:
            print("DEBUG username error:", e)
            return None



    def list(self, limit: int = 50, skip: int = 0, silent: bool = False) -> List[Dict]:
        query = """
        query problemsetQuestionListV2($limit: Int!, $skip: Int!) {
          problemsetQuestionListV2(
            categorySlug: ""
            limit: $limit
            skip: $skip
          ) {
            hasMore
            questions {
              questionFrontendId
              title
              titleSlug
              difficulty
              paidOnly
              acRate
            }
          }
        }
        """
        data = self.api.graphql(query, {"limit": limit, "skip": skip})
        node = data.get("problemsetQuestionListV2", {})
        questions = node.get("questions", [])

        if silent:
            return questions

        table = Table(title="LeetCode Problems")
        table.add_column("ID", no_wrap=True)
        table.add_column("Title")
        table.add_column("Difficulty", no_wrap=True)
        table.add_column("AC %", no_wrap=True)
        for q in questions:
            ac = q.get("acRate")
            ac_str = f"{ac:.1f}%" if isinstance(ac, (int, float)) else "-"
            table.add_row(q.get("questionFrontendId",""), q.get("title",""), q.get("difficulty",""), ac_str)
        console.print("\n")
        console.print(table)
        return questions

    def search(self, keyword: str, limit: int = 500) -> List[Dict]:
        keyword = keyword.lower().strip()
        questions = []
        step = 100
        fetched = 0
        while fetched < limit:
            qs = self.list(limit=min(step, limit-fetched), skip=fetched, silent=True)
            if not qs:
                break
            questions.extend(qs)
            fetched += len(qs)
            if len(qs) < step:
                break

        matches = [q for q in questions if keyword in q.get("title","").lower() or keyword in q.get("titleSlug","").lower()]

        if not matches:
            console.print(f"\n[red]No problems found for '{keyword}'[/red]")
            return []

        table = Table(title=f"\nSearch results for '{keyword}'")
        table.add_column("Index", no_wrap=True)
        table.add_column("ID", no_wrap=True)
        table.add_column("Title")
        table.add_column("Slug", no_wrap=True)
        table.add_column("Difficulty", no_wrap=True)
        for i, q in enumerate(matches, 1):
            table.add_row(str(i), q.get("questionFrontendId",""), q.get("title",""), q.get("titleSlug",""), q.get("difficulty",""))
        console.print(table)
        return matches

    def view(self, title_slug: str) -> Dict:
      from rich.console import Console
      from rich.markdown import Markdown
      import html2text

      console = Console()

      # ------------------ Fetch Full Problem Details ------------------
      query_details = """
      query questionDetail($slug: String!) {
        question(titleSlug: $slug) {
          questionFrontendId
          title
          titleSlug
          difficulty
          content
          codeSnippets {
            lang
            langSlug
            code
          }
          sampleTestCase
          exampleTestcases
          topicTags {
            name
          }
        }
      }
      """

      details = self.api.graphql(query_details, {"slug": title_slug})
      problem = details.get("question")

      if not problem:
          console.print("[red]Could not load question details.[/red]")
          return {}

      # ------------------ Headers ------------------
      console.print(f"\n[bold yellow]🔥 Problem ({problem['questionFrontendId']})[/bold yellow]")
      console.print(f"[cyan]{problem['questionFrontendId']} — {problem['title']}[/cyan] — [green]{problem['difficulty']}[/green]")
      console.print(f"🔗 https://leetcode.com/problems/{title_slug}/\n")

      # ------------------ Convert HTML → Markdown ------------------
      html = problem.get("content")
      if not html:
          console.print("[red]Problem description not available (maybe paid-only)[/red]")
          md = "Description not available."
          return 
      else:
          md = html2text.html2text(html)

      console.print("[bold green]📘 Problem Description[/bold green]")
      console.print(Markdown(md))

      # ------------------- Examples / Sample Testcases -------------------
      sample = problem.get("sampleTestCase", "")
      examples = problem.get("exampleTestcases", "")

      if sample:
          console.print("\n[bold blue]📌 Sample Test Cases[/bold blue]")
          console.print(f"[yellow]{sample}[/yellow]")

      if examples:
          console.print("\n[bold blue]📌 Example Testcases[/bold blue]")
          console.print(f"[green]{examples}[/green]\n")

      # ------------------- Topic Tags -------------------
      tags = problem.get("topicTags", [])
      taglist = ", ".join([t["name"] for t in tags])
      console.print(f"[bold magenta]Tags:[/bold magenta] {taglist}\n")

      # ------------------- Starter Code -------------------
      console.print("[bold cyan]📥 Starter code available. Use:[/bold cyan]")
      console.print(f"[white]lc download {title_slug} [--lang python/java/cpp/js][/white]\n")

      # ------------------- Return problem dictionary -------------------
      return {
          "id": problem["questionFrontendId"],
          "title": problem["title"],
          "slug": title_slug,
          "difficulty": problem["difficulty"],
          "content": md,
          "samples": sample,
          "examples": examples,
          "topics": taglist,
          "codeSnippets": problem.get("codeSnippets", []),
      }


    def daily(self) -> Optional[Dict]:
      from rich.console import Console
      from rich.markdown import Markdown
      import html2text

      console = Console()

      # ------------------ Fetch Daily Challenge ------------------
      query_daily = """
      query questionOfToday {
        activeDailyCodingChallengeQuestion {
          date
          link
          question {
            questionFrontendId
            title
            titleSlug
            difficulty
          }
        }
      }
      """
      data = self.api.graphql(query_daily)
      daily = data.get("activeDailyCodingChallengeQuestion")

      if not daily:
          console.print("[red]No daily challenge available.[/red]")
          return None

      q = daily["question"]
      slug = q["titleSlug"]

      # ------------------ Headers ------------------
      console.print(f"[bold yellow]🔥 Daily Challenge ({daily['date']})[/bold yellow]")
      console.print(f"[cyan]{q['questionFrontendId']} — {q['title']}[/cyan] — [green]{q['difficulty']}[/green]")
      console.print(f"🔗 https://leetcode.com/problems/{slug}/\n")

      # ------------------ Fetch Full Problem Details ------------------
      query_details = """
      query questionDetail($slug: String!) {
        question(titleSlug: $slug) {
          content
          codeSnippets {
            lang
            langSlug
            code
          }
          sampleTestCase
          exampleTestcases
          topicTags {
            name
          }
          difficulty
        }
      }
      """
      details = self.api.graphql(query_details, {"slug": slug})
      problem = details.get("question")

      if not problem:
          console.print("[red]Could not load question details.[/red]")
          return q

      # ------------------ Convert HTML → Markdown ------------------
      html = problem.get("content", "")
      md = html2text.html2text(html)
      console.print("[bold green]📘 Problem Description[/bold green]")
      console.print(Markdown(md))

      # ------------------- Examples / Sample Testcases -------------------
      sample = problem.get("sampleTestCase", "")
      examples = problem.get("exampleTestcases", "")

      if sample:
          console.print("\n[bold blue]📌 Sample Test Cases[/bold blue]")
          console.print(f"[yellow]{sample}[/yellow]")

      if examples:
          console.print("\n[bold blue]📌 Example Testcases[/bold blue]")
          console.print(f"[green]{examples}[/green]\n")

      # ------------------- Topic Tags -------------------
      tags = problem.get("topicTags", [])
      taglist = ", ".join([t["name"] for t in tags])
      console.print(f"[bold magenta]Tags:[/bold magenta] {taglist}\n")

      # ------------------- Starter Code -------------------
      console.print("[bold cyan]📥 Starter code available. Use:[/bold cyan]")
      console.print(f"[white]lc download {slug} [--lang python/java/cpp/js][/white]\n")

      # ------------------- Return problem dictionary -------------------
      return {
          "id": q["questionFrontendId"],
          "title": q["title"],
          "slug": slug,
          "difficulty": q["difficulty"],
          "content": md,
          "samples": sample,
          "examples": examples,
          "topics": taglist,
          "codeSnippets": problem.get("codeSnippets", []),
      }



    def stats(self, username: Optional[str] = None):

      if not username:
          username = self.get_logged_in_username()
      if not username:
          console.print("[red]Could not determine username. Provide username or ensure you are logged in.[/red]")
          return

      from datetime import datetime
      year = datetime.now().year

      # ---------------------- GraphQL Queries ----------------------

      query_profile = """
      query userProfile($username: String!) {
        matchedUser(username: $username) {
          username
          profile {
            realName
            countryName
            userAvatar
            ranking
            reputation
          }
          submitStatsGlobal {
            acSubmissionNum {
              difficulty
              count
              submissions
            }
          }
        }
      }
      """

      query_lang = """
      query userLanguageStats($username: String!) {
        matchedUser(username: $username) {
          languageProblemCount {
            languageName
            problemsSolved
          }
        }
      }
      """

      query_recent = """
      query recentAc($username: String!) {
        recentAcSubmissionList(username: $username, limit: 10) {
          id
          title
          titleSlug
          timestamp
        }
      }
      """

      query_badges = """
      query userBadges($username: String!) {
        matchedUser(username: $username) {
          badges {
            id
            displayName
            icon
          }
        }
      }
      """

      # ⭐ Contest rating
      query_contest = """
      query contestInfo($username: String!) {
        userContestRanking(username: $username) {
          rating
          globalRanking
          totalParticipants
          topPercentage
          attendedContestsCount
        }
      }
      """

      # ⭐ Heatmap
      query_calendar = """
      query userCalendar($username: String!, $year: Int!) {
        matchedUser(username: $username) {
          userCalendar(year: $year) {
            streak
            totalActiveDays
            submissionCalendar
          }
        }
      }
      """

      # ---------------------- Execute Queries ----------------------

      p = self.api.graphql(query_profile, {"username": username})
      l = self.api.graphql(query_lang, {"username": username})
      r = self.api.graphql(query_recent, {"username": username})
      b = self.api.graphql(query_badges, {"username": username})
      ct = self.api.graphql(query_contest, {"username": username})
      cal = self.api.graphql(query_calendar, {"username": username, "year": year})

      # ---------------------- Extract ----------------------

      user = p.get("matchedUser") or {}
      profile = user.get("profile", {})

      console.print(f"\n[bold yellow]📊 Stats for {username}[/bold yellow]\n")

      # ---------------------- Profile ----------------------
      console.print("[cyan]--- Profile ---[/cyan]")
      console.print(f"Name: {profile.get('realName')}")
      console.print(f"Country: {profile.get('countryName')}")
      console.print(f"Ranking: {profile.get('ranking')}")
      console.print(f"Reputation: {profile.get('reputation')}\n")

      # ---------------------- Contest Rating ----------------------
      console.print("[bold magenta]--- Contest Rating ---[/bold magenta]")
      c = ct.get("userContestRanking") or {}
      console.print(f"Rating: {c.get('rating')}")
      console.print(f"Global Rank: {c.get('globalRanking')} / {c.get('totalParticipants')}")
      console.print(f"Top %: {c.get('topPercentage')}")
      console.print(f"Contests Attended: {c.get('attendedContestsCount')}\n")

      # ---------------------- Problem Stats ----------------------
      console.print("[green]--- Problems Solved ---[/green]")
      for e in user.get("submitStatsGlobal", {}).get("acSubmissionNum", []):
          diff = e.get("difficulty")
          cnt = e.get("count")
          sub = e.get("submissions")
          console.print(f"{diff:6}: {cnt} solved ({sub} submissions)")
      console.print()

      # ---------------------- Language Stats ----------------------
      console.print("[cyan]--- Language Usage ---[/cyan]")
      langs = l.get("matchedUser", {}).get("languageProblemCount", [])
      for lang in langs:
          console.print(f"{lang['languageName']:10}: {lang['problemsSolved']} solved")
      console.print()

      # ---------------------- Recent AC ----------------------
      console.print("[blue]--- Recent Submissions ---[/blue]")
      for item in r.get("recentAcSubmissionList", []):
          ts = int(item["timestamp"])
          dt = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
          console.print(f"✔ {item['title']}  ({dt})")
      console.print()

      # ---------------------- Badges ----------------------
      console.print("[yellow]--- Badges ---[/yellow]")
      badges = b.get("matchedUser", {}).get("badges", [])
      for badge in badges:
          console.print(f"🏅 {badge['displayName']}")
      console.print()

      # ---------------------- Heatmap ----------------------
      from datetime import datetime, timezone
      import calendar
      import json

      console.print("\n[bold green]--- LeetCode Submission Heatmap ---[/bold green]\n")

      caldata = cal.get("matchedUser", {}).get("userCalendar", {})
      daymap = json.loads(caldata.get("submissionCalendar", "{}"))

      # LeetCode colors
      COLORS = [
          "[#606060]■[/]",  # 0
          "[#9be9a8]■[/]",  # 1
          "[#40c463]■[/]",  # 2–3
          "[#30a14e]■[/]",  # 4–7
          "[#216e39]■[/]",  # 8+
      ]

      def shade(cnt: int) -> str:
          if cnt == 0:
              return COLORS[0]
          elif cnt < 2:
              return COLORS[1]
          elif cnt < 4:
              return COLORS[2]
          elif cnt < 8:
              return COLORS[3]
          return COLORS[4]

      # Weekday headers
      weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
      console.print(" " * 8 + "  ".join(f"{d:^5}" for d in weekdays))

      for month in range(1, 13):
          month_name = calendar.month_name[month]
          days_in_month = calendar.monthrange(year, month)[1]

          console.print(f"\n[bold cyan]{month_name}[/bold cyan]")

          week = ["     "] * 7
          week_idx = 0

          for day in range(1, days_in_month + 1):
              dt = datetime(year, month, day, tzinfo=timezone.utc)
              ts = int(dt.timestamp())
              cnt = daymap.get(str(ts), 0)

              weekday = dt.weekday()  # Mon=0 … Sun=6
              col = (weekday + 1) % 7  # Convert to Sun=0

              week[col] = f"  {shade(cnt)}  "

              if col == 6 or day == days_in_month:
                  # prefix = f"{'':8}" if week_idx > 0 else f"{month_name:<8}"
                  console.print("        "+"  ".join(week))
                  week = ["     "] * 7
                  week_idx += 1

      # Legend
      console.print("\nLess ", *COLORS, " More", sep="")


      console.print(f"\nStreak: {caldata.get('streak')}")
      console.print(f"Active Days: {caldata.get('totalActiveDays')}\n")

    


    def download_starter(self, slug: str, lang: str = "python3", out_dir: str = ".") -> str:
      """
      Download ONLY the official LeetCode starter code.
      No testcases, no main(), no modification.
      """

      LANG_MAP = {
          "cpp": "C++",
          "c++": "C++",
          "python": "Python3",
          "python3": "Python3",
          "java": "Java",
          "js": "JavaScript",
          "javascript": "JavaScript",
          "c": "C",
          "go": "Go",
      }

      EXT_MAP = {
          "C++": "cpp",
          "C": "c",
          "Java": "java",
          "Python3": "py",
          "JavaScript": "js",
          "Go": "go",
      }

      lang_key = LANG_MAP.get(lang.lower(), lang)

      query = """
      query questionContent($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
          codeSnippets {
            lang
            code
          }
        }
      }
      """

      data = self.api.graphql(query, {"titleSlug": slug})
      question = data.get("question", {})
      snippets = question.get("codeSnippets", [])

      if not snippets:
          console.print("[red]No starter code available.[/red]")
          return ""

      # Select correct language snippet
      chosen = None
      for s in snippets:
          if s.get("lang") == lang_key:
              chosen = s
              break

      if not chosen:
          available = [s.get("lang") for s in snippets]
          console.print(
              f"[red]Language '{lang}' not available. Available: {available}[/red]"
          )
          return ""

      code = chosen.get("code", "")

      # Determine file extension
      ext = EXT_MAP.get(lang_key, lang_key.lower())
      filename = f"{slug}.{ext}"
      filepath = os.path.join(out_dir, filename)

      # Save starter code exactly as-is
      with open(filepath, "w", encoding="utf-8") as f:
          f.write(code)

      console.print(f"[green]Starter code saved to:[/green] {filepath}")
      return filepath
