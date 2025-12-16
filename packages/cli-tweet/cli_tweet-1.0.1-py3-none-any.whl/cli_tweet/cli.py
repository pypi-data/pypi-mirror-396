# src/autotweet/cli.py
from __future__ import annotations

import sys
from datetime import timezone

import tweepy

from .config import load_secrets, TWEET_LIMIT


def create_client() -> tweepy.Client:
    secrets = load_secrets()
    return tweepy.Client(
        consumer_key=secrets["TWITTER_API_KEY"],
        consumer_secret=secrets["TWITTER_API_KEY_SECRET"],
        access_token=secrets["ACCESS_TOKEN"],
        access_token_secret=secrets["ACCESS_TOKEN_SECRET"],
    )


def send_tweet(tweet_text: str) -> None:
    client = create_client()
    response = client.create_tweet(text=tweet_text)
    print(f"✅ Tweet sent! ID: {response.data['id']}")


def get_my_user(client: tweepy.Client) -> tuple[str, str]:
    """Return (user_id, username) for the authenticated user."""
    me = client.get_me(user_auth=True)
    if not me.data:
        raise RuntimeError("Could not fetch authenticated user profile.")
    return str(me.data.id), me.data.username


def list_my_recent(limit: int = 5) -> None:
    client = create_client()
    user_id, username = get_my_user(client)
    # Tweepy allows up to 100 per request; keep a sensible default.
    limit = max(1, min(limit, 100))
    response = client.get_users_tweets(
        id=user_id,
        max_results=limit,
        tweet_fields=["created_at"],
        user_auth=True,
    )

    tweets = response.data or []
    if not tweets:
        print(f"No recent posts found for @{username}.")
        return

    print(f"Recent posts by @{username} (newest first):")
    for idx, tweet in enumerate(tweets, start=1):
        created = tweet.created_at
        if created and created.tzinfo is None:
            # Normalize naive datetimes to UTC for consistent output.
            created = created.replace(tzinfo=timezone.utc)
        timestamp = created.isoformat(timespec="minutes") if created else "unknown time"
        one_liner = " ".join(tweet.text.strip().split())
        print(f"{idx}. [{tweet.id}] {timestamp} — {one_liner}")


def reply_to_own_tweet(tweet_id: str, reply_text: str) -> None:
    client = create_client()
    user_id, username = get_my_user(client)

    original = client.get_tweet(
        tweet_id, tweet_fields=["author_id"], user_auth=True
    )
    author_id = getattr(original.data, "author_id", None) if original.data else None
    if author_id and str(author_id) != user_id:
        raise RuntimeError(
            f"Tweet {tweet_id} is not authored by @{username}; refusing to reply."
        )

    response = client.create_tweet(
        text=reply_text, in_reply_to_tweet_id=tweet_id, user_auth=True
    )
    print(
        f"✅ Comment posted! ID: {response.data['id']} "
        f"(in reply to {tweet_id})"
    )


def interactive_compose() -> str | None:
    """
    Simple REPL-like tweet composer.

    Controls:
      - Type your tweet, multiple lines allowed
      - `/send` on an empty line → finish and send
      - `/clear` → clear current text
      - `/quit` or Ctrl+D → abort without sending
    """
    print("=== Tweet composer ===")
    print("Type your tweet. Multi-line is allowed.")
    print("Commands: /send, /clear, /quit")
    print("(Ctrl+D also quits)\n")

    lines: list[str] = []

    while True:
        try:
            prompt = ">>> " if not lines else "... "
            line = input(prompt)
        except EOFError:
            print("\nAborted.")
            return None

        if line.strip() == "/quit":
            print("Aborted.")
            return None
        if line.strip() == "/clear":
            lines.clear()
            print("[cleared]")
            continue
        if line.strip() == "/send":
            tweet_text = "\n".join(lines).strip()
            if not tweet_text:
                print("⚠️  Nothing to send.")
                continue
            return tweet_text

        lines.append(line)
        tweet_text = "\n".join(lines)
        length = len(tweet_text)
        over = length - TWEET_LIMIT

        if over > 0:
            print(f"[{length} chars, {over} over {TWEET_LIMIT} ⚠️]")
        else:
            remaining = TWEET_LIMIT - length
            print(f"[{length} chars, {remaining} left]")


def main() -> None:
    # Mode 0: subcommands
    if len(sys.argv) >= 2 and sys.argv[1] in {"list", "ls"}:
        try:
            count = int(sys.argv[2]) if len(sys.argv) >= 3 else 5
        except ValueError:
            print("Error: list expects an optional integer count.")
            return
        try:
            list_my_recent(count)
        except Exception as e:
            print(f"❌ Error: {e}")
        return

    if len(sys.argv) >= 3 and sys.argv[1] in {"reply", "comment"}:
        tweet_id = sys.argv[2]
        reply_text = " ".join(sys.argv[3:]).strip()
        if not reply_text:
            print("Error: No reply text provided.")
            print("Usage: cli_tweet reply <tweet_id> \"your reply text\"")
            return
        if len(reply_text) > TWEET_LIMIT:
            print(
                f"Error: Reply is {len(reply_text)} chars "
                f"({len(reply_text) - TWEET_LIMIT} over limit)."
            )
            return
        try:
            reply_to_own_tweet(tweet_id, reply_text)
        except Exception as e:
            print(f"❌ Error: {e}")
        return

    # Mode 1: no args → interactive compose mode
    if len(sys.argv) == 1:
        tweet_text = interactive_compose()
        if tweet_text is None:
            return
        try:
            send_tweet(tweet_text)
        except Exception as e:
            print(f"❌ Error: {e}")
        return

    # Mode 2: with args → one-liner via CLI
    tweet_text = " ".join(sys.argv[1:])
    if not tweet_text.strip():
        print("Error: No text provided.")
        print("Usage: autotweet \"Hello World\"")
        return

    try:
        send_tweet(tweet_text)
    except Exception as e:
        print(f"❌ Error: {e}")
