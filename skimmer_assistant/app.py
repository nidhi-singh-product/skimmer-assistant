"""
Skimmer Assistant - Pool Pro Knowledge Base
A beautifully designed RAG-powered chat app for pool service technicians
"""

import streamlit as st
import chromadb
from chromadb.utils import embedding_functions
import os
import base64
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Skimmer Assistant",
    page_icon="🏊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Skimmer Brand Colors
COLORS = {
    "navy": "#160F4E",
    "skimmer_dark": "#256295",
    "skimmer_light": "#4795EC",
    "mint": "#AEEBF3",
    "sunrise": "#FB8B24",
    "text_dark": "#212B36",
    "text_medium": "#637381",
    "bg_light": "#F9FAFB",
    "white": "#FFFFFF"
}

# Custom CSS - Perplexity-inspired with Skimmer branding
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Roboto:wght@400;500&display=swap');

    /* Global styles */
    .stApp {{
        background: linear-gradient(180deg, {COLORS['white']} 0%, {COLORS['bg_light']} 100%);
    }}

    /* Hide default Streamlit elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* Custom header */
    .skimmer-header {{
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1.5rem 0;
        margin-bottom: 1rem;
        border-bottom: 1px solid #E9EAEB;
    }}

    .skimmer-logo {{
        display: flex;
        align-items: center;
        gap: 12px;
    }}

    .skimmer-logo svg {{
        width: 40px;
        height: 40px;
    }}

    .skimmer-logo-text {{
        font-family: 'Outfit', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: {COLORS['skimmer_dark']};
        letter-spacing: -0.02em;
    }}

    .skimmer-logo-badge {{
        background: {COLORS['mint']};
        color: {COLORS['skimmer_dark']};
        font-family: 'Roboto', sans-serif;
        font-size: 0.7rem;
        font-weight: 500;
        padding: 2px 8px;
        border-radius: 12px;
        margin-left: 8px;
    }}

    /* Hero section - shown when no messages */
    .hero-section {{
        text-align: center;
        padding: 3rem 1rem;
        max-width: 600px;
        margin: 0 auto;
    }}

    .hero-title {{
        font-family: 'Outfit', sans-serif;
        font-size: 2.25rem;
        font-weight: 700;
        color: {COLORS['navy']};
        margin-bottom: 0.75rem;
        letter-spacing: -0.02em;
    }}

    .hero-subtitle {{
        font-family: 'Roboto', sans-serif;
        font-size: 1.1rem;
        color: {COLORS['text_medium']};
        margin-bottom: 2rem;
    }}

    /* Quick action buttons */
    .quick-actions {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        justify-content: center;
        margin-top: 1.5rem;
    }}

    .quick-action {{
        background: {COLORS['white']};
        border: 1px solid #E9EAEB;
        border-radius: 20px;
        padding: 8px 16px;
        font-family: 'Roboto', sans-serif;
        font-size: 0.875rem;
        color: {COLORS['text_dark']};
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
    }}

    .quick-action:hover {{
        border-color: {COLORS['skimmer_dark']};
        background: {COLORS['bg_light']};
    }}

    /* Chat message styles */
    .stChatMessage {{
        background: transparent !important;
        padding: 1rem 0 !important;
    }}

    /* User message */
    [data-testid="stChatMessageContent"] {{
        font-family: 'Roboto', sans-serif !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
    }}

    /* Response card */
    .response-card {{
        background: {COLORS['white']};
        border: 1px solid #E9EAEB;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}

    .response-card p {{
        font-family: 'Roboto', sans-serif;
        font-size: 1rem;
        line-height: 1.7;
        color: {COLORS['text_dark']};
    }}

    /* Sources section */
    .sources-section {{
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #E9EAEB;
    }}

    .sources-title {{
        font-family: 'Outfit', sans-serif;
        font-size: 0.8rem;
        font-weight: 600;
        color: {COLORS['text_medium']};
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.75rem;
    }}

    .source-chip {{
        display: inline-flex;
        align-items: center;
        background: {COLORS['bg_light']};
        border: 1px solid #E9EAEB;
        border-radius: 8px;
        padding: 6px 12px;
        margin: 4px;
        font-family: 'Roboto', sans-serif;
        font-size: 0.8rem;
        color: {COLORS['skimmer_dark']};
    }}

    .source-chip:hover {{
        background: {COLORS['mint']};
        border-color: {COLORS['skimmer_light']};
    }}

    /* Image upload area */
    .image-upload-area {{
        background: {COLORS['white']};
        border: 2px dashed #D2D4D6;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
        transition: all 0.2s ease;
    }}

    .image-upload-area:hover {{
        border-color: {COLORS['skimmer_dark']};
        background: {COLORS['bg_light']};
    }}

    .image-preview {{
        max-width: 300px;
        border-radius: 12px;
        margin: 1rem auto;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}

    /* Input styling */
    .stChatInput {{
        border-color: #E9EAEB !important;
    }}

    .stChatInput > div {{
        border-radius: 24px !important;
        border: 2px solid #E9EAEB !important;
        background: {COLORS['white']} !important;
    }}

    .stChatInput > div:focus-within {{
        border-color: {COLORS['skimmer_dark']} !important;
        box-shadow: 0 0 0 3px rgba(37, 98, 149, 0.1) !important;
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

    .status-warning {{
        background: #FEF3E5;
        color: #B45309;
    }}

    /* Expander styling */
    .streamlit-expanderHeader {{
        font-family: 'Roboto', sans-serif !important;
        font-size: 0.9rem !important;
        color: {COLORS['text_medium']} !important;
    }}

    /* Image upload button */
    .upload-btn {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: {COLORS['bg_light']};
        border: 1px solid #E9EAEB;
        border-radius: 8px;
        padding: 8px 16px;
        font-family: 'Roboto', sans-serif;
        font-size: 0.875rem;
        color: {COLORS['text_dark']};
        cursor: pointer;
        margin-bottom: 1rem;
    }}

    /* Wave decoration at bottom */
    .wave-decoration {{
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 100px;
        pointer-events: none;
        z-index: -1;
        opacity: 0.1;
    }}
</style>
""", unsafe_allow_html=True)

# Skimmer Logo SVG
SKIMMER_LOGO_SVG = """
<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M20 4C15 4 8 8 8 16C8 24 14 32 20 36C26 32 32 24 32 16C32 8 25 4 20 4Z" stroke="#256295" stroke-width="2.5" fill="none"/>
    <path d="M14 16C14 16 16 14 20 14C24 14 26 16 26 16" stroke="#256295" stroke-width="2" stroke-linecap="round"/>
    <path d="M16 20C16 20 17.5 18.5 20 18.5C22.5 18.5 24 20 24 20" stroke="#256295" stroke-width="2" stroke-linecap="round"/>
    <circle cx="20" cy="24" r="1.5" fill="#256295"/>
</svg>
"""


def get_api_key():
    """Get API key from secrets (cloud) or session state (local)"""
    if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
        return st.secrets['OPENAI_API_KEY']
    if os.getenv("OPENAI_API_KEY"):
        return os.getenv("OPENAI_API_KEY")
    return st.session_state.get("openai_api_key", "")


@st.cache_resource
def init_chromadb(_api_key):
    """Initialize ChromaDB with OpenAI embeddings"""
    if not _api_key:
        return None, None
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=_api_key,
        model_name="text-embedding-3-small"
    )
    client = chromadb.Client()
    collection = client.get_or_create_collection(
        name="pool_knowledge",
        embedding_function=openai_ef,
        metadata={"description": "Pool service technician knowledge base"}
    )
    return client, collection


def load_guides(collection):
    """Load markdown guides into the vector database"""
    possible_paths = [
        Path(__file__).parent.parent / "topic_guides",
        Path("topic_guides"),
        Path("../topic_guides"),
    ]

    guides_path = None
    for path in possible_paths:
        if path.exists():
            guides_path = path
            break

    if not guides_path:
        st.error("Topic guides folder not found!")
        return 0

    documents, metadatas, ids = [], [], []
    doc_id = 0

    for guide_file in sorted(guides_path.glob("*.md")):
        if guide_file.name == "README.md":
            continue

        content = guide_file.read_text()
        topic = guide_file.stem.replace("_", " ").title()
        if topic[0:2].isdigit():
            topic = topic[3:]

        chunks, current_chunk, current_header = [], "", topic
        for line in content.split("\n"):
            if line.startswith("## "):
                if current_chunk.strip():
                    chunks.append({
                        "content": current_chunk.strip(),
                        "header": current_header,
                        "source": guide_file.name
                    })
                current_header = line[3:].strip()
                current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"

        if current_chunk.strip():
            chunks.append({
                "content": current_chunk.strip(),
                "header": current_header,
                "source": guide_file.name
            })

        for chunk in chunks:
            documents.append(chunk["content"])
            metadatas.append({
                "source": chunk["source"],
                "topic": topic,
                "section": chunk["header"]
            })
            ids.append(f"doc_{doc_id}")
            doc_id += 1

    if documents:
        collection.add(documents=documents, metadatas=metadatas, ids=ids)

    return len(documents)


def generate_response(query, context, api_key):
    """Generate a response using GPT-4o-mini"""
    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    system_prompt = """You are Skimmer Assistant, a helpful expert for pool service technicians.
Answer questions using ONLY the provided context. Be specific with exact numbers, procedures, and safety warnings.
Format your response clearly with short paragraphs. Use bullet points only when listing steps or items.
If the context doesn't contain enough information, say so honestly."""

    context_text = "\n\n---\n\n".join(context)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {query}"}
        ],
        temperature=0.3,
        max_tokens=1000
    )
    return response.choices[0].message.content


def analyze_image(image_bytes, question, context, api_key):
    """Analyze an image using GPT-4o vision"""
    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    system_prompt = """You are Skimmer Assistant, a pool service expert with vision capabilities.
First, analyze the image to identify any pool-related issues (equipment problems, water conditions, damage, error codes, etc.).
Then, use the provided knowledge base context to give specific repair procedures, chemical dosages, or troubleshooting steps.
Be specific with exact numbers and procedures from the context. If you can't identify the issue clearly, say so."""

    context_text = "\n\n---\n\n".join(context) if context else "No specific context found."

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                {"type": "text", "text": f"Knowledge Base Context:\n{context_text}\n\nUser Question: {question}"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ],
        temperature=0.3,
        max_tokens=1500
    )
    return response.choices[0].message.content


def render_header():
    """Render the Skimmer header"""
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


def render_hero():
    """Render the hero section with quick actions and photo upload"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem; max-width: 600px; margin: 0 auto;">
        <h1 style="font-family: 'Outfit', sans-serif; font-size: 2.25rem; font-weight: 700; color: #160F4E; margin-bottom: 0.75rem; letter-spacing: -0.02em;">What can I help you with?</h1>
        <p style="font-family: 'Roboto', sans-serif; font-size: 1.1rem; color: #637381; margin-bottom: 1.5rem;">Your AI-powered pool service expert. Ask about water chemistry, equipment repair, troubleshooting, and more.</p>
    </div>
    """, unsafe_allow_html=True)

    # Photo upload section - prominent in main area
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

    # Quick action suggestions
    st.markdown("""
    <div style="text-align: center; margin-bottom: 0.5rem;">
        <p style="font-family: 'Roboto', sans-serif; font-size: 0.85rem; color: #919EAB;">Or try a quick question:</p>
    </div>
    """, unsafe_allow_html=True)

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


def render_sources(metadatas):
    """Render sources in a nice format"""
    if not metadatas:
        return

    unique_sources = []
    seen = set()
    for m in metadatas[:4]:
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


def main():
    # Initialize session state
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

    api_key = get_api_key()

    # Sidebar - Settings
    with st.sidebar:
        st.markdown("### ⚙️ Settings")

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

        if api_key:
            client, collection = init_chromadb(api_key)
            if collection:
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

        # Image upload in sidebar
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

        # Clear chat button
        st.markdown("---")
        if st.button("🗑️ Clear conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    # Main content
    render_header()

    if not api_key:
        st.info("👈 Enter your OpenAI API key in the sidebar to get started")
        return

    client, collection = init_chromadb(api_key)
    if not collection:
        st.error("Failed to initialize. Please check your API key.")
        return

    if collection.count() == 0:
        st.warning("📥 Click 'Load Knowledge Base' in the sidebar to get started")
        return

    # Show hero if no messages
    if not st.session_state.messages:
        render_hero()

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🏊" if message["role"] == "assistant" else None):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                render_sources(message["sources"])

    # Handle prefilled questions from quick actions
    prefill_text = st.session_state.get("prefill", None)
    if prefill_text:
        st.session_state.prefill = None

    # Image upload indicator
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

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🏊"):
            has_image = st.session_state.get("uploaded_image") is not None

            with st.spinner("Thinking..." if not has_image else "Analyzing image..."):
                results = collection.query(query_texts=[prompt], n_results=5)
                context = results["documents"][0] if results and results["documents"] and results["documents"][0] else []
                metadatas = results["metadatas"][0] if results and results["metadatas"] and results["metadatas"][0] else []

                if has_image:
                    response = analyze_image(
                        st.session_state.uploaded_image,
                        prompt,
                        context,
                        api_key
                    )
                    st.session_state.uploaded_image = None
                elif context:
                    response = generate_response(prompt, context, api_key)
                else:
                    response = "I couldn't find relevant information for that question in my knowledge base."

                st.markdown(response)

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


if __name__ == "__main__":
    main()
