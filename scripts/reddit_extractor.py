#!/usr/bin/env python3
"""
Reddit Data Extractor for Pool Service Knowledge Base
======================================================
Extracts posts and comments from pool-related subreddits using Reddit's official API.

SETUP REQUIRED:
1. Create a Reddit app at https://www.reddit.com/prefs/apps
2. Choose "script" as the app type
3. Note your client_id and client_secret
4. Create a .env file or set environment variables:
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   REDDIT_USER_AGENT=KBPooltech/1.0

Usage:
    python reddit_extractor.py --subreddit pools --limit 100
    python reddit_extractor.py --all-subreddits --limit 50
    python reddit_extractor.py --search "green pool" --limit 25
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import time

try:
    import praw
except ImportError:
    print("Installing praw (Reddit API wrapper)...")
    os.system("pip install praw --break-system-packages")
    import praw

try:
    from dotenv import load_dotenv
except ImportError:
    print("Installing python-dotenv...")
    os.system("pip install python-dotenv --break-system-packages")
    from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Configuration
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "raw" / "reddit"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Pool-related subreddits
POOL_SUBREDDITS = [
    "pools",           # Main pool subreddit
    "swimmingpools",   # General swimming pools
    "hottub",          # Hot tubs and spas
    "poolcare",        # Pool maintenance
]

# Common pool-related search terms for discovery
POOL_SEARCH_TERMS = [
    "green pool",
    "cloudy pool water",
    "pool pump not working",
    "salt cell",
    "pool filter",
    "pool algae",
    "pool chemistry",
    "pool leak",
    "pool heater",
    "chlorine levels",
    "CYA high",
    "pH balance pool",
    "pool opening",
    "pool closing winterize",
    "variable speed pump"
]


def get_reddit_client() -> Optional[praw.Reddit]:
    """
    Initialize Reddit API client.
    Requires environment variables or .env file with credentials.
    """
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT', 'KBPooltech/1.0 (Pool Service Knowledge Base)')

    if not client_id or not client_secret:
        print("=" * 60)
        print("REDDIT API CREDENTIALS REQUIRED")
        print("=" * 60)
        print("\nTo use this script, you need to:")
        print("1. Go to https://www.reddit.com/prefs/apps")
        print("2. Click 'create another app...'")
        print("3. Choose 'script' as the type")
        print("4. Set redirect uri to 'http://localhost:8080'")
        print("5. Create the app and note your client_id and secret")
        print("\nThen either:")
        print("  A. Create a .env file in the scripts folder with:")
        print("     REDDIT_CLIENT_ID=your_client_id")
        print("     REDDIT_CLIENT_SECRET=your_client_secret")
        print("\n  B. Or set environment variables before running")
        print("=" * 60)
        return None

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        # Test the connection
        reddit.user.me()
        return reddit
    except Exception as e:
        print(f"Error connecting to Reddit API: {e}")
        print("\nMake sure your credentials are correct.")
        return None


def classify_topic(text: str, title: str = "") -> str:
    """Classify the topic based on content keywords."""
    combined = (title + " " + text[:2000]).lower()

    topic_keywords = {
        "water_chemistry": ["ph", "chlorine", "alkalinity", "calcium", "cya", "stabilizer", "lsi", "balance", "chemical", "shock", "test"],
        "algae": ["algae", "green", "mustard", "black algae", "slam", "brush"],
        "equipment_pump": ["pump", "motor", "variable speed", "impeller", "prime", "air leak"],
        "equipment_filter": ["filter", "cartridge", "sand", "de", "backwash", "pressure"],
        "equipment_heater": ["heater", "heat pump", "gas heater", "temperature"],
        "equipment_cleaner": ["cleaner", "robot", "vacuum", "suction", "pressure side"],
        "troubleshooting": ["problem", "issue", "fix", "repair", "help", "not working", "broken"],
        "maintenance": ["clean", "brush", "skim", "maintenance", "routine", "weekly"],
        "saltwater": ["salt", "saltwater", "salt cell", "chlorine generator", "swg"],
        "opening_closing": ["open", "close", "winterize", "spring", "cover"]
    }

    scores = {topic: 0 for topic in topic_keywords}
    for topic, keywords in topic_keywords.items():
        for keyword in keywords:
            if keyword in combined:
                scores[topic] += 1

    if max(scores.values()) > 0:
        return max(scores, key=scores.get)
    return "general"


def estimate_difficulty(text: str, score: int) -> str:
    """Estimate difficulty level based on content complexity."""
    text_lower = text.lower()

    advanced_terms = ["lsi", "saturation index", "orenda", "taylor", "ppm calculation", "hydraulics"]
    beginner_terms = ["first pool", "new pool owner", "beginner", "basic", "help needed", "newbie"]

    advanced_count = sum(1 for term in advanced_terms if term in text_lower)
    beginner_count = sum(1 for term in beginner_terms if term in text_lower)

    if advanced_count >= 2:
        return "advanced"
    elif beginner_count >= 1 or "help" in text_lower[:100]:
        return "beginner"
    return "intermediate"


def process_submission(submission) -> Dict[str, Any]:
    """Process a Reddit submission (post) into structured format."""
    # Get top-level comments
    submission.comments.replace_more(limit=0)  # Don't load "more comments"
    comments = []

    for comment in submission.comments[:20]:  # Limit to top 20 comments
        if hasattr(comment, 'body') and comment.body != '[deleted]':
            comments.append({
                "author": str(comment.author) if comment.author else "[deleted]",
                "body": comment.body,
                "score": comment.score,
                "created_utc": datetime.fromtimestamp(comment.created_utc).isoformat()
            })

    # Combine post body and top comments for full content
    full_content = submission.selftext
    if comments:
        full_content += "\n\n--- TOP ANSWERS ---\n\n"
        for i, c in enumerate(comments[:10], 1):
            full_content += f"Answer {i} (score: {c['score']}):\n{c['body']}\n\n"

    record = {
        "source": "reddit",
        "source_type": "discussion",
        "post_id": submission.id,
        "url": f"https://reddit.com{submission.permalink}",
        "subreddit": str(submission.subreddit),
        "title": submission.title,
        "content": full_content,
        "post_body": submission.selftext,
        "author": str(submission.author) if submission.author else "[deleted]",
        "score": submission.score,
        "upvote_ratio": submission.upvote_ratio,
        "num_comments": submission.num_comments,
        "comments": comments,
        "topic": classify_topic(submission.selftext, submission.title),
        "difficulty_level": estimate_difficulty(submission.selftext, submission.score),
        "created_utc": datetime.fromtimestamp(submission.created_utc).isoformat(),
        "extracted_at": datetime.now().isoformat(),
        "metadata": {
            "flair": submission.link_flair_text,
            "is_self": submission.is_self,
            "over_18": submission.over_18
        }
    }

    return record


def save_record(record: Dict[str, Any], output_dir: Path = OUTPUT_DIR):
    """Save a single record to JSON file."""
    filename = f"{record['subreddit']}_{record['post_id']}.json"
    filepath = output_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

    print(f"  Saved: {filepath.name}")


def extract_subreddit(reddit: praw.Reddit, subreddit_name: str, limit: int = 100,
                      sort: str = "top", time_filter: str = "all"):
    """
    Extract posts from a subreddit.

    Args:
        reddit: PRAW Reddit instance
        subreddit_name: Name of the subreddit
        limit: Maximum number of posts to extract
        sort: Sort method (hot, new, top, rising)
        time_filter: Time filter for 'top' sort (hour, day, week, month, year, all)
    """
    print(f"\nExtracting from r/{subreddit_name} (sort: {sort}, limit: {limit})")

    try:
        subreddit = reddit.subreddit(subreddit_name)

        if sort == "top":
            submissions = subreddit.top(time_filter=time_filter, limit=limit)
        elif sort == "hot":
            submissions = subreddit.hot(limit=limit)
        elif sort == "new":
            submissions = subreddit.new(limit=limit)
        else:
            submissions = subreddit.hot(limit=limit)

        processed = 0
        for submission in submissions:
            try:
                # Skip non-text posts
                if not submission.is_self:
                    continue

                record = process_submission(submission)
                save_record(record)
                processed += 1

                # Rate limiting
                time.sleep(0.5)

            except Exception as e:
                print(f"  Error processing post {submission.id}: {e}")

        print(f"  Extracted {processed} posts from r/{subreddit_name}")

    except Exception as e:
        print(f"Error accessing r/{subreddit_name}: {e}")


def search_reddit(reddit: praw.Reddit, query: str, limit: int = 25):
    """Search Reddit for pool-related content."""
    print(f"\nSearching Reddit for: '{query}'")

    try:
        results = reddit.subreddit("all").search(
            query,
            sort="relevance",
            time_filter="all",
            limit=limit
        )

        processed = 0
        for submission in results:
            try:
                # Only process text posts
                if not submission.is_self:
                    continue

                record = process_submission(submission)
                save_record(record)
                processed += 1
                time.sleep(0.5)

            except Exception as e:
                print(f"  Error processing search result: {e}")

        print(f"  Found {processed} relevant posts for '{query}'")

    except Exception as e:
        print(f"Error searching Reddit: {e}")


def main():
    parser = argparse.ArgumentParser(description='Reddit Data Extractor for Pool Service KB')
    parser.add_argument('--subreddit', type=str, help='Subreddit to extract from')
    parser.add_argument('--all-subreddits', action='store_true', help='Extract from all known pool subreddits')
    parser.add_argument('--search', type=str, help='Search query')
    parser.add_argument('--all-searches', action='store_true', help='Run all predefined search queries')
    parser.add_argument('--limit', type=int, default=100, help='Max posts per subreddit/search')
    parser.add_argument('--sort', type=str, default='top', choices=['hot', 'new', 'top', 'rising'])
    parser.add_argument('--time', type=str, default='all', choices=['hour', 'day', 'week', 'month', 'year', 'all'])
    parser.add_argument('--list-subreddits', action='store_true', help='List known pool subreddits')

    args = parser.parse_args()

    if args.list_subreddits:
        print("Known pool-related subreddits:")
        for sub in POOL_SUBREDDITS:
            print(f"  r/{sub}")
        print("\nPredefined search terms:")
        for term in POOL_SEARCH_TERMS:
            print(f"  - {term}")
        return

    # Initialize Reddit client
    reddit = get_reddit_client()
    if not reddit:
        return

    if args.subreddit:
        extract_subreddit(reddit, args.subreddit, args.limit, args.sort, args.time)
    elif args.all_subreddits:
        for subreddit in POOL_SUBREDDITS:
            extract_subreddit(reddit, subreddit, args.limit, args.sort, args.time)
            time.sleep(2)
    elif args.search:
        search_reddit(reddit, args.search, args.limit)
    elif args.all_searches:
        for query in POOL_SEARCH_TERMS:
            search_reddit(reddit, query, args.limit)
            time.sleep(2)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
