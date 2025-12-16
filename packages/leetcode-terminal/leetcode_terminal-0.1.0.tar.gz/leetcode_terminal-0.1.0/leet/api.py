# leet/api.py
import requests
from typing import Optional

class LeetCodeAPI:
    def __init__(self, session: requests.Session):
        self.session = session
        self.url = "https://leetcode.com/graphql/"

    def graphql(self, query: str, variables: Optional[dict] = None, timeout: int = 20):
        payload = {"query": query, "variables": variables or {}}
        resp = self.session.post(self.url, json=payload, headers={"Referer": "https://leetcode.com"}, timeout=timeout)
        try:
            data = resp.json()
        except Exception:
            raise RuntimeError(f"Non-JSON response from LeetCode (status {resp.status_code}). Response snippet:\n{resp.text[:1000]}")
        if "errors" in data:
            raise RuntimeError(f"GraphQL error: {data['errors']}")
        # data may be {'data': {...}}
        return data.get("data", data)
    def get_question_id(self, slug: str):
        url = f"https://leetcode.com/api/problems/all/"
        res = self.session.get(url)
        items = res.json().get("stat_status_pairs", [])
        for x in items:
            if x["stat"]["question__title_slug"] == slug:
                return x["stat"]["question_id"]
        raise ValueError("Question ID not found for slug: " + slug)

    def slug_to_id(self, slug: str) -> str:
      url = f"https://leetcode.com/graphql"
      payload = {
          "query": """
          query questionSlugToId($titleSlug: String!) {
              question(titleSlug: $titleSlug) {
                  questionId
              }
          }
          """,
          "variables": {"titleSlug": slug},
      }
      headers = {"x-csrftoken": self.session.cookies.get("csrftoken"),
                "content-type": "application/json"}

      r = self.session.post(url, json=payload, headers=headers)
      return r.json()["data"]["question"]["questionId"]