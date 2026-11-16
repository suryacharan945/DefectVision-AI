#!/usr/bin/env python3
"""
DefectVision AI — GitHub Publication Automation Helper

Executes controlled publication steps via GitHub REST API:
1. Make existing repo private and verify visibility change.
2. Create new public repository with empty initial state.
"""

import os
import sys
import subprocess
import urllib.request
import json

def get_github_token():
    p = subprocess.Popen(
        ['git', 'credential', 'fill'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, _ = p.communicate(input='protocol=https\nhost=github.com\n\n')
    for line in out.splitlines():
        if line.startswith('password='):
            return line.split('=', 1)[1].strip()
    return None

def make_repo_private(owner, repo, token):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    data = json.dumps({"private": True}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="PATCH")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "DefectVision-Controlled-Publication")
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        return res

def create_public_repo(repo_name, description, token):
    url = "https://api.github.com/user/repos"
    payload = {
        "name": repo_name,
        "description": description,
        "private": False,
        "auto_init": False,  # Completely empty initial state: no README, license, or gitignore
        "has_issues": True,
        "has_wiki": False,
        "has_projects": False
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "DefectVision-Controlled-Publication")
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        return res

def verify_repo_visibility(owner, repo, token):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "DefectVision-Controlled-Publication")

    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        return res.get("private"), res.get("visibility")

def main():
    if len(sys.argv) < 2:
        print("Usage: github_publication_helper.py [make-private | create-public | check-visibility]")
        sys.exit(1)

    action = sys.argv[1]
    token = get_github_token()
    if not token:
        print("[ERROR] Failed to obtain GitHub token from git-credential-manager.")
        sys.exit(1)

    if action == "make-private":
        owner = "suryacharan945"
        repo = "DefectVision-AI"
        print(f"Modifying visibility for {owner}/{repo} to PRIVATE...")
        res = make_repo_private(owner, repo, token)
        print(f"Result: full_name={res.get('full_name')}, private={res.get('private')}, visibility={res.get('visibility')}")

    elif action == "create-public":
        repo_name = "DefectVisionAI-OpenSource"
        desc = "DefectVision AI — Reproducible Industrial Visual Anomaly Detection Platform (Clean-Room Open-Source Release)"
        print(f"Creating empty public repository: {repo_name}...")
        res = create_public_repo(repo_name, desc, token)
        print(f"Result: full_name={res.get('full_name')}, html_url={res.get('html_url')}, private={res.get('private')}")

    elif action == "check-visibility":
        owner = sys.argv[2]
        repo = sys.argv[3]
        is_private, vis = verify_repo_visibility(owner, repo, token)
        print(f"Repo {owner}/{repo}: private={is_private}, visibility={vis}")

if __name__ == "__main__":
    main()
