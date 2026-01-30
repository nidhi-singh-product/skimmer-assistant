# Skimmer Assistant - Pool Pro Knowledge Base

A RAG-powered chat application for pool service technicians.

## Quick Start

### 1. Install Dependencies

```bash
cd skimmer_assistant
pip install -r requirements.txt
```

### 2. Run the App

```bash
streamlit run app.py
```

### 3. Enter Your OpenAI API Key

- Get a key from [platform.openai.com](https://platform.openai.com)
- Enter it in the sidebar

### 4. Load the Knowledge Base

- Click "Load Topic Guides" in the sidebar
- Wait for the guides to be embedded (~30 seconds)

### 5. Start Asking Questions!

Example questions:
- "What's the ideal pH range for a pool?"
- "How do I troubleshoot a pump that won't prime?"
- "What are the steps to treat green pool water?"
- "How much salt should be in a saltwater pool?"

## Features

- 12 comprehensive topic guides covering all aspects of pool service
- Vector search using ChromaDB for accurate retrieval
- GPT-4o-mini for generating helpful answers
- Source citations for every response
- Skimmer branding with your colors

## Topic Guides Included

1. Water Chemistry
2. Equipment - Pumps
3. Equipment - Filters
4. Equipment - Heaters
5. Saltwater Pools
6. Troubleshooting
7. Cleaning & Maintenance
8. Business Operations
9. Safety & Liability
10. ADA Compliance
11. Emergency Response
12. Customer Communication

## File Structure

```
skimmer_assistant/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── chroma_db/         # Vector database (created on first run)

topic_guides/          # Knowledge base content (in parent folder)
├── 01_water_chemistry.md
├── 02_equipment_pumps.md
└── ... (12 files total)
```

## Customization

- Edit the topic guides in `../topic_guides/` to update content
- Click "Reload Guides" in the sidebar after making changes
- Modify `app.py` to customize the UI or add features

## Deployment

To deploy on Streamlit Cloud:
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Add `OPENAI_API_KEY` to secrets
