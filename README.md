# 🏊 Skimmer Assistant - Pool Pro Knowledge Base

A RAG (Retrieval-Augmented Generation) powered knowledge base assistant for pool service technicians. Built with Streamlit, ChromaDB, and OpenAI.

**Status:** POC (Proof of Concept) - Ready for team review
**Version:** 1.0.0
**Last Updated:** January 2025

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Developer Setup](#developer-setup)
- [Project Structure](#project-structure)
- [Knowledge Base](#knowledge-base)
- [Testing](#testing)
- [Deployment](#deployment)
- [Security Considerations](#security-considerations)
- [API Costs](#api-costs)
- [Contributing](#contributing)

## Features

- **23 Topic Guides** covering water chemistry, equipment, troubleshooting, CPO certification, and more
- **AI-Powered Q&A** using GPT-4o-mini with retrieval augmented generation
- **Photo Analysis** - Upload images of pool issues for AI diagnosis using GPT-4o Vision
- **Skimmer Branding** - Custom Perplexity-inspired UI with Skimmer brand colors
- **Source Citations** - Shows which knowledge base sections were used for each answer

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit UI                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Sidebar   │  │    Hero     │  │      Chat Interface      │ │
│  │  - API Key  │  │  - Upload   │  │  - Message History       │ │
│  │  - KB Load  │  │  - Quick    │  │  - Source Citations      │ │
│  │  - Photo    │  │    Actions  │  │                          │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Query Processing                            │
│                                                                  │
│  1. User asks question (text or with image)                     │
│  2. Question embedded via OpenAI text-embedding-3-small         │
│  3. ChromaDB returns top 5 similar chunks                       │
│  4. Chunks + Question sent to GPT-4o-mini (or GPT-4o for images)│
│  5. Response displayed with source citations                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                  │
│                                                                  │
│  ┌─────────────────────┐    ┌─────────────────────────────────┐│
│  │   topic_guides/     │───▶│        ChromaDB (in-memory)     ││
│  │   (23 .md files)    │    │   - 400+ embedded chunks        ││
│  │                     │    │   - Semantic search             ││
│  └─────────────────────┘    └─────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Option 1: Streamlit Cloud (Recommended for Teams)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app" and connect your GitHub repo
4. Set the main file path: `skimmer_assistant/app.py`
5. Add your OpenAI API key in **Settings > Secrets**:
   ```toml
   OPENAI_API_KEY = "sk-..."
   ```
6. Click "Deploy" - your team can access via the generated URL!

### Option 2: Local Development

```bash
# Clone the repository
git clone https://github.com/nidhi-singh-product/skimmer-assistant.git
cd skimmer-assistant

# Install dependencies
pip install -r requirements.txt

# Set your API key (choose one method)
export OPENAI_API_KEY="sk-..."  # Environment variable
# OR create .streamlit/secrets.toml with: OPENAI_API_KEY = "sk-..."

# Run the app
cd skimmer_assistant
streamlit run app.py
```

## Developer Setup

### Prerequisites

- Python 3.9+
- OpenAI API key with access to:
  - `text-embedding-3-small` (embeddings)
  - `gpt-4o-mini` (chat)
  - `gpt-4o` (vision - optional, for image analysis)

### Installation

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies for testing
pip install pytest pytest-cov
```

### Configuration

The app looks for the OpenAI API key in this order:
1. Streamlit secrets (`st.secrets['OPENAI_API_KEY']`)
2. Environment variable (`OPENAI_API_KEY`)
3. User input in sidebar (for demos)

For local development, create `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "sk-your-key-here"
```

**Important:** Never commit API keys to version control!

### Code Quality

The codebase follows these conventions:
- **Type hints** on all function signatures
- **Docstrings** on all public functions
- **Section comments** for code organization
- **Constants** extracted to top of file for easy modification

## Project Structure

```
KBPooltech/
├── skimmer_assistant/
│   ├── app.py              # Main Streamlit application (fully documented)
│   └── test_app.py         # Unit tests (pytest)
├── topic_guides/           # Knowledge base (23 markdown files)
│   ├── 01_water_chemistry.md
│   ├── 02_equipment_pumps.md
│   ├── ...
│   └── 23_pool_care_cheatsheet.md
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

### Key Files

| File | Purpose |
|------|---------|
| `app.py` | Main application - UI, RAG pipeline, OpenAI integration |
| `test_app.py` | Unit tests for core functions |
| `topic_guides/*.md` | Knowledge base content (edit to update KB) |
| `requirements.txt` | Pin versions for reproducible builds |

## Knowledge Base

### Topics Covered (23 Guides)

| # | Topic | Key Content |
|---|-------|-------------|
| 1 | Water Chemistry | pH, chlorine, alkalinity, calcium hardness |
| 2 | Equipment - Pumps | Single speed, variable speed, troubleshooting |
| 3 | Equipment - Filters | Sand, cartridge, DE filters |
| 4 | Equipment - Heaters | Gas, heat pump, solar heating |
| 5 | Saltwater Pools | Salt cells, maintenance, conversion |
| 6 | Troubleshooting | Common problems and diagnostic trees |
| 7 | Cleaning & Maintenance | Brushing, vacuuming, routines |
| 8 | Business Operations | Scheduling, pricing, growth |
| 9 | Safety & Liability | Chemical handling, insurance |
| 10 | ADA Compliance | Pool accessibility requirements |
| 11 | Emergency Response | Accidents, contamination protocols |
| 12 | Customer Communication | Explaining issues to homeowners |
| 13 | Installation Procedures | Hydraulic efficiency, bonding |
| 14 | Water Testing | Taylor K2005, test procedures |
| 15 | Manual Vacuuming | Techniques, filter vs waste |
| 16 | Service Documentation | Report writing, photo standards |
| 17 | Automation | Pentair IntelliConnect, smart systems |
| 18 | CPO Certification | Regulatory compliance, renewal |
| 19 | Leak Detection | Bucket test, dye test, pressure testing |
| 20 | Heater Safety | High limit switches, pressure switches |
| 21 | Saltwater Maintenance | Cell cleaning, chemistry specifics |
| 22 | Technician Training | Onboarding, skill progression |
| 23 | Pool Care Cheat Sheet | Quick reference for common tasks |

### Adding New Content

1. Create a new markdown file in `topic_guides/`:
   ```
   topic_guides/24_new_topic.md
   ```

2. Use H2 headers (`## `) to create logical sections (these become chunks):
   ```markdown
   # New Topic Guide

   ## Section One
   Content here becomes one chunk...

   ## Section Two
   Content here becomes another chunk...
   ```

3. Reload the knowledge base in the app (sidebar button)

### Chunking Strategy

- Files are split on `## ` (H2 headers)
- Each chunk includes its header for context
- Metadata tracks: source file, topic name, section header
- Average chunk size: ~200-500 tokens

## Testing

### Running Tests

```bash
# Run all tests
pytest skimmer_assistant/test_app.py -v

# Run with coverage report
pytest skimmer_assistant/test_app.py --cov=skimmer_assistant --cov-report=html

# Run specific test class
pytest skimmer_assistant/test_app.py::TestChunking -v
```

### Test Coverage

Tests cover:
- API key retrieval logic
- Markdown chunking and parsing
- Topic name extraction from filenames
- ChromaDB operations (mocked)
- Source deduplication
- File discovery

### Manual Testing Checklist

Before deploying changes:
- [ ] App loads without errors
- [ ] Knowledge base loads successfully
- [ ] Text queries return relevant answers
- [ ] Image upload works
- [ ] Quick action buttons function
- [ ] Sources display correctly
- [ ] Sidebar controls work

## Deployment

### Streamlit Cloud (Production)

1. Push changes to GitHub main branch
2. Streamlit Cloud auto-deploys on push
3. Monitor logs at share.streamlit.io

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for embeddings and chat |

### Production Considerations

For production deployment beyond POC:

1. **Persistent Vector DB**: Replace in-memory ChromaDB with persistent storage
   ```python
   client = chromadb.PersistentClient(path="./chroma_db")
   ```

2. **Caching**: Add response caching for common queries

3. **Rate Limiting**: Implement rate limiting for API cost control

4. **Monitoring**: Add logging and error tracking (e.g., Sentry)

5. **Authentication**: Add user authentication if deploying publicly

## Security Considerations

### API Keys
- Never commit API keys to version control
- Use Streamlit secrets or environment variables
- Rotate keys if exposed

### Data Privacy
- No user data is stored permanently
- Chat history exists only in session state
- Images are processed but not saved

### Dependencies
- Review `requirements.txt` for known vulnerabilities
- Keep dependencies updated

## API Costs

Approximate costs per 1,000 queries:

| Component | Cost |
|-----------|------|
| Embeddings (text-embedding-3-small) | ~$0.02 |
| Chat responses (GPT-4o-mini) | ~$0.15 |
| Image analysis (GPT-4o) | ~$0.50 per image |

**Monthly estimate** (1,000 queries, 100 images): ~$67

## Contributing

### Code Style
- Use type hints
- Write docstrings for public functions
- Keep functions focused and testable
- Comment complex logic

### Pull Request Process
1. Create feature branch from `main`
2. Make changes with tests
3. Run test suite
4. Update README if needed
5. Submit PR with description

### Commit Messages
Follow conventional commits:
```
feat: Add new troubleshooting guide
fix: Correct pH range in water chemistry
docs: Update deployment instructions
test: Add chunking edge case tests
```

---

## Contact

**Product Owner:** Nidhi Singh
**Email:** nidhi@getskimmer.com
**Company:** Skimmer Pro

---

Built for Skimmer Pro 🏊 | Pool Service Software
