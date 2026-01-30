#!/usr/bin/env python3
"""
Data Processor for Pool Service Knowledge Base
==============================================
Combines, cleans, and structures all extracted data for use in RAG/LLM training.

Features:
- Combines data from all sources (YouTube, Reddit, Podcasts, Articles)
- Cleans and normalizes text
- Chunks content for optimal embedding
- Creates unified dataset in multiple formats (JSON, JSONL, CSV)
- Generates statistics and quality reports

Usage:
    python data_processor.py --process-all
    python data_processor.py --stats
    python data_processor.py --export jsonl
    python data_processor.py --chunk --chunk-size 512
"""

import os
import json
import re
import csv
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Generator
from collections import defaultdict
import hashlib

try:
    from tqdm import tqdm
except ImportError:
    print("Installing tqdm...")
    os.system("pip install tqdm --break-system-packages")
    from tqdm import tqdm


# Configuration
BASE_DIR = Path(__file__).parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "output"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Topic taxonomy for pool service knowledge base
TOPIC_TAXONOMY = {
    "water_chemistry": {
        "parent": None,
        "keywords": ["ph", "chlorine", "alkalinity", "calcium hardness", "cya", "cyanuric acid",
                    "stabilizer", "lsi", "saturation index", "balanced water", "chemical"],
        "subtopics": ["balancing", "testing", "dosing", "algae_treatment"]
    },
    "equipment": {
        "parent": None,
        "keywords": ["pump", "filter", "heater", "motor", "valve", "plumbing"],
        "subtopics": ["pumps", "filters", "heaters", "cleaners", "automation"]
    },
    "maintenance": {
        "parent": None,
        "keywords": ["clean", "brush", "vacuum", "skim", "backwash", "routine", "weekly"],
        "subtopics": ["daily_routine", "weekly_routine", "seasonal"]
    },
    "troubleshooting": {
        "parent": None,
        "keywords": ["problem", "issue", "fix", "repair", "diagnose", "not working"],
        "subtopics": ["water_problems", "equipment_problems", "leaks"]
    },
    "business": {
        "parent": None,
        "keywords": ["route", "customer", "pricing", "profit", "marketing", "growth", "employee"],
        "subtopics": ["operations", "marketing", "finance", "hiring"]
    },
    "safety": {
        "parent": None,
        "keywords": ["safety", "chemical handling", "ppe", "hazard", "osha"],
        "subtopics": ["chemical_safety", "electrical", "drowning_prevention"]
    }
}

# Difficulty level criteria
DIFFICULTY_CRITERIA = {
    "beginner": {
        "max_word_count": 2000,
        "keywords": ["basic", "beginner", "introduction", "what is", "how to", "first time", "new pool owner"],
        "complexity_indicators": []
    },
    "intermediate": {
        "min_word_count": 500,
        "keywords": ["troubleshoot", "diagnose", "adjust", "optimize", "balance"],
        "complexity_indicators": ["ppm", "testing", "adjusting"]
    },
    "advanced": {
        "min_word_count": 1000,
        "keywords": ["lsi calculation", "hydraulics", "plumbing", "advanced", "commercial", "complex"],
        "complexity_indicators": ["lsi", "gpm", "tdh", "head pressure", "turnover rate"]
    }
}


def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    if not text:
        return ""

    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s.,!?;:\'\"-]', '', text)

    # Remove URLs
    text = re.sub(r'http[s]?://\S+', '', text)

    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")

    return text.strip()


def calculate_content_hash(content: str) -> str:
    """Generate a hash for deduplication."""
    normalized = clean_text(content.lower())[:1000]
    return hashlib.md5(normalized.encode()).hexdigest()


def classify_topic_enhanced(text: str, title: str = "") -> Dict[str, Any]:
    """
    Enhanced topic classification with confidence scores.
    Returns primary topic, subtopics, and confidence.
    """
    combined = (title + " " + text[:3000]).lower()

    scores = {}
    for topic, info in TOPIC_TAXONOMY.items():
        score = sum(1 for kw in info['keywords'] if kw in combined)
        if score > 0:
            scores[topic] = score

    if not scores:
        return {"primary": "general", "confidence": 0.0, "all_topics": []}

    # Sort by score
    sorted_topics = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    max_score = sorted_topics[0][1]

    return {
        "primary": sorted_topics[0][0],
        "confidence": min(max_score / 5, 1.0),  # Normalize to 0-1
        "all_topics": [t[0] for t in sorted_topics[:3]]
    }


def assess_difficulty(text: str, metadata: Dict = None) -> str:
    """Assess content difficulty level."""
    text_lower = text.lower()
    word_count = len(text.split())

    # Count complexity indicators
    advanced_count = sum(1 for kw in DIFFICULTY_CRITERIA['advanced']['keywords']
                        if kw in text_lower)
    advanced_count += sum(1 for ind in DIFFICULTY_CRITERIA['advanced']['complexity_indicators']
                         if ind in text_lower)

    beginner_count = sum(1 for kw in DIFFICULTY_CRITERIA['beginner']['keywords']
                        if kw in text_lower)

    if advanced_count >= 3 or word_count > 3000:
        return "advanced"
    elif beginner_count >= 2 or word_count < 500:
        return "beginner"
    return "intermediate"


def load_raw_records(source_type: str) -> Generator[Dict[str, Any], None, None]:
    """Load all raw records from a specific source type."""
    source_dir = RAW_DATA_DIR / source_type

    if not source_dir.exists():
        print(f"No data found for source: {source_type}")
        return

    for json_file in source_dir.glob("*.json"):
        if json_file.name.startswith("_"):
            continue  # Skip meta files

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                yield json.load(f)
        except Exception as e:
            print(f"Error loading {json_file}: {e}")


def process_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a single record into the unified format.

    Output format: {
        source: str,
        source_type: str,
        content: str,
        topic: str,
        difficulty_level: str,
        title: str,
        url: str,
        word_count: int,
        content_hash: str,
        metadata: dict
    }
    """
    content = clean_text(record.get('content', ''))
    title = record.get('title', '')

    # Enhanced topic classification
    topic_info = classify_topic_enhanced(content, title)

    # Assess difficulty
    difficulty = record.get('difficulty_level') or assess_difficulty(content)

    processed = {
        "id": record.get('video_id') or record.get('post_id') or record.get('episode_id') or calculate_content_hash(content)[:12],
        "source": record.get('source', 'unknown'),
        "source_type": record.get('source_type', 'unknown'),
        "content": content,
        "topic": topic_info['primary'],
        "topic_confidence": topic_info['confidence'],
        "all_topics": topic_info['all_topics'],
        "difficulty_level": difficulty,
        "title": title,
        "url": record.get('url', ''),
        "word_count": len(content.split()),
        "content_hash": calculate_content_hash(content),
        "created_at": record.get('created_utc') or record.get('published') or record.get('extracted_at'),
        "extracted_at": record.get('extracted_at', datetime.now().isoformat()),
        "metadata": {
            "channel": record.get('channel'),
            "subreddit": record.get('subreddit'),
            "podcast_name": record.get('podcast_name'),
            "score": record.get('score'),
            "duration_seconds": record.get('duration_seconds'),
            "is_auto_generated": record.get('is_auto_generated')
        }
    }

    # Clean up None values in metadata
    processed['metadata'] = {k: v for k, v in processed['metadata'].items() if v is not None}

    return processed


def chunk_content(text: str, chunk_size: int = 512, overlap: int = 50) -> List[Dict[str, Any]]:
    """
    Split content into chunks for embedding.

    Args:
        text: The text to chunk
        chunk_size: Target size in words
        overlap: Number of words to overlap between chunks

    Returns:
        List of chunk dictionaries with text and position info
    """
    words = text.split()

    if len(words) <= chunk_size:
        return [{"text": text, "chunk_index": 0, "total_chunks": 1}]

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]

        # Try to end at a sentence boundary
        chunk_text = ' '.join(chunk_words)
        if end < len(words):
            # Look for sentence ending
            last_period = chunk_text.rfind('.')
            if last_period > len(chunk_text) * 0.7:  # Don't cut too short
                chunk_text = chunk_text[:last_period + 1]

        chunks.append({
            "text": chunk_text,
            "chunk_index": len(chunks),
            "start_word": start,
            "end_word": min(end, len(words))
        })

        start = end - overlap

    # Update total chunks
    for chunk in chunks:
        chunk['total_chunks'] = len(chunks)

    return chunks


def process_all_sources() -> List[Dict[str, Any]]:
    """Process all raw data from all sources."""
    all_records = []
    seen_hashes = set()
    source_counts = defaultdict(int)

    sources = ['youtube', 'reddit', 'podcasts', 'articles']

    for source in sources:
        print(f"\nProcessing {source}...")

        for record in tqdm(list(load_raw_records(source)), desc=source):
            processed = process_record(record)

            # Deduplication
            if processed['content_hash'] in seen_hashes:
                continue

            seen_hashes.add(processed['content_hash'])
            all_records.append(processed)
            source_counts[source] += 1

    print(f"\nProcessed records by source:")
    for source, count in source_counts.items():
        print(f"  {source}: {count}")

    print(f"\nTotal unique records: {len(all_records)}")

    return all_records


def generate_statistics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate statistics about the processed dataset."""
    stats = {
        "total_records": len(records),
        "total_words": sum(r['word_count'] for r in records),
        "by_source": defaultdict(int),
        "by_topic": defaultdict(int),
        "by_difficulty": defaultdict(int),
        "avg_word_count": 0,
        "word_count_distribution": {
            "under_500": 0,
            "500_to_1000": 0,
            "1000_to_2000": 0,
            "over_2000": 0
        }
    }

    for record in records:
        stats['by_source'][record['source']] += 1
        stats['by_topic'][record['topic']] += 1
        stats['by_difficulty'][record['difficulty_level']] += 1

        wc = record['word_count']
        if wc < 500:
            stats['word_count_distribution']['under_500'] += 1
        elif wc < 1000:
            stats['word_count_distribution']['500_to_1000'] += 1
        elif wc < 2000:
            stats['word_count_distribution']['1000_to_2000'] += 1
        else:
            stats['word_count_distribution']['over_2000'] += 1

    if records:
        stats['avg_word_count'] = stats['total_words'] // len(records)

    # Convert defaultdicts to regular dicts for JSON serialization
    stats['by_source'] = dict(stats['by_source'])
    stats['by_topic'] = dict(stats['by_topic'])
    stats['by_difficulty'] = dict(stats['by_difficulty'])

    return stats


def export_dataset(records: List[Dict[str, Any]], format: str = 'json',
                  output_path: Path = None, chunked: bool = False, chunk_size: int = 512):
    """
    Export the dataset in various formats.

    Formats:
    - json: Single JSON file with all records
    - jsonl: JSON Lines format (one record per line) - good for streaming
    - csv: CSV format with main fields
    - chunks: Chunked format for embedding
    """
    if output_path is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = OUTPUT_DIR / f"pool_kb_dataset_{timestamp}"

    if format == 'json':
        filepath = output_path.with_suffix('.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        print(f"Exported {len(records)} records to {filepath}")

    elif format == 'jsonl':
        filepath = output_path.with_suffix('.jsonl')
        with open(filepath, 'w', encoding='utf-8') as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        print(f"Exported {len(records)} records to {filepath}")

    elif format == 'csv':
        filepath = output_path.with_suffix('.csv')
        fields = ['id', 'source', 'topic', 'difficulty_level', 'title', 'url', 'word_count', 'content']
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
            writer.writeheader()
            for record in records:
                writer.writerow(record)
        print(f"Exported {len(records)} records to {filepath}")

    elif format == 'chunks':
        # Export as chunked format for RAG
        filepath = output_path.with_suffix('.chunks.jsonl')
        chunk_count = 0
        with open(filepath, 'w', encoding='utf-8') as f:
            for record in records:
                chunks = chunk_content(record['content'], chunk_size)
                for chunk in chunks:
                    chunk_record = {
                        "id": f"{record['id']}_chunk{chunk['chunk_index']}",
                        "parent_id": record['id'],
                        "source": record['source'],
                        "topic": record['topic'],
                        "difficulty_level": record['difficulty_level'],
                        "title": record['title'],
                        "text": chunk['text'],
                        "chunk_index": chunk['chunk_index'],
                        "total_chunks": chunk['total_chunks'],
                        "url": record['url']
                    }
                    f.write(json.dumps(chunk_record, ensure_ascii=False) + '\n')
                    chunk_count += 1
        print(f"Exported {chunk_count} chunks from {len(records)} records to {filepath}")

    return filepath


def print_statistics(stats: Dict[str, Any]):
    """Pretty print statistics."""
    print("\n" + "=" * 60)
    print("POOL SERVICE KNOWLEDGE BASE - DATASET STATISTICS")
    print("=" * 60)

    print(f"\nTotal Records: {stats['total_records']:,}")
    print(f"Total Words: {stats['total_words']:,}")
    print(f"Average Words per Record: {stats['avg_word_count']:,}")

    print("\nBy Source:")
    for source, count in sorted(stats['by_source'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {source}: {count:,}")

    print("\nBy Topic:")
    for topic, count in sorted(stats['by_topic'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {topic}: {count:,}")

    print("\nBy Difficulty Level:")
    for level, count in sorted(stats['by_difficulty'].items()):
        print(f"  {level}: {count:,}")

    print("\nWord Count Distribution:")
    for range_name, count in stats['word_count_distribution'].items():
        print(f"  {range_name.replace('_', ' ')}: {count:,}")

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Data Processor for Pool Service Knowledge Base')
    parser.add_argument('--process-all', action='store_true', help='Process all raw data sources')
    parser.add_argument('--stats', action='store_true', help='Show statistics for processed data')
    parser.add_argument('--export', type=str, choices=['json', 'jsonl', 'csv', 'chunks'],
                       help='Export format')
    parser.add_argument('--chunk-size', type=int, default=512, help='Chunk size in words')
    parser.add_argument('--output', type=str, help='Output file path')

    args = parser.parse_args()

    if args.process_all:
        records = process_all_sources()

        # Save processed data
        processed_file = PROCESSED_DIR / "all_records.json"
        with open(processed_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        print(f"\nSaved processed data to {processed_file}")

        # Generate and save statistics
        stats = generate_statistics(records)
        stats_file = PROCESSED_DIR / "statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)

        print_statistics(stats)

    elif args.stats:
        # Load existing processed data
        processed_file = PROCESSED_DIR / "all_records.json"
        if not processed_file.exists():
            print("No processed data found. Run --process-all first.")
            return

        with open(processed_file, 'r', encoding='utf-8') as f:
            records = json.load(f)

        stats = generate_statistics(records)
        print_statistics(stats)

    elif args.export:
        # Load existing processed data
        processed_file = PROCESSED_DIR / "all_records.json"
        if not processed_file.exists():
            print("No processed data found. Run --process-all first.")
            return

        with open(processed_file, 'r', encoding='utf-8') as f:
            records = json.load(f)

        output_path = Path(args.output) if args.output else None
        export_dataset(records, args.export, output_path,
                      chunked=(args.export == 'chunks'),
                      chunk_size=args.chunk_size)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
