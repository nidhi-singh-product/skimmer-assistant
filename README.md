# 🏊 Skimmer Assistant - Pool Pro Knowledge Base

A RAG-powered knowledge base assistant for pool service technicians, built with Streamlit, ChromaDB, and OpenAI.

## Features

- **17 Topic Guides** covering water chemistry, equipment, troubleshooting, and more
- **AI-Powered Q&A** using GPT-4o-mini with retrieval augmented generation
- **Photo Analysis** - Upload images of pool issues for AI diagnosis
- **Skimmer Branding** - Custom UI with Skimmer colors

## Quick Start

### Option 1: Streamlit Cloud (Recommended for Teams)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app" and connect your GitHub repo
4. Set the main file path: `skimmer_assistant/app.py`
5. Add your OpenAI API key in **Advanced Settings > Secrets**:
   ```toml
   OPENAI_API_KEY = "sk-..."
   ```
6. Click "Deploy" - your team can access via the generated URL!

### Option 2: Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   cd skimmer_assistant
   streamlit run app.py
   ```
3. Enter your OpenAI API key in the sidebar

## Project Structure

```
KBPooltech/
├── skimmer_assistant/
│   └── app.py              # Main Streamlit app
├── topic_guides/           # Knowledge base (17 markdown files)
│   ├── 01_water_chemistry.md
│   ├── 02_equipment_pumps.md
│   ├── ...
│   └── 17_variable_speed_pumps.md
├── requirements.txt
└── README.md
```

## Knowledge Base Topics

| # | Topic | Description |
|---|-------|-------------|
| 1 | Water Chemistry | pH, chlorine, alkalinity, calcium hardness |
| 2 | Equipment - Pumps | Single speed, variable speed, troubleshooting |
| 3 | Equipment - Filters | Sand, cartridge, DE filters |
| 4 | Equipment - Heaters | Gas, heat pump, solar heating |
| 5 | Saltwater Pools | Salt cells, maintenance, conversion |
| 6 | Troubleshooting | Common problems and solutions |
| 7 | Cleaning & Maintenance | Brushing, vacuuming, routines |
| 8 | Business Operations | Scheduling, pricing, growth |
| 9 | Safety & Liability | Chemical handling, insurance |
| 10 | ADA Compliance | Pool accessibility requirements |
| 11 | Emergency Response | Accidents, contamination |
| 12 | Customer Communication | Explaining issues to homeowners |
| 13 | Pool Automation | Controllers, smart systems |
| 14 | Pool Cleaners | Pressure, suction, robotic cleaners |
| 15 | Leak Detection | Bucket test, dye test, pressure testing |
| 16 | Seasonal Pool Care | Opening, closing, winterization |
| 17 | Variable Speed Pumps | Installation, programming, RPM settings |

## Tech Stack

- **Frontend**: Streamlit
- **Vector DB**: ChromaDB (in-memory)
- **Embeddings**: OpenAI text-embedding-3-small
- **LLM**: GPT-4o-mini (chat), GPT-4o (vision)

## API Costs

Approximate costs per 1,000 queries:
- Embeddings: ~$0.02
- GPT-4o-mini responses: ~$0.15
- GPT-4o vision (image analysis): ~$0.50 per image

---

Built for Skimmer Pro 🏊 | Contact: nidhi@getskimmer.com
