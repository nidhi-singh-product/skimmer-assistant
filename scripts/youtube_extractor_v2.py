#!/usr/bin/env python3
"""
YouTube Transcript Extractor v2 - Using Official APIs
======================================================
This version uses:
1. Official YouTube Data API v3 for video discovery (requires API key)
2. youtube-transcript-api for transcripts (uses YouTube's public transcript endpoints)

SETUP:
1. Go to https://console.cloud.google.com
2. Create a project and enable "YouTube Data API v3"
3. Create an API key (no OAuth needed for public data)
4. Set: export YOUTUBE_API_KEY=your_key_here

Usage:
    python youtube_extractor_v2.py --video-id "dQw4w9WgXcQ"
    python youtube_extractor_v2.py --video-url "https://www.youtube.com/watch?v=VIDEO_ID"
    python youtube_extractor_v2.py --channel-id "UCpS3qJfJFyJsPIaEtvjA8mA" --max-videos 20
    python youtube_extractor_v2.py --playlist-id "PLxxxxxxx" --max-videos 50
"""

import os
import json
import re
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import time

# Check for required packages
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("Installing google-api-python-client...")
    os.system("pip install google-api-python-client")
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    print("Installing youtube-transcript-api...")
    os.system("pip install youtube-transcript-api")
    from youtube_transcript_api import YouTubeTranscriptApi

try:
    from dotenv import load_dotenv
except ImportError:
    print("Installing python-dotenv...")
    os.system("pip install python-dotenv")
    from dotenv import load_dotenv

load_dotenv()

# Configuration
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "raw" / "youtube"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Pool service channel IDs (official YouTube channel IDs)
POOL_CHANNELS = {
    "SwimUniversity": {
        "channel_id": "UCoxxrQ_l87I7rbw1L1JG0jA",
        "name": "Swim University",
        "focus": "homeowner fundamentals",
        "difficulty": "beginner"
    },
    "InyoPools": {
        "channel_id": "UC2WIYX5pTR7rkz7GrV4fnAg",
        "name": "Inyo Pools",
        "focus": "equipment guides",
        "difficulty": "beginner"
    },
    "PoolChasers": {
        "channel_id": "UCYfmE4kSk5HEcgpPkUR4XhA",
        "name": "Pool Chasers",
        "focus": "business growth",
        "difficulty": "intermediate"
    }
}


def get_youtube_client():
    """Initialize YouTube Data API client."""
    api_key = os.getenv('YOUTUBE_API_KEY')

    if not api_key:
        print("=" * 60)
        print("YOUTUBE DATA API KEY REQUIRED")
        print("=" * 60)
        print("\nTo use the official YouTube API:")
        print("1. Go to https://console.cloud.google.com")
        print("2. Create a new project (or select existing)")
        print("3. Go to 'APIs & Services' > 'Enable APIs'")
        print("4. Search for and enable 'YouTube Data API v3'")
        print("5. Go to 'Credentials' > 'Create Credentials' > 'API Key'")
        print("6. Copy the API key")
        print("\nThen either:")
        print("  export YOUTUBE_API_KEY=your_key_here")
        print("  OR add to .env file: YOUTUBE_API_KEY=your_key_here")
        print("=" * 60)
        return None

    return build('youtube', 'v3', developerKey=api_key)


def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from various YouTube URL formats."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_video_details(youtube, video_id: str) -> Optional[Dict[str, Any]]:
    """Get video metadata using official API."""
    try:
        response = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=video_id
        ).execute()

        if response['items']:
            item = response['items'][0]
            snippet = item['snippet']
            return {
                'video_id': video_id,
                'title': snippet['title'],
                'description': snippet['description'],
                'channel_title': snippet['channelTitle'],
                'channel_id': snippet['channelId'],
                'published_at': snippet['publishedAt'],
                'tags': snippet.get('tags', []),
                'duration': item['contentDetails']['duration'],
                'view_count': item['statistics'].get('viewCount', 0),
                'like_count': item['statistics'].get('likeCount', 0)
            }
    except HttpError as e:
        print(f"  API error getting video details: {e}")
    return None


def get_channel_videos(youtube, channel_id: str, max_videos: int = 50) -> List[str]:
    """Get video IDs from a channel using official API."""
    video_ids = []

    try:
        # First, get the uploads playlist ID
        channel_response = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()

        if not channel_response['items']:
            print(f"  Channel not found: {channel_id}")
            return []

        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # Get videos from uploads playlist
        next_page_token = None
        while len(video_ids) < max_videos:
            playlist_response = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=uploads_playlist_id,
                maxResults=min(50, max_videos - len(video_ids)),
                pageToken=next_page_token
            ).execute()

            for item in playlist_response['items']:
                video_ids.append(item['contentDetails']['videoId'])

            next_page_token = playlist_response.get('nextPageToken')
            if not next_page_token:
                break

        print(f"  Found {len(video_ids)} videos")

    except HttpError as e:
        print(f"  API error: {e}")

    return video_ids


def get_playlist_videos(youtube, playlist_id: str, max_videos: int = 50) -> List[str]:
    """Get video IDs from a playlist using official API."""
    video_ids = []

    try:
        next_page_token = None
        while len(video_ids) < max_videos:
            response = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=playlist_id,
                maxResults=min(50, max_videos - len(video_ids)),
                pageToken=next_page_token
            ).execute()

            for item in response['items']:
                video_ids.append(item['contentDetails']['videoId'])

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        print(f"  Found {len(video_ids)} videos in playlist")

    except HttpError as e:
        print(f"  API error: {e}")

    return video_ids


def get_transcript(video_id: str, languages: List[str] = ['en']) -> Optional[Dict[str, Any]]:
    """
    Fetch transcript using youtube-transcript-api.
    This uses YouTube's public transcript endpoints.
    """
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)

        # Try manually created first, then auto-generated
        transcript = None
        for lang in languages:
            try:
                transcript = transcript_list.find_manually_created_transcript([lang])
                break
            except:
                try:
                    transcript = transcript_list.find_generated_transcript([lang])
                    break
                except:
                    continue

        if transcript:
            data = transcript.fetch()
            # Convert to list of dicts for JSON serialization (library now returns objects)
            segments = [{'text': entry.text, 'start': entry.start, 'duration': entry.duration} for entry in data]
            full_text = ' '.join([s['text'] for s in segments])

            return {
                "video_id": video_id,
                "language": transcript.language_code,
                "is_generated": transcript.is_generated,
                "full_text": full_text,
                "segments": segments,
                "word_count": len(full_text.split()),
                "duration_seconds": segments[-1]['start'] + segments[-1]['duration'] if segments else 0
            }

    except Exception as e:
        print(f"  No transcript available: {e}")

    return None


def classify_topic(text: str, title: str = "") -> str:
    """Classify content topic based on keywords."""
    combined = (title + " " + text[:1000]).lower()

    topic_keywords = {
        "water_chemistry": ["ph", "chlorine", "alkalinity", "calcium", "cya", "stabilizer", "lsi", "balance", "chemical", "shock", "algae"],
        "equipment": ["pump", "filter", "heater", "motor", "valve", "skimmer", "cleaner", "robot", "variable speed"],
        "troubleshooting": ["problem", "issue", "fix", "repair", "leak", "cloudy", "green", "diagnose"],
        "maintenance": ["clean", "brush", "vacuum", "skim", "backwash", "maintenance", "routine"],
        "business": ["route", "customer", "pricing", "profit", "marketing", "growth", "business"],
        "saltwater": ["salt", "saltwater", "salt cell", "chlorine generator"]
    }

    scores = {topic: 0 for topic in topic_keywords}
    for topic, keywords in topic_keywords.items():
        for keyword in keywords:
            if keyword in combined:
                scores[topic] += 1

    if max(scores.values()) > 0:
        return max(scores, key=scores.get)
    return "general"


def process_video(video_id: str, youtube=None, channel_info: Dict = None) -> Optional[Dict[str, Any]]:
    """Process a single video: get metadata and transcript."""
    print(f"  Processing: {video_id}")

    # Get metadata (if API client available)
    metadata = {}
    if youtube:
        metadata = get_video_details(youtube, video_id) or {}

    if not metadata:
        metadata = {
            'video_id': video_id,
            'title': 'Unknown',
            'description': '',
            'url': f'https://www.youtube.com/watch?v={video_id}'
        }

    # Get transcript
    transcript_data = get_transcript(video_id)
    if not transcript_data:
        print(f"    Skipping (no transcript)")
        return None

    # Classify topic
    topic = classify_topic(transcript_data['full_text'], metadata.get('title', ''))

    record = {
        "source": "youtube",
        "source_type": "video_transcript",
        "video_id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "title": metadata.get('title', 'Unknown'),
        "description": metadata.get('description', '')[:500],
        "content": transcript_data['full_text'],
        "topic": topic,
        "difficulty_level": channel_info.get('difficulty', 'intermediate') if channel_info else 'intermediate',
        "channel": metadata.get('channel_title', channel_info.get('name', 'Unknown') if channel_info else 'Unknown'),
        "word_count": transcript_data['word_count'],
        "duration_seconds": transcript_data['duration_seconds'],
        "language": transcript_data['language'],
        "is_auto_generated": transcript_data['is_generated'],
        "published_at": metadata.get('published_at'),
        "view_count": metadata.get('view_count'),
        "extracted_at": datetime.now().isoformat(),
        "metadata": {
            "focus_area": channel_info.get('focus', 'general') if channel_info else 'general',
            "tags": metadata.get('tags', [])[:10]
        }
    }

    return record


def save_record(record: Dict[str, Any]):
    """Save record to JSON file."""
    filename = f"{record['video_id']}.json"
    filepath = OUTPUT_DIR / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

    print(f"    Saved: {filename}")


def main():
    parser = argparse.ArgumentParser(description='YouTube Transcript Extractor (Official API)')
    parser.add_argument('--video-id', type=str, help='Single video ID to process')
    parser.add_argument('--video-url', type=str, help='Single video URL to process')
    parser.add_argument('--channel-id', type=str, help='Channel ID to get videos from')
    parser.add_argument('--channel-name', type=str, help='Known channel name (SwimUniversity, InyoPools, etc.)')
    parser.add_argument('--playlist-id', type=str, help='Playlist ID to get videos from')
    parser.add_argument('--max-videos', type=int, default=20, help='Max videos to process')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests')
    parser.add_argument('--list-channels', action='store_true', help='List known channels')
    parser.add_argument('--no-api', action='store_true', help='Skip YouTube API (transcript only mode)')

    args = parser.parse_args()

    if args.list_channels:
        print("Known pool service channels:")
        for name, info in POOL_CHANNELS.items():
            print(f"  {name}: {info['channel_id']} - {info['focus']}")
        return

    # Initialize YouTube API (optional)
    youtube = None
    if not args.no_api:
        youtube = get_youtube_client()
        if not youtube and (args.channel_id or args.channel_name or args.playlist_id):
            print("\nYouTube API key required for channel/playlist processing.")
            print("Use --no-api with --video-id to process single videos without API key.")
            return

    # Process based on arguments
    if args.video_url:
        video_id = extract_video_id(args.video_url)
        if video_id:
            record = process_video(video_id, youtube)
            if record:
                save_record(record)
        else:
            print(f"Could not extract video ID from: {args.video_url}")

    elif args.video_id:
        record = process_video(args.video_id, youtube)
        if record:
            save_record(record)

    elif args.channel_name:
        if args.channel_name not in POOL_CHANNELS:
            print(f"Unknown channel: {args.channel_name}")
            print(f"Use --list-channels to see available options")
            return

        channel_info = POOL_CHANNELS[args.channel_name]
        print(f"\nProcessing channel: {channel_info['name']}")

        video_ids = get_channel_videos(youtube, channel_info['channel_id'], args.max_videos)

        for vid in video_ids:
            record = process_video(vid, youtube, channel_info)
            if record:
                save_record(record)
            time.sleep(args.delay)

    elif args.channel_id:
        print(f"\nProcessing channel: {args.channel_id}")
        video_ids = get_channel_videos(youtube, args.channel_id, args.max_videos)

        for vid in video_ids:
            record = process_video(vid, youtube)
            if record:
                save_record(record)
            time.sleep(args.delay)

    elif args.playlist_id:
        print(f"\nProcessing playlist: {args.playlist_id}")
        video_ids = get_playlist_videos(youtube, args.playlist_id, args.max_videos)

        for vid in video_ids:
            record = process_video(vid, youtube)
            if record:
                save_record(record)
            time.sleep(args.delay)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
