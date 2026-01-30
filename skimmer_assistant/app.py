"""
Skimmer Assistant - Pool Pro Knowledge Base
============================================

A RAG (Retrieval-Augmented Generation) powered chat application for pool service
technicians. Built with Streamlit, ChromaDB, and OpenAI.

Architecture Overview:
---------------------
1. Knowledge Base: Markdown files in ../topic_guides/ are chunked and embedded
   into ChromaDB vector database for semantic search.

2. Query Flow:
   - User asks a question (text or with image)
   - Question is embedded and matched against knowledge base
   - Top 5 relevant chunks are retrieved
   - GPT-4o-mini generates response using retrieved context

3. Image Analysis:
   - Users can upload photos of pool equipment/issues
   - GPT-4o Vision analyzes the image
   - Knowledge base context augments the visual analysis

Dependencies:
------------
- streamlit: Web UI framework
- chromadb: Vector database for embeddings
- openai: GPT-4o and embedding models

Environment Variables:
---------------------
- OPENAI_API_KEY: Required for embeddings and chat completion

Author: Skimmer Pro Team
Version: 1.0.0 (POC)
Last Updated: January 2025
"""

import streamlit as st
import chromadb
from chromadb.utils import embedding_functions
import os
import base64
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import streamlit.components.v1 as components
import hashlib

# =============================================================================
# CONFIGURATION
# =============================================================================

# Streamlit page configuration - must be first Streamlit command
st.set_page_config(
    page_title="Skimmer Assistant",
    page_icon="🏊",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Skimmer Brand Colors - matches company style guide
COLORS = {
    "navy": "#160F4E",           # Primary dark - headers, emphasis
    "skimmer_dark": "#256295",   # Primary blue - buttons, links
    "skimmer_light": "#4795EC",  # Secondary blue - hover states
    "mint": "#AEEBF3",           # Accent - badges, highlights
    "sunrise": "#FB8B24",        # Warning/attention color
    "text_dark": "#212B36",      # Primary text
    "text_medium": "#637381",    # Secondary text
    "bg_light": "#F9FAFB",       # Background
    "white": "#FFFFFF"           # Cards, inputs
}

# Model configuration
EMBEDDING_MODEL = "text-embedding-3-small"  # OpenAI embedding model
CHAT_MODEL = "gpt-4o-mini"                  # For text responses
VISION_MODEL = "gpt-4o"                     # For image analysis

# RAG configuration
CHUNK_RESULTS = 5        # Number of chunks to retrieve per query
MAX_RESPONSE_TOKENS = 1000
TEMPERATURE = 0.3        # Lower = more focused responses


# =============================================================================
# STYLES
# =============================================================================

def load_custom_css() -> None:
    """
    Inject custom CSS for Perplexity-inspired UI with Skimmer branding.

    Design Philosophy:
    - Clean, minimal interface inspired by Perplexity.ai
    - Skimmer brand colors and typography
    - Mobile-responsive layout
    - Accessible color contrast ratios
    """
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Roboto:wght@400;500&display=swap');

        /* Global styles */
        .stApp {{
            background: linear-gradient(180deg, {COLORS['white']} 0%, {COLORS['bg_light']} 100%);
        }}

        /* Hide default Streamlit chrome for cleaner look */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}

        /* Chat message styling */
        .stChatMessage {{
            background: transparent !important;
            padding: 1rem 0 !important;
        }}

        [data-testid="stChatMessageContent"] {{
            font-family: 'Roboto', sans-serif !important;
            font-size: 1rem !important;
            line-height: 1.6 !important;
        }}

        /* Input field styling */
        .stChatInput > div {{
            border-radius: 24px !important;
            border: 2px solid #E9EAEB !important;
            background: {COLORS['white']} !important;
        }}

        .stChatInput > div:focus-within {{
            border-color: {COLORS['skimmer_dark']} !important;
            box-shadow: 0 0 0 3px rgba(37, 98, 149, 0.1) !important;
        }}

        /* Chat input send button - Skimmer brand colors */
        .stChatInput button {{
            background: {COLORS['skimmer_dark']} !important;
            border: none !important;
        }}

        .stChatInput button:hover {{
            background: {COLORS['navy']} !important;
        }}

        .stChatInput button svg {{
            fill: {COLORS['white']} !important;
            stroke: {COLORS['white']} !important;
        }}

        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background: {COLORS['white']};
            border-right: 1px solid #E9EAEB;
        }}

        [data-testid="stSidebar"] .stMarkdown h3 {{
            font-family: 'Outfit', sans-serif;
            color: {COLORS['navy']};
        }}

        /* Button styling */
        .stButton > button {{
            font-family: 'Roboto', sans-serif;
            font-weight: 500;
            border-radius: 8px;
            transition: all 0.2s ease;
        }}

        .stButton > button[kind="primary"] {{
            background: {COLORS['skimmer_dark']};
            border: none;
        }}

        .stButton > button[kind="primary"]:hover {{
            background: {COLORS['navy']};
        }}

        /* Status badges */
        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 20px;
            font-family: 'Roboto', sans-serif;
            font-size: 0.8rem;
            font-weight: 500;
        }}

        .status-success {{
            background: #E6F7ED;
            color: #1B7F4A;
        }}
    </style>
    """, unsafe_allow_html=True)


# =============================================================================
# API KEY MANAGEMENT
# =============================================================================

def get_api_key() -> str:
    """
    Retrieve OpenAI API key from available sources.

    Priority order:
    1. Streamlit secrets (for Streamlit Cloud deployment)
    2. Environment variable (for local development)
    3. Session state (user-entered in sidebar)

    Returns:
        str: API key or empty string if not found

    Security Note:
        API keys should never be committed to version control.
        Use .streamlit/secrets.toml locally or Streamlit Cloud secrets in production.
    """
    # Check Streamlit secrets first (production)
    if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
        return st.secrets['OPENAI_API_KEY']

    # Check environment variable (local development)
    if os.getenv("OPENAI_API_KEY"):
        return os.getenv("OPENAI_API_KEY")

    # Fall back to user-entered key in session
    return st.session_state.get("openai_api_key", "")


# =============================================================================
# VECTOR DATABASE
# =============================================================================

@st.cache_resource
def init_chromadb(_api_key: str) -> Tuple[Optional[chromadb.Client], Optional[chromadb.Collection]]:
    """
    Initialize ChromaDB client and collection with OpenAI embeddings.

    Uses Streamlit's cache_resource decorator to persist across reruns.
    The underscore prefix on _api_key prevents Streamlit from hashing it.

    Args:
        _api_key: OpenAI API key for embedding function

    Returns:
        Tuple of (client, collection) or (None, None) if initialization fails

    Technical Notes:
        - Uses in-memory ChromaDB (resets on app restart)
        - For production, consider persistent storage with chromadb.PersistentClient
        - Embedding dimension: 1536 (text-embedding-3-small)
    """
    if not _api_key:
        return None, None

    # Configure OpenAI embedding function
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=_api_key,
        model_name=EMBEDDING_MODEL
    )

    # Create in-memory client
    client = chromadb.Client()

    # Get or create the knowledge base collection
    collection = client.get_or_create_collection(
        name="pool_knowledge",
        embedding_function=openai_ef,
        metadata={"description": "Pool service technician knowledge base"}
    )

    return client, collection


def load_guides(collection: chromadb.Collection) -> int:
    """
    Load and chunk markdown guides into the vector database.

    Chunking Strategy:
    - Split on H2 headers (## ) to create semantic chunks
    - Each chunk includes its header for context
    - Metadata tracks source file, topic, and section

    Args:
        collection: ChromaDB collection to load documents into

    Returns:
        int: Number of chunks loaded

    File Structure Expected:
        topic_guides/
        ├── 01_water_chemistry.md
        ├── 02_equipment_pumps.md
        └── ...
    """
    # Try multiple paths to find topic_guides (handles different deployments)
    possible_paths = [
        Path(__file__).parent.parent / "topic_guides",  # Standard structure
        Path("topic_guides"),                            # Current directory
        Path("../topic_guides"),                         # Parent directory
    ]

    guides_path = None
    for path in possible_paths:
        if path.exists():
            guides_path = path
            break

    if not guides_path:
        st.error("Topic guides folder not found!")
        return 0

    documents: List[str] = []
    metadatas: List[Dict] = []
    ids: List[str] = []
    doc_id = 0

    # Process each markdown file
    for guide_file in sorted(guides_path.glob("*.md")):
        # Skip README
        if guide_file.name == "README.md":
            continue

        content = guide_file.read_text()

        # Extract topic name from filename (e.g., "01_water_chemistry.md" -> "Water Chemistry")
        topic = guide_file.stem.replace("_", " ").title()
        if topic[0:2].isdigit():
            topic = topic[3:]  # Remove number prefix

        # Chunk by H2 headers
        chunks: List[Dict] = []
        current_chunk = ""
        current_header = topic

        for line in content.split("\n"):
            if line.startswith("## "):
                # Save previous chunk
                if current_chunk.strip():
                    chunks.append({
                        "content": current_chunk.strip(),
                        "header": current_header,
                        "source": guide_file.name
                    })
                # Start new chunk
                current_header = line[3:].strip()
                current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"

        # Don't forget the last chunk
        if current_chunk.strip():
            chunks.append({
                "content": current_chunk.strip(),
                "header": current_header,
                "source": guide_file.name
            })

        # Add chunks to batch
        for chunk in chunks:
            documents.append(chunk["content"])
            metadatas.append({
                "source": chunk["source"],
                "topic": topic,
                "section": chunk["header"]
            })
            ids.append(f"doc_{doc_id}")
            doc_id += 1

    # Batch insert into ChromaDB
    if documents:
        collection.add(documents=documents, metadatas=metadatas, ids=ids)

    return len(documents)


# =============================================================================
# AI RESPONSE GENERATION
# =============================================================================

def generate_response(query: str, context: List[str], api_key: str) -> str:
    """
    Generate a response using GPT-4o-mini with RAG context.

    Args:
        query: User's question
        context: List of relevant text chunks from knowledge base
        api_key: OpenAI API key

    Returns:
        str: Generated response

    Prompt Engineering Notes:
        - System prompt establishes expert persona
        - Context is clearly separated from question
        - Temperature 0.3 for factual, consistent responses
    """
    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    system_prompt = """You are Skimmer Assistant, a helpful expert for pool service technicians.
Answer questions using ONLY the provided context. Be specific with exact numbers, procedures, and safety warnings.
Format your response clearly with short paragraphs. Use bullet points only when listing steps or items.
If the context doesn't contain enough information, say so honestly."""

    # Join context chunks with clear separators
    context_text = "\n\n---\n\n".join(context)

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {query}"}
        ],
        temperature=TEMPERATURE,
        max_tokens=MAX_RESPONSE_TOKENS
    )

    return response.choices[0].message.content


def analyze_image(image_bytes: bytes, question: str, context: List[str], api_key: str) -> str:
    """
    Analyze an uploaded image using GPT-4o Vision with RAG context.

    This enables technicians to upload photos of:
    - Equipment with error codes
    - Water conditions (green pools, cloudiness)
    - Damaged equipment
    - Unknown parts for identification

    Args:
        image_bytes: Raw image bytes
        question: User's question about the image
        context: Relevant knowledge base chunks
        api_key: OpenAI API key

    Returns:
        str: Analysis and recommendations

    Technical Notes:
        - Image is base64 encoded for API transmission
        - GPT-4o (not mini) required for vision capabilities
        - Context augments visual analysis with specific procedures
    """
    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    # Encode image for API
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    system_prompt = """You are Skimmer Assistant, a pool service expert with vision capabilities.
First, analyze the image to identify any pool-related issues (equipment problems, water conditions, damage, error codes, etc.).
Then, use the provided knowledge base context to give specific repair procedures, chemical dosages, or troubleshooting steps.
Be specific with exact numbers and procedures from the context. If you can't identify the issue clearly, say so."""

    context_text = "\n\n---\n\n".join(context) if context else "No specific context found."

    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                {"type": "text", "text": f"Knowledge Base Context:\n{context_text}\n\nUser Question: {question}"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ],
        temperature=TEMPERATURE,
        max_tokens=1500
    )

    return response.choices[0].message.content


# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_read_aloud_button(text: str, button_key: str) -> None:
    """
    Render a "Read Aloud" button that uses the browser's Speech Synthesis API.

    This enables hands-free operation for field technicians who may be working
    with equipment and can't easily read a screen.

    Args:
        text: The text content to be read aloud
        button_key: Unique key for the button (to handle multiple buttons)

    Technical Notes:
        - Uses Web Speech API (built into modern browsers)
        - Works on mobile devices (iOS Safari, Android Chrome)
        - No API costs - runs entirely in the browser
        - Falls back gracefully if speech synthesis unavailable
    """
    # Escape text for JavaScript (handle quotes and newlines)
    escaped_text = text.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

    # Create unique ID for this button instance
    button_id = hashlib.md5(button_key.encode()).hexdigest()[:8]

    # HTML/JavaScript component for text-to-speech
    tts_html = f"""
    <div style="margin: 10px 0;">
        <button id="tts-btn-{button_id}" onclick="toggleSpeech_{button_id}()" style="
            background: linear-gradient(135deg, #256295 0%, #4795EC 100%);
            color: white;
            border: none;
            border-radius: 20px;
            padding: 8px 16px;
            font-family: 'Roboto', sans-serif;
            font-size: 0.85rem;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(37, 98, 149, 0.2);
        " onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 8px rgba(37, 98, 149, 0.3)';"
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 4px rgba(37, 98, 149, 0.2)';">
            <span id="tts-icon-{button_id}">🔊</span>
            <span id="tts-text-{button_id}">Read Aloud</span>
        </button>
    </div>

    <script>
        let speaking_{button_id} = false;
        let utterance_{button_id} = null;

        function toggleSpeech_{button_id}() {{
            const btn = document.getElementById('tts-btn-{button_id}');
            const icon = document.getElementById('tts-icon-{button_id}');
            const text = document.getElementById('tts-text-{button_id}');

            if (!('speechSynthesis' in window)) {{
                alert('Sorry, your browser does not support text-to-speech.');
                return;
            }}

            if (speaking_{button_id}) {{
                // Stop speaking
                window.speechSynthesis.cancel();
                speaking_{button_id} = false;
                icon.textContent = '🔊';
                text.textContent = 'Read Aloud';
                btn.style.background = 'linear-gradient(135deg, #256295 0%, #4795EC 100%)';
            }} else {{
                // Start speaking
                const content = `{escaped_text}`;
                utterance_{button_id} = new SpeechSynthesisUtterance(content);
                utterance_{button_id}.rate = 0.9;  // Slightly slower for clarity
                utterance_{button_id}.pitch = 1.0;

                // Try to use a natural-sounding voice
                const voices = window.speechSynthesis.getVoices();
                const preferredVoice = voices.find(v =>
                    v.name.includes('Samantha') ||
                    v.name.includes('Google') ||
                    v.name.includes('Microsoft') ||
                    v.lang.startsWith('en')
                );
                if (preferredVoice) {{
                    utterance_{button_id}.voice = preferredVoice;
                }}

                utterance_{button_id}.onend = function() {{
                    speaking_{button_id} = false;
                    icon.textContent = '🔊';
                    text.textContent = 'Read Aloud';
                    btn.style.background = 'linear-gradient(135deg, #256295 0%, #4795EC 100%)';
                }};

                utterance_{button_id}.onerror = function() {{
                    speaking_{button_id} = false;
                    icon.textContent = '🔊';
                    text.textContent = 'Read Aloud';
                    btn.style.background = 'linear-gradient(135deg, #256295 0%, #4795EC 100%)';
                }};

                window.speechSynthesis.speak(utterance_{button_id});
                speaking_{button_id} = true;
                icon.textContent = '⏹️';
                text.textContent = 'Stop';
                btn.style.background = 'linear-gradient(135deg, #FCA250 0%, #FB8B24 100%)';
            }}
        }}

        // Load voices (needed for some browsers)
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.getVoices();
        }}
    </script>
    """

    components.html(tts_html, height=50)


def render_header() -> None:
    """Render the Skimmer-branded header with logo."""
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: center; padding: 1.5rem 0; margin-bottom: 1rem; border-bottom: 1px solid #E9EAEB;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 40px; height: 40px;">
                <path d="M20 4C15 4 8 8 8 16C8 24 14 32 20 36C26 32 32 24 32 16C32 8 25 4 20 4Z" stroke="#256295" stroke-width="2.5" fill="none"/>
                <path d="M14 16C14 16 16 14 20 14C24 14 26 16 26 16" stroke="#256295" stroke-width="2" stroke-linecap="round"/>
                <path d="M16 20C16 20 17.5 18.5 20 18.5C22.5 18.5 24 20 24 20" stroke="#256295" stroke-width="2" stroke-linecap="round"/>
                <circle cx="20" cy="24" r="1.5" fill="#256295"/>
            </svg>
            <span style="font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 700; color: #256295; letter-spacing: -0.02em;">Skimmer Assistant</span>
            <span style="background: #AEEBF3; color: #256295; font-family: 'Roboto', sans-serif; font-size: 0.7rem; font-weight: 500; padding: 2px 8px; border-radius: 12px;">AI</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_hero() -> None:
    """
    Render the hero section shown when chat is empty.

    Includes:
    - Welcome message
    - Photo upload prompt
    - Quick action buttons for common questions
    """
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem; max-width: 600px; margin: 0 auto;">
        <h1 style="font-family: 'Outfit', sans-serif; font-size: 2.25rem; font-weight: 700; color: #160F4E; margin-bottom: 0.75rem; letter-spacing: -0.02em;">What can I help you with?</h1>
        <p style="font-family: 'Roboto', sans-serif; font-size: 1.1rem; color: #637381; margin-bottom: 1.5rem;">Your AI-powered pool service expert. Ask about water chemistry, equipment repair, troubleshooting, and more.</p>
    </div>
    """, unsafe_allow_html=True)

    # Photo upload section
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1rem;">
        <p style="font-family: 'Roboto', sans-serif; font-size: 0.9rem; color: #637381;">📷 Have a photo of an issue? Upload it below!</p>
    </div>
    """, unsafe_allow_html=True)

    # Centered file uploader
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        uploaded_image = st.file_uploader(
            "Upload a photo of pool equipment, water issues, or error codes",
            type=["jpg", "jpeg", "png"],
            key="hero_image_uploader",
            help="Take a photo and upload it to get AI-powered diagnosis"
        )
        if uploaded_image:
            st.image(uploaded_image, use_container_width=True)
            st.session_state.uploaded_image = uploaded_image.getvalue()
            st.success("✓ Photo uploaded! Now ask a question about it below.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick action buttons
    st.markdown("""
    <div style="text-align: center; margin-bottom: 0.5rem;">
        <p style="font-family: 'Roboto', sans-serif; font-size: 0.85rem; color: #919EAB;">Or try a quick question:</p>
    </div>
    """, unsafe_allow_html=True)

    # First row of quick actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💧 Balance pH levels", use_container_width=True):
            st.session_state.prefill = "How do I balance pH levels in a pool?"
            st.rerun()
    with col2:
        if st.button("🔧 Fix pump issues", use_container_width=True):
            st.session_state.prefill = "How do I troubleshoot a pool pump that won't prime?"
            st.rerun()
    with col3:
        if st.button("🧪 Green pool fix", use_container_width=True):
            st.session_state.prefill = "How do I treat a green algae pool?"
            st.rerun()

    # Second row of quick actions
    col4, col5, col6 = st.columns(3)
    with col4:
        if st.button("❄️ Winter closing", use_container_width=True):
            st.session_state.prefill = "What are the steps for winterizing a pool?"
            st.rerun()
    with col5:
        if st.button("🔍 Leak detection", use_container_width=True):
            st.session_state.prefill = "How do I perform a bucket test for leaks?"
            st.rerun()
    with col6:
        if st.button("⚡ Variable speed pump", use_container_width=True):
            st.session_state.prefill = "What RPM settings should I use for a variable speed pump?"
            st.rerun()


def render_sources(metadatas: List[Dict]) -> None:
    """
    Render source citations for transparency.

    Shows which knowledge base sections were used to generate the response.
    This builds trust and allows users to verify information.

    Args:
        metadatas: List of metadata dicts with 'topic' and 'section' keys
    """
    if not metadatas:
        return

    # Deduplicate sources
    unique_sources = []
    seen = set()
    for m in metadatas[:4]:  # Limit to 4 sources
        key = f"{m['topic']}-{m['section']}"
        if key not in seen:
            seen.add(key)
            unique_sources.append(m)

    st.markdown("---")
    st.markdown("**📚 Sources**")

    cols = st.columns(len(unique_sources))
    for i, source in enumerate(unique_sources):
        with cols[i]:
            st.markdown(f"""
            <div style="background: #F9FAFB; border: 1px solid #E9EAEB; border-radius: 8px; padding: 10px; text-align: center;">
                <div style="font-size: 0.75rem; color: #637381; margin-bottom: 4px;">{source['topic']}</div>
                <div style="font-size: 0.85rem; color: #256295; font-weight: 500;">{source['section'][:30]}...</div>
            </div>
            """, unsafe_allow_html=True)


def render_feedback_buttons(response_idx: int) -> None:
    """
    Render thumbs up/down feedback buttons for response quality tracking.

    This helps measure AI quality and identify areas for improvement.
    Feedback is stored in session state for now (could be sent to analytics later).

    Args:
        response_idx: Index of the response for unique button keys
    """
    # Initialize feedback storage
    if "feedback" not in st.session_state:
        st.session_state.feedback = {}

    feedback_key = f"feedback_{response_idx}"
    current_feedback = st.session_state.feedback.get(feedback_key)

    st.markdown("""
    <div style="margin-top: 8px;">
        <span style="font-size: 0.75rem; color: #919EAB; margin-right: 8px;">Was this helpful?</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 10])

    with col1:
        if current_feedback == "up":
            st.markdown("✅")
        elif st.button("👍", key=f"up_{response_idx}", help="This was helpful"):
            st.session_state.feedback[feedback_key] = "up"
            st.rerun()

    with col2:
        if current_feedback == "down":
            st.markdown("❌")
        elif st.button("👎", key=f"down_{response_idx}", help="This needs improvement"):
            st.session_state.feedback[feedback_key] = "down"
            st.rerun()


def render_disclaimer() -> None:
    """
    Render the AI disclaimer at the bottom of the page.

    Important for setting expectations and legal protection.
    """
    st.markdown("""
    <div style="
        text-align: center;
        padding: 1.5rem;
        margin-top: 2rem;
        border-top: 1px solid #E9EAEB;
        color: #919EAB;
        font-size: 0.75rem;
        font-family: 'Roboto', sans-serif;
    ">
        <p style="margin: 0;">
            🤖 <strong>Powered by AI</strong> · Responses are generated using artificial intelligence and may not always be accurate.
            <br>Always verify critical information and follow manufacturer guidelines.
        </p>
        <p style="margin: 8px 0 0 0; font-size: 0.7rem;">
            © 2026 Skimmer Pro · Pool Service Knowledge Base POC
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar(api_key: str, collection: Optional[chromadb.Collection]) -> None:
    """
    Render the sidebar with settings and controls.

    Sections:
    - API key input (if not configured)
    - Knowledge base status and reload
    - Photo upload (alternative location)
    - Clear conversation button
    """
    with st.sidebar:
        st.markdown("### ⚙️ Settings")

        # API key input (only if not in secrets)
        if not (hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets):
            manual_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=st.session_state.openai_api_key,
                help="Enter your OpenAI API key"
            )
            if manual_key and manual_key != st.session_state.openai_api_key:
                st.session_state.openai_api_key = manual_key
                st.rerun()
        else:
            st.markdown('<div class="status-badge status-success">✓ API Connected</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📚 Knowledge Base")

        if api_key and collection:
            count = collection.count()
            if count == 0:
                if st.button("📥 Load Knowledge Base", use_container_width=True):
                    with st.spinner("Loading..."):
                        loaded = load_guides(collection)
                        st.session_state.kb_loaded = True
                        st.success(f"✓ Loaded {loaded} chunks")
                        st.rerun()
            else:
                st.markdown(f'<div class="status-badge status-success">✓ {count} chunks ready</div>', unsafe_allow_html=True)
                if st.button("🔄 Reload", use_container_width=True):
                    all_ids = collection.get()["ids"]
                    if all_ids:
                        collection.delete(ids=all_ids)
                    load_guides(collection)
                    st.rerun()

        # Sidebar image upload
        st.markdown("---")
        st.markdown("### 📷 Photo Analysis")
        st.caption("Upload a photo to get help identifying issues")
        uploaded_image = st.file_uploader(
            "Drop image here",
            type=["jpg", "jpeg", "png"],
            key="image_uploader",
            label_visibility="collapsed"
        )
        if uploaded_image:
            st.image(uploaded_image, use_container_width=True)
            st.session_state.uploaded_image = uploaded_image.getvalue()
            st.info("📷 Now ask a question about this image!")
        else:
            st.session_state.uploaded_image = None

        # Clear conversation
        st.markdown("---")
        if st.button("🗑️ Clear conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main() -> None:
    """
    Main application entry point.

    Flow:
    1. Initialize session state
    2. Load CSS and render header
    3. Handle API key and database initialization
    4. Render chat interface
    5. Process user queries
    """
    # Initialize session state variables
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = ""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_image" not in st.session_state:
        st.session_state.uploaded_image = None
    if "kb_loaded" not in st.session_state:
        st.session_state.kb_loaded = False
    if "prefill" not in st.session_state:
        st.session_state.prefill = None

    # Load styling
    load_custom_css()

    # Get API key
    api_key = get_api_key()

    # Initialize database
    client, collection = None, None
    if api_key:
        client, collection = init_chromadb(api_key)

    # Render sidebar
    render_sidebar(api_key, collection)

    # Render main header
    render_header()

    # Check prerequisites
    if not api_key:
        st.info("👈 Enter your OpenAI API key in the sidebar to get started")
        return

    if not collection:
        st.error("Failed to initialize. Please check your API key.")
        return

    if collection.count() == 0:
        st.warning("📥 Click 'Load Knowledge Base' in the sidebar to get started")
        return

    # Show hero section if no messages yet
    if not st.session_state.messages:
        render_hero()

    # Display chat history
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"], avatar="🏊" if message["role"] == "assistant" else None):
            st.markdown(message["content"])
            # Add Read Aloud button for assistant messages
            if message["role"] == "assistant":
                render_read_aloud_button(message["content"], f"history_{idx}")
                render_feedback_buttons(idx)  # Add feedback buttons
            if "sources" in message and message["sources"]:
                render_sources(message["sources"])

    # Handle prefilled questions from quick actions
    prefill_text = st.session_state.get("prefill", None)
    if prefill_text:
        st.session_state.prefill = None

    # Show image upload indicator
    if st.session_state.get("uploaded_image"):
        st.info("📷 **Image attached** - Ask a question about it below!")

    # Chat input
    placeholder_text = "Ask about pool service, water chemistry, equipment..."
    if st.session_state.get("uploaded_image"):
        placeholder_text = "What's wrong with this? / How do I fix this?"

    prompt = st.chat_input(placeholder_text)

    # Use prefill if available
    if prefill_text and not prompt:
        prompt = prefill_text

    # Process user input
    if prompt:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant", avatar="🏊"):
            has_image = st.session_state.get("uploaded_image") is not None

            with st.spinner("Thinking..." if not has_image else "Analyzing image..."):
                # Retrieve relevant context
                results = collection.query(query_texts=[prompt], n_results=CHUNK_RESULTS)
                context = results["documents"][0] if results and results["documents"] and results["documents"][0] else []
                metadatas = results["metadatas"][0] if results and results["metadatas"] and results["metadatas"][0] else []

                # Generate response (with or without image)
                if has_image:
                    response = analyze_image(
                        st.session_state.uploaded_image,
                        prompt,
                        context,
                        api_key
                    )
                    st.session_state.uploaded_image = None  # Clear after use
                elif context:
                    response = generate_response(prompt, context, api_key)
                else:
                    response = "I couldn't find relevant information for that question in my knowledge base."

                st.markdown(response)

                # Add Read Aloud button for the new response
                render_read_aloud_button(response, f"new_{len(st.session_state.messages)}")

                # Show sources and save to history
                if metadatas:
                    render_sources(metadatas)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "sources": [{"topic": m["topic"], "section": m["section"]} for m in metadatas]
                    })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })

    # Render disclaimer at the bottom
    render_disclaimer()


# Entry point
if __name__ == "__main__":
    main()
