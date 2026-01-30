"""
Skimmer Assistant - Pool Pro Knowledge Base
A RAG-powered chat app for pool service technicians
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
    layout="centered"
)

# Custom CSS for Skimmer branding
st.markdown("""
<style>
    .stApp {
        background-color: #F9FAFB;
    }
    .main-header {
        background-color: #160F4E;
        padding: 1rem 2rem;
        border-radius: 8px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-family: 'Outfit', sans-serif;
    }
    .main-header p {
        color: #AEEBF3;
        margin: 0;
        font-size: 0.9rem;
    }
    .stButton > button {
        background-color: #FB8B24;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
    }
    .stButton > button:hover {
        background-color: #BC681B;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🏊 Skimmer Assistant</h1>
    <p>Pool Pro Knowledge Base</p>
</div>
""", unsafe_allow_html=True)


def get_api_key():
    """Get API key from secrets (cloud) or session state (local)"""
    # First check Streamlit secrets (for cloud deployment)
    if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
        return st.secrets['OPENAI_API_KEY']
    # Then check environment variable
    if os.getenv("OPENAI_API_KEY"):
        return os.getenv("OPENAI_API_KEY")
    # Finally check session state (manual input)
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
    # Use in-memory client for cloud (persistent for local)
    client = chromadb.Client()  # In-memory for cloud compatibility
    collection = client.get_or_create_collection(
        name="pool_knowledge",
        embedding_function=openai_ef,
        metadata={"description": "Pool service technician knowledge base"}
    )
    return client, collection


def load_guides(collection):
    """Load markdown guides into the vector database"""
    # Try multiple paths for flexibility
    possible_paths = [
        Path(__file__).parent.parent / "topic_guides",  # When run from skimmer_assistant/
        Path("topic_guides"),  # When run from root
        Path("../topic_guides"),  # Relative path
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

        # Chunk by ## headers
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
    """Analyze an image using GPT-4o vision and combine with knowledge base context."""
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

    # Get API key (from secrets, env, or manual input)
    api_key = get_api_key()

    with st.sidebar:
        st.markdown("### ⚙️ Settings")

        # Only show manual API key input if not configured in secrets
        if not (hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets):
            manual_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=st.session_state.openai_api_key,
                help="Enter your OpenAI API key"
            )
            if manual_key and manual_key != st.session_state.openai_api_key:
                st.session_state.openai_api_key = manual_key
                api_key = manual_key
                st.rerun()
        else:
            st.success("✅ API Key configured")

        st.markdown("---")
        st.markdown("### 📚 Knowledge Base")

        if api_key:
            client, collection = init_chromadb(api_key)
            if collection:
                count = collection.count()
                if count == 0:
                    if st.button("📥 Load Topic Guides"):
                        with st.spinner("Loading knowledge base..."):
                            loaded = load_guides(collection)
                            st.session_state.kb_loaded = True
                            st.success(f"Loaded {loaded} chunks!")
                            st.rerun()
                else:
                    st.success(f"✅ {count} chunks loaded")
                    if st.button("🔄 Reload"):
                        all_ids = collection.get()["ids"]
                        if all_ids:
                            collection.delete(ids=all_ids)
                        load_guides(collection)
                        st.rerun()

        # Image upload section
        st.markdown("---")
        st.markdown("### 📷 Photo Analysis")
        uploaded_image = st.file_uploader(
            "Upload a photo",
            type=["jpg", "jpeg", "png"],
            key="image_uploader"
        )
        if uploaded_image:
            st.image(uploaded_image, caption="Uploaded image", use_container_width=True)
            st.session_state.uploaded_image = uploaded_image.getvalue()
        else:
            st.session_state.uploaded_image = None

    # Main content area
    if not api_key:
        st.info("👈 Enter your OpenAI API key in the sidebar to get started")
        return

    client, collection = init_chromadb(api_key)
    if not collection:
        st.error("Failed to initialize. Check API key.")
        return

    if collection.count() == 0:
        st.warning("📥 Click 'Load Topic Guides' in the sidebar to load the knowledge base")
        return

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                with st.expander("📚 Sources"):
                    for s in message["sources"]:
                        st.markdown(f"- **{s['topic']}** > {s['section']}")

    # Show hint if image is uploaded
    if st.session_state.get("uploaded_image"):
        st.info("📷 Image uploaded! Ask a question about it (e.g., 'What's wrong with this pool?' or 'How do I fix this?')")

    # Chat input
    if prompt := st.chat_input("Ask about pool service..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            has_image = st.session_state.get("uploaded_image") is not None

            with st.spinner("Analyzing..." if has_image else "Searching..."):
                # Search knowledge base
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
                    st.markdown(response)
                    st.session_state.uploaded_image = None
                elif context:
                    response = generate_response(prompt, context, api_key)
                    st.markdown(response)
                else:
                    response = "I couldn't find relevant information for that question."
                    st.markdown(response)

                if metadatas:
                    sources = [{"topic": m["topic"], "section": m["section"]} for m in metadatas]
                    with st.expander("📚 Sources"):
                        for s in sources[:3]:
                            st.markdown(f"- **{s['topic']}** > {s['section']}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "sources": sources
                    })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })


if __name__ == "__main__":
    main()
