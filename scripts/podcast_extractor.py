#!/usr/bin/env python3
"""
Podcast Transcript Extractor for Pool Service Knowledge Base
=============================================================
Downloads and transcribes podcast episodes using AssemblyAI.

SETUP REQUIRED:
1. Sign up for AssemblyAI at https://www.assemblyai.com (free tier: 100 hours)
2. Get your API key from the dashboard
3. Set environment variable: ASSEMBLYAI_API_KEY=your_api_key

Usage:
    python podcast_extractor.py --rss "https://feed.url/rss" --limit 5
    python podcast_extractor.py --audio-url "https://example.com/episode.mp3"
    python podcast_extractor.py --audio-file "/path/to/episode.mp3"
    python podcast_extractor.py --list-feeds
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import time
import hashlib

try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system("pip install requests --break-system-packages")
    import requests

try:
    import feedparser
except ImportError:
    print("Installing feedparser...")
    os.system("pip install feedparser --break-system-packages")
    import feedparser

try:
    import assemblyai as aai
except ImportError:
    print("Installing assemblyai...")
    os.system("pip install assemblyai --break-system-packages")
    import assemblyai as aai

try:
    from dotenv import load_dotenv
except ImportError:
    print("Installing python-dotenv...")
    os.system("pip install python-dotenv --break-system-packages")
    from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Configuration
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "raw" / "podcasts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

AUDIO_CACHE_DIR = Path(__file__).parent.parent / "data" / "raw" / "podcasts" / "_audio_cache"
AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Pool service podcast RSS feeds
POOL_PODCAST_FEEDS = {
    "pool_guy_podcast": {
        "name": "The Pool Guy Podcast Show",
        "host": "David Van Brunt",
        "rss": "https://the-pool-guy-podcast-show.onpodium.com/rss",  # May need verification
        "focus": "service tactics, water chemistry",
        "difficulty": "intermediate"
    },
    "pool_chasers": {
        "name": "Pool Chasers Podcast",
        "hosts": "Greg Villafana & Justin Buoy",
        "rss": None,  # Need to find RSS feed
        "youtube": "https://www.youtube.com/@poolchasers",
        "focus": "business growth, marketing",
        "difficulty": "intermediate"
    },
    "rule_your_pool": {
        "name": "Rule Your Pool (Orenda)",
        "hosts": "Eric Knight & Jared Brimhall",
        "rss": None,  # Need to find RSS feed
        "focus": "proactive chemistry, LSI",
        "difficulty": "advanced"
    },
    "pool_magazine": {
        "name": "Pool Magazine Podcast",
        "host": "Joe Trusty",
        "rss": None,  # Need to find from poolmagazine.com
        "focus": "industry trends, innovation",
        "difficulty": "intermediate"
    }
}


def get_assemblyai_client():
    """Initialize AssemblyAI client."""
    api_key = os.getenv('ASSEMBLYAI_API_KEY')

    if not api_key:
        print("=" * 60)
        print("ASSEMBLYAI API KEY REQUIRED")
        print("=" * 60)
        print("\nTo transcribe podcasts, you need an AssemblyAI API key:")
        print("1. Sign up at https://www.assemblyai.com (free tier: 100 hours)")
        print("2. Get your API key from the dashboard")
        print("3. Set it as an environment variable:")
        print("   export ASSEMBLYAI_API_KEY=your_api_key")
        print("\nOr create a .env file in the scripts folder with:")
        print("   ASSEMBLYAI_API_KEY=your_api_key")
        print("=" * 60)
        return None

    aai.settings.api_key = api_key
    return aai.Transcriber()


def parse_podcast_feed(rss_url: str) -> List[Dict[str, Any]]:
    """Parse a podcast RSS feed and extract episode information."""
    print(f"Parsing RSS feed: {rss_url}")

    try:
        feed = feedparser.parse(rss_url)

        if feed.bozo:
            print(f"Warning: Feed parsing issues - {feed.bozo_exception}")

        episodes = []
        for entry in feed.entries:
            # Find audio enclosure
            audio_url = None
            for link in entry.get('links', []):
                if link.get('type', '').startswith('audio/'):
                    audio_url = link.get('href')
                    break

            # Try enclosures if no audio link found
            if not audio_url:
                for enclosure in entry.get('enclosures', []):
                    if enclosure.get('type', '').startswith('audio/'):
                        audio_url = enclosure.get('href')
                        break

            if audio_url:
                episodes.append({
                    "title": entry.get('title', 'Unknown'),
                    "audio_url": audio_url,
                    "published": entry.get('published', ''),
                    "description": entry.get('summary', entry.get('description', '')),
                    "duration": entry.get('itunes_duration', ''),
                    "episode_id": entry.get('id', hashlib.md5(audio_url.encode()).hexdigest()[:12])
                })

        print(f"Found {len(episodes)} episodes with audio")
        return episodes

    except Exception as e:
        print(f"Error parsing feed: {e}")
        return []


def download_audio(audio_url: str, episode_id: str) -> Optional[Path]:
    """Download audio file to cache directory."""
    # Determine file extension
    ext = '.mp3'
    if '.m4a' in audio_url:
        ext = '.m4a'
    elif '.wav' in audio_url:
        ext = '.wav'

    cache_path = AUDIO_CACHE_DIR / f"{episode_id}{ext}"

    if cache_path.exists():
        print(f"  Using cached audio: {cache_path.name}")
        return cache_path

    print(f"  Downloading audio...")
    try:
        response = requests.get(audio_url, stream=True, timeout=60)
        response.raise_for_status()

        with open(cache_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"  Downloaded: {cache_path.name}")
        return cache_path

    except Exception as e:
        print(f"  Error downloading audio: {e}")
        return None


def transcribe_audio(transcriber: aai.Transcriber, audio_source: str) -> Optional[Dict[str, Any]]:
    """
    Transcribe an audio file or URL using AssemblyAI.

    Args:
        transcriber: AssemblyAI Transcriber instance
        audio_source: Path to audio file or URL
    """
    print(f"  Transcribing audio...")

    try:
        # Configure transcription
        config = aai.TranscriptionConfig(
            speaker_labels=True,  # Identify different speakers
            auto_chapters=True,   # Auto-generate chapters
            entity_detection=True # Detect key entities
        )

        # Submit for transcription
        transcript = transcriber.transcribe(audio_source, config=config)

        if transcript.status == aai.TranscriptStatus.error:
            print(f"  Transcription error: {transcript.error}")
            return None

        result = {
            "text": transcript.text,
            "confidence": transcript.confidence,
            "duration_seconds": transcript.audio_duration,
            "word_count": len(transcript.text.split()) if transcript.text else 0,
            "words": [
                {
                    "text": w.text,
                    "start": w.start,
                    "end": w.end,
                    "confidence": w.confidence,
                    "speaker": w.speaker
                }
                for w in (transcript.words or [])
            ],
            "chapters": [
                {
                    "headline": c.headline,
                    "summary": c.summary,
                    "start": c.start,
                    "end": c.end
                }
                for c in (transcript.chapters or [])
            ],
            "speakers": list(set(w.speaker for w in (transcript.words or []) if w.speaker))
        }

        print(f"  Transcribed: {result['word_count']} words, {len(result['speakers'])} speakers")
        return result

    except Exception as e:
        print(f"  Error transcribing: {e}")
        return None


def classify_topic(text: str, title: str = "") -> str:
    """Classify the topic based on content keywords."""
    combined = (title + " " + text[:3000]).lower()

    topic_keywords = {
        "water_chemistry": ["ph", "chlorine", "alkalinity", "calcium", "cya", "lsi", "balance", "chemical"],
        "equipment": ["pump", "filter", "heater", "motor", "valve", "skimmer", "cleaner"],
        "troubleshooting": ["problem", "issue", "fix", "repair", "leak", "cloudy", "green"],
        "business": ["route", "customer", "pricing", "profit", "marketing", "growth", "business"],
        "maintenance": ["clean", "brush", "vacuum", "maintenance", "routine", "service"],
        "industry": ["trend", "innovation", "technology", "market", "future"]
    }

    scores = {topic: 0 for topic in topic_keywords}
    for topic, keywords in topic_keywords.items():
        for keyword in keywords:
            if keyword in combined:
                scores[topic] += 1

    if max(scores.values()) > 0:
        return max(scores, key=scores.get)
    return "general"


def process_episode(transcriber: aai.Transcriber, episode: Dict[str, Any],
                    podcast_info: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
    """Process a single podcast episode."""
    print(f"\nProcessing: {episode['title'][:60]}...")

    # Get audio (download if needed, or use URL directly)
    audio_source = episode['audio_url']

    # AssemblyAI can handle URLs directly, but downloading gives us a cache
    # For large-scale processing, you might want to download first

    # Transcribe
    transcript_data = transcribe_audio(transcriber, audio_source)
    if not transcript_data:
        return None

    # Build record
    record = {
        "source": "podcast",
        "source_type": "podcast_transcript",
        "episode_id": episode['episode_id'],
        "title": episode['title'],
        "description": episode['description'],
        "audio_url": episode['audio_url'],
        "published": episode['published'],
        "content": transcript_data['text'],
        "topic": classify_topic(transcript_data['text'], episode['title']),
        "difficulty_level": podcast_info.get('difficulty', 'intermediate') if podcast_info else 'intermediate',
        "podcast_name": podcast_info.get('name', 'Unknown') if podcast_info else 'Unknown',
        "host": podcast_info.get('host', podcast_info.get('hosts', 'Unknown')) if podcast_info else 'Unknown',
        "word_count": transcript_data['word_count'],
        "duration_seconds": transcript_data['duration_seconds'],
        "confidence": transcript_data['confidence'],
        "speakers": transcript_data['speakers'],
        "chapters": transcript_data['chapters'],
        "extracted_at": datetime.now().isoformat(),
        "metadata": {
            "focus_area": podcast_info.get('focus', 'general') if podcast_info else 'general',
            "transcription_words": transcript_data['words'][:100]  # First 100 words with timestamps
        }
    }

    return record


def save_record(record: Dict[str, Any], output_dir: Path = OUTPUT_DIR):
    """Save a single record to JSON file."""
    filename = f"{record['episode_id']}.json"
    filepath = output_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

    print(f"  Saved: {filepath.name}")


def process_feed(transcriber: aai.Transcriber, feed_key: str, limit: int = 5):
    """Process episodes from a podcast feed."""
    if feed_key not in POOL_PODCAST_FEEDS:
        print(f"Unknown feed: {feed_key}")
        print(f"Available feeds: {list(POOL_PODCAST_FEEDS.keys())}")
        return

    feed_info = POOL_PODCAST_FEEDS[feed_key]

    if not feed_info.get('rss'):
        print(f"RSS feed URL not available for {feed_info['name']}")
        print("You may need to find the RSS feed URL manually or use YouTube for this podcast.")
        return

    print(f"\nProcessing podcast: {feed_info['name']}")

    episodes = parse_podcast_feed(feed_info['rss'])
    if not episodes:
        return

    processed = 0
    for episode in episodes[:limit]:
        try:
            record = process_episode(transcriber, episode, feed_info)
            if record:
                save_record(record)
                processed += 1
        except Exception as e:
            print(f"  Error processing episode: {e}")

        # Rate limiting for API
        time.sleep(1)

    print(f"\nProcessed {processed} episodes from {feed_info['name']}")


def process_audio_url(transcriber: aai.Transcriber, audio_url: str, title: str = "Unknown Episode"):
    """Process a single audio URL."""
    episode = {
        "title": title,
        "audio_url": audio_url,
        "description": "",
        "published": "",
        "episode_id": hashlib.md5(audio_url.encode()).hexdigest()[:12]
    }

    record = process_episode(transcriber, episode)
    if record:
        save_record(record)


def main():
    parser = argparse.ArgumentParser(description='Podcast Transcript Extractor for Pool Service KB')
    parser.add_argument('--feed', type=str, help='Podcast feed key to process')
    parser.add_argument('--rss', type=str, help='RSS feed URL to process')
    parser.add_argument('--audio-url', type=str, help='Single audio URL to transcribe')
    parser.add_argument('--audio-file', type=str, help='Local audio file to transcribe')
    parser.add_argument('--title', type=str, default='Unknown Episode', help='Episode title (for single files)')
    parser.add_argument('--limit', type=int, default=5, help='Max episodes per feed')
    parser.add_argument('--list-feeds', action='store_true', help='List known podcast feeds')

    args = parser.parse_args()

    if args.list_feeds:
        print("Known pool service podcasts:")
        for key, info in POOL_PODCAST_FEEDS.items():
            rss_status = "RSS available" if info.get('rss') else "RSS not configured"
            print(f"  {key}: {info['name']} ({rss_status})")
        return

    # Initialize AssemblyAI
    transcriber = get_assemblyai_client()
    if not transcriber:
        return

    if args.audio_url:
        process_audio_url(transcriber, args.audio_url, args.title)
    elif args.audio_file:
        process_audio_url(transcriber, args.audio_file, args.title)
    elif args.rss:
        # Custom RSS feed
        episodes = parse_podcast_feed(args.rss)
        for episode in episodes[:args.limit]:
            record = process_episode(transcriber, episode)
            if record:
                save_record(record)
            time.sleep(1)
    elif args.feed:
        process_feed(transcriber, args.feed, args.limit)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
