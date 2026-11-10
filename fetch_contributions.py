#!/usr/bin/env python3
"""
Fetch GitHub Contribution Data for Ujjwal-Qubit
Supports:
  1. Authenticated GitHub GraphQL API (when GITHUB_TOKEN is present in env, e.g. in GitHub Actions)
  2. Public fallback API / scraper when running locally without tokens
Saves normalized output to data/contributions.json
"""

import os
import sys
import json
import urllib.request

USERNAME = "Ujjwal-Qubit"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "contributions.json")
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_via_graphql(token):
    print(f"[*] Querying GitHub GraphQL API for {USERNAME}...")
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
                contributionLevel
              }
            }
          }
        }
      }
    }
    """
    url = "https://api.github.com/graphql"
    payload = json.dumps({"query": query, "variables": {"login": USERNAME}}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": "GitHub-Cards-Generator",
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
    
    cal = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    total = cal["totalContributions"]
    
    level_map = {
        "NONE": 0,
        "FIRST_QUARTILE": 1,
        "SECOND_QUARTILE": 2,
        "THIRD_QUARTILE": 3,
        "FOURTH_QUARTILE": 4
    }

    days = []
    for week in cal["weeks"]:
        for d in week["contributionDays"]:
            days.append({
                "date": d["date"],
                "count": d["contributionCount"],
                "level": level_map.get(d["contributionLevel"], 0)
            })

    return {
        "total": {"lastYear": total},
        "contributions": days
    }

def fetch_via_public_api():
    print(f"[*] Querying public contribution endpoint for {USERNAME}...")
    url = f"https://github-contributions-api.jogruber.de/v4/{USERNAME}?y=last"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data

def main():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    data = None

    if token:
        try:
            data = fetch_via_graphql(token)
            print("[+] Successfully fetched via GitHub GraphQL API.")
        except Exception as e:
            print(f"[!] GraphQL error: {e}. Falling back to public endpoint...")

    if not data:
        try:
            data = fetch_via_public_api()
            print("[+] Successfully fetched via public API.")
        except Exception as e:
            print(f"[!] Public API error: {e}")
            if os.path.exists(OUTPUT_FILE):
                print("[*] Preserving existing contributions.json file.")
                return
            else:
                raise e

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    total_cnt = data.get("total", {}).get("lastYear", sum(d["count"] for d in data.get("contributions", [])))
    print(f"[+] Saved {len(data.get('contributions', []))} contribution records ({total_cnt} total) to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
