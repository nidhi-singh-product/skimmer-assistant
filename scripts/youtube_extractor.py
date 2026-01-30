#!/usr/bin/env python3
"""
YouTube Transcript Extractor for Pool Service Knowledge Base
============================================================
Extracts transcripts from YouTube videos using the youtube-transcript-api library.
No API key required - uses publicly available transcript data.

Usage:
    python youtube_extractor.py --channel "SwimUniversity" --max-videos 50
    python youtube_extractor.py --video-url "https://www.youtube.com/watch?v=VIDEO_ID"
    python youtube_extractor.py --playlist "PLAYLIST_ID"
"""

import os
import json
import re
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import time

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
except ImportError:
    print("Installing youtube-transcript-api...")
    os.system("pip install youtube-transcript-api --break-system-packages")
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system("pip install requests --break-system-packages")
    import requests

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing beautifulsoup4...")
    os.system("pip install beautifulsoup4 --break-system-packages")
    from bs4 import BeautifulSoup


# Configuration
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "raw" / "youtube"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Pool service YouTube channels with their channel handles/IDs
POOL_CHANNELS = {
    "SwimUniversity": {
        "handle": "@SwimUniversity",
        "channel_id": "UCpS3qJfJFyJsPIaEtvjA8mA",
        "focus": "homeowner fundamentals",
        "difficulty": "beginner"
    },
    "SPL": {
        "handle": "@SPL",
        "channel_id": None,  # Will need to extract
        "focus": "professional service",
        "difficulty": "intermediate"
    },
    "ChlorineKingPoolService": {
        "handle": "@ChlorineKingPoolService",
        "channel_id": None,
        "focus": "business and troubleshooting",
        "difficulty": "intermediate"
    },
    "BCSPoolPros": {
        "handle": "@BCSPoolPros",
        "channel_id": None,
        "focus": "new tech training",
        "difficulty": "beginner"
    },
    "InyoPools": {
        "handle": "@InyoPools",
        "channel_id": None,
        "focus": "equipment guides",
        "difficulty": "beginner"
    },
    "RiverPools": {
        "handle": "@RiverPools",
        "channel_id": None,
        "focus": "fiberglass installation",
        "difficulty": "intermediate"
    },
    "Askthepoolguy": {
        "handle": "@Askthepoolguy",
        "channel_id": None,
        "focus": "construction and design",
        "difficulty": "intermediate"
    },
    "poolchasers": {
        "handle": "@poolchasers",
        "channel_id": None,
        "focus": "business growth",
        "difficulty": "intermediate"
    }
}


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


def get_transcript(video_id: str, languages: List[str] = ['en']) -> Optional[Dict[str, Any]]:
    """
    Fetch transcript for a video.
    Returns structured data with full text and timestamped segments.
    """
    try:
        # Initialize the API client
        api = YouTubeTranscriptApi()

        # List available transcripts
        transcript_list = api.list(video_id)

        # Try to get manually created transcript first, then auto-generated
        transcript = None
        try:
            transcript = transcript_list.find_manually_created_transcript(languages)
        except:
            try:
                transcript = transcript_list.find_generated_transcript(languages)
            except:
                pass

        if transcript:
            transcript_data = transcript.fetch()

            # Combine into full text
            full_text = ' '.join([entry['text'] for entry in transcript_data])

            return {
                "video_id": video_id,
                "language": transcript.language_code,
                "is_generated": transcript.is_generated,
                "full_text": full_text,
                "segments": transcript_data,
                "word_count": len(full_text.split()),
                "duration_seconds": transcript_data[-1]['start'] + transcript_data[-1]['duration'] if transcript_data else 0
            }
    except TranscriptsDisabled:
        print(f"  Transcripts disabled for video: {video_id}")
    except NoTranscriptFound:
        print(f"  No transcript found for video: {video_id}")
    except Exception as e:
        print(f"  Error fetching transcript for {video_id}: {e}")

    return None


def get_video_metadata(video_id: str) -> Optional[Dict[str, Any]]:
    """
    Get basic video metadata by scraping the watch page.
    Note: For production, use YouTube Data API for more reliable metadata.
    """
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            # Extract title from page
            soup = BeautifulSoup(response.text, 'html.parser')
            title_tag = soup.find('meta', property='og:title')
            description_tag = soup.find('meta', property='og:description')

            return {
                "title": title_tag['content'] if title_tag else "Unknown",
                "description": description_tag['content'] if description_tag else "",
                "url": url
            }
    except Exception as e:
        print(f"  Could not fetch metadata for {video_id}: {e}")

    return {"title": "Unknown", "description": "", "url": f"https://www.youtube.com/watch?v={video_id}"}


def get_channel_videos(channel_handle: str, max_videos: int = 50) -> List[str]:
    """
    Get video IDs from a channel.
    Note: This is a simplified scraper. For production, use YouTube Data API.
    """
    video_ids = []

    try:
        # Try to get videos from the channel's videos page
        url = f"https://www.youtube.com/{channel_handle}/videos"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code == 200:
            # Find video IDs in the page content
            video_id_pattern = r'"videoId":"([a-zA-Z0-9_-]{11})"'
            matches = re.findall(video_id_pattern, response.text)

            # Remove duplicates while preserving order
            seen = set()
            for vid in matches:
                if vid not in seen:
                    seen.add(vid)
                    video_ids.append(vid)
                    if len(video_ids) >= max_videos:
                        break

        print(f"  Found {len(video_ids)} videos for {channel_handle}")

    except Exception as e:
        print(f"  Error getting videos for {channel_handle}: {e}")

    return video_ids


def classify_topic(text: str, title: str = "") -> str:
    """
    Simple topic classification based on keywords.
    For production, use ML-based classification.
    """
    combined = (title + " " + text[:1000]).lower()

    topic_keywords = {
        "water_chemistry": ["ph", "chlorine", "alkalinity", "calcium", "cya", "stabilizer", "lsi", "balance", "chemical", "shock", "algae"],
        "equipment": ["pump", "filter", "heater", "motor", "valve", "skimmer", "cleaner", "robot", "variable speed", "cartridge", "sand", "de filter"],
        "troubleshooting": ["problem", "issue", "fix", "repair", "leak", "cloudy", "green", "algae bloom", "diagnose", "troubleshoot"],
        "maintenance": ["clean", "brush", "vacuum", "skim", "backwash", "maintenance", "routine", "weekly", "service"],
        "business": ["route", "customer", "pricing", "profit", "marketing", "growth", "employee", "business", "schedule"],
        "installation": ["install", "plumb", "construction", "build", "replace", "upgrade"],
        "safety": ["safety", "chemical handling", "ppe", "hazard", "osha"],
        "saltwater": ["salt", "saltwater", "salt cell", "chlorine generator", "swg"]
    }

    scores = {topic: 0 for topic in topic_keywords}
    for topic, keywords in topic_keywords.items():
        for keyword in keywords:
            if keyword in combined:
                scores[topic] += 1

    if max(scores.values()) > 0:
        return max(scores, key=scores.get)
    return "general"


def process_video(video_id: str, channel_info: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
    """Process a single video: get metadata and transcript."""
    print(f"  Processing video: {video_id}")

    # Get metadata
    metadata = get_video_metadata(video_id)

    # Get transcript
    transcript_data = get_transcript(video_id)

    if not transcript_data:
        return None

    # Classify topic
    topic = classify_topic(
        transcript_data['full_text'],
        metadata.get('title', '')
    )

    # Build structured record
    record = {
        "source": "youtube",
        "source_type": "video_transcript",
        "video_id": video_id,
        "url": metadata['url'],
        "title": metadata['title'],
        "description": metadata['description'],
        "content": transcript_data['full_text'],
        "segments": transcript_data['segments'],
        "topic": topic,
        "difficulty_level": channel_info.get('difficulty', 'intermediate') if channel_info else 'intermediate',
        "channel": channel_info.get('handle', 'unknown') if channel_info else 'unknown',
        "word_count": transcript_data['word_count'],
        "duration_seconds": transcript_data['duration_seconds'],
        "language": transcript_data['language'],
        "is_auto_generated": transcript_data['is_generated'],
        "extracted_at": datetime.now().isoformat(),
        "metadata": {
            "focus_area": channel_info.get('focus', 'general') if channel_info else 'general'
        }
    }

    return record


def save_record(record: Dict[str, Any], output_dir: Path = OUTPUT_DIR):
    """Save a single record to JSON file."""
    filename = f"{record['video_id']}.json"
    filepath = output_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

    print(f"  Saved: {filepath.name}")


def process_channel(channel_name: str, max_videos: int = 50, delay: float = 1.0):
    """Process all videos from a channel."""
    if channel_name not in POOL_CHANNELS:
        print(f"Unknown channel: {channel_name}")
        print(f"Available channels: {list(POOL_CHANNELS.keys())}")
        return

    channel_info = POOL_CHANNELS[channel_name]
    print(f"\nProcessing channel: {channel_name} ({channel_info['handle']})")

    # Get video IDs
    video_ids = get_channel_videos(channel_info['handle'], max_videos)

    if not video_ids:
        print(f"No videos found for {channel_name}")
        return

    # Process each video
    processed = 0
    failed = 0

    for video_id in video_ids:
        try:
            record = process_video(video_id, channel_info)
            if record:
                save_record(record)
                processed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  Error processing {video_id}: {e}")
            failed += 1

        # Rate limiting
        time.sleep(delay)

    print(f"\nChannel {channel_name}: Processed {processed}, Failed {failed}")


def process_video_url(url: str):
    """Process a single video from URL."""
    video_id = extract_video_id(url)
    if not video_id:
        print(f"Could not extract video ID from: {url}")
        return

    record = process_video(video_id)
    if record:
        save_record(record)
        print(f"Successfully processed: {record['title']}")


def main():
    parser = argparse.ArgumentParser(description='YouTube Transcript Extractor for Pool Service KB')
    parser.add_argument('--channel', type=str, help='Channel name to process (e.g., SwimUniversity)')
    parser.add_argument('--all-channels', action='store_true', help='Process all known pool channels')
    parser.add_argument('--video-url', type=str, help='Single video URL to process')
    parser.add_argument('--video-id', type=str, help='Single video ID to process')
    parser.add_argument('--max-videos', type=int, default=50, help='Max videos per channel (default: 50)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests in seconds')
    parser.add_argument('--list-channels', action='store_true', help='List available channels')

    args = parser.parse_args()

    if args.list_channels:
        print("Available channels:")
        for name, info in POOL_CHANNELS.items():
            print(f"  {name}: {info['handle']} - {info['focus']}")
        return

    if args.video_url:
        process_video_url(args.video_url)
    elif args.video_id:
        record = process_video(args.video_id)
        if record:
            save_record(record)
    elif args.channel:
        process_channel(args.channel, args.max_videos, args.delay)
    elif args.all_channels:
        for channel_name in POOL_CHANNELS:
            process_channel(channel_name, args.max_videos, args.delay)
            time.sleep(2)  # Extra delay between channels
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
