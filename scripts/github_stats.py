"""Collect public GitHub metrics, regardless of the token's private access."""

import json
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class GitHub:
    def __init__(self, token):
        self.token = token

    def request(self, path, payload=None):
        request = Request(
            f"https://api.github.com/{path}",
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
                "User-Agent": "ylongw-public-profile",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        for attempt in range(4):
            try:
                with urlopen(request, timeout=40) as response:
                    return json.load(response)
            except HTTPError as error:
                if error.code not in (429, 500, 502, 503, 504) or attempt == 3:
                    raise RuntimeError(f"GitHub API returned HTTP {error.code}") from None
            except (URLError, TimeoutError):
                if attempt == 3:
                    raise RuntimeError("GitHub API could not be reached") from None
            time.sleep(2 ** attempt)

    def graphql(self, query, variables):
        result = self.request("graphql", {"query": query, "variables": variables})
        if result.get("errors") or not result.get("data", {}).get("user"):
            raise RuntimeError("GitHub GraphQL failed; no partial statistics were saved")
        return result["data"]["user"]


def public_owned_repositories(client, username):
    repositories = []
    page = 1
    while True:
        query = urlencode({"type": "owner", "per_page": 100, "page": page})
        batch = client.request(f"users/{username}/repos?{query}")
        repositories.extend(
            repository for repository in batch
            if repository.get("private") is False
            and repository.get("visibility") == "public"
            and repository.get("owner", {}).get("login", "").lower() == username.lower()
        )
        if len(batch) < 100:
            return repositories
        page += 1


def timestamp(value):
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


def public_commits(client, username, start, end):
    query = """query($login:String!, $from:DateTime!, $to:DateTime!) {
      user(login:$login) {
        contributionsCollection(from:$from, to:$to) {
          commitContributionsByRepository(maxRepositories:100) {
            repository { visibility }
            contributions { totalCount }
          }
        }
      }
    }"""
    user = client.graphql(query, {"login": username, "from": timestamp(start), "to": timestamp(end)})
    groups = user["contributionsCollection"]["commitContributionsByRepository"]
    if len(groups) >= 100:
        start_day = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end_day = end.replace(hour=0, minute=0, second=0, microsecond=0)
        if start_day == end_day:
            raise RuntimeError("Commit repository limit reached for one day; refusing a partial total")
        split = start_day + timedelta(days=max(1, (end_day - start_day).days // 2))
        return public_commits(client, username, start, split - timedelta(seconds=1)) + public_commits(
            client, username, split, end
        )
    return sum(
        group["contributions"]["totalCount"] for group in groups
        if (group.get("repository") or {}).get("visibility") == "PUBLIC"
    )


def public_contribution_count(client, username, start, end, connection):
    options = {
        "issueContributions": ", excludeFirst:false, excludePopular:false",
        "pullRequestContributions": ", excludeFirst:false, excludePopular:false",
        "pullRequestReviewContributions": "",
        "repositoryContributions": ", excludeFirst:false",
    }
    selection = {
        "issueContributions": "item:issue { repository { visibility } }",
        "pullRequestContributions": "item:pullRequest { repository { visibility } }",
        "pullRequestReviewContributions": "repository { visibility }",
        "repositoryContributions": "repository { visibility }",
    }
    query = """query($login:String!, $from:DateTime!, $to:DateTime!, $cursor:String) {
      user(login:$login) {
        contributionsCollection(from:$from, to:$to) {
          CONNECTION(first:100, after:$cursor OPTIONS) {
            nodes { isRestricted SELECTION }
            pageInfo { hasNextPage endCursor }
          }
        }
      }
    }""".replace("CONNECTION", connection).replace("OPTIONS", options[connection]).replace("SELECTION", selection[connection])
    count = 0
    cursor = None
    while True:
        user = client.graphql(query, {
            "login": username, "from": timestamp(start), "to": timestamp(end), "cursor": cursor,
        })
        result = user["contributionsCollection"][connection]
        count += sum(
            1 for node in result["nodes"] if node and node.get("isRestricted") is False
            and ((node.get("item") or node).get("repository") or {}).get("visibility") == "PUBLIC"
        )
        if not result["pageInfo"]["hasNextPage"]:
            return count
        next_cursor = result["pageInfo"]["endCursor"]
        if not next_cursor or next_cursor == cursor:
            raise RuntimeError("GitHub pagination did not advance")
        cursor = next_cursor


def fetch_stats(token, username="ylongw", now=None):
    client = GitHub(token)
    now = (now or datetime.now(timezone.utc)).replace(microsecond=0)
    start = (now - timedelta(days=364)).replace(hour=0, minute=0, second=0)
    user = client.request(f"users/{username}")
    repositories = public_owned_repositories(client, username)
    originals = [repository for repository in repositories if not repository["fork"]]
    language_bytes = Counter()

    def languages(repository):
        return client.request(f"repos/{repository['full_name']}/languages")

    with ThreadPoolExecutor(max_workers=6) as executor:
        for sizes in executor.map(languages, originals):
            language_bytes.update(sizes)

    contributions = {"commits": public_commits(client, username, start, now)}
    for label, connection in (
        ("issues", "issueContributions"),
        ("pull_requests", "pullRequestContributions"),
        ("reviews", "pullRequestReviewContributions"),
        ("repositories_created", "repositoryContributions"),
    ):
        contributions[label] = public_contribution_count(client, username, start, now, connection)
    return {
        "username": username,
        "updated_at": timestamp(now),
        "period_start": timestamp(start),
        "period_end": timestamp(now),
        "public_repositories": len(repositories),
        "original_repositories": len(originals),
        "stars": sum(repository["stargazers_count"] for repository in repositories),
        "followers": user["followers"],
        "contributions": contributions,
        "total_contributions": sum(contributions.values()),
        "language_bytes": dict(sorted(language_bytes.items(), key=lambda item: (-item[1], item[0]))),
        "scope": "Public owned repositories (including forks); language bytes exclude forks; public contributions only.",
    }
