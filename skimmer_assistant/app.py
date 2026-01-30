"""
Skimmer Assistant - Pool Pro Knowledge Base
A RAG-powered chat app for pool service technicians
"""

import streamlit as st
import chromadb
from chromadb.utils import embedding_functions
import os
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
    .chat-message {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #E5ECF2;
    }
    .assistant-message {
        background-color: white;
        border-left: 4px solid #4795EC;
    }
    .source-box {
        background-color: #F0F7FD;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-size: 0.85rem;
        margin-top: 0.5rem;
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

# Initialize ChromaDB
@st.cache_resource
def init_chromadb():
    """Initialize ChromaDB with OpenAI embeddings"""

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY") or st.session_state.get("openai_api_key")

    if not api_key:
        return None, None

    # Create embedding function
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=api_key,
        model_name="text-embedding-3-small"
    )

    # Initialize ChromaDB
    client = chromadb.PersistentClient(path="./chroma_db")

    # Get or create collection
    collection = client.get_or_create_collection(
        name="pool_knowledge",
        embedding_function=openai_ef,
        metadata={"description": "Pool service technician knowledge base"}
    )

    return client, collection

def load_guides(collection):
    """Load topic guides into ChromaDB"""

    guides_path = Path("../topic_guides")

    if not guides_path.exists():
        # Try alternate path
        guides_path = Path("/sessions/exciting-beautiful-babbage/mnt/nidhisingh/topic_guides")

    if not guides_path.exists():
        st.error("Topic guides folder not found!")
        return 0

    # Check if already loaded
    if collection.count() > 0:
        return collection.count()

    documents = []
    metadatas = []
    ids = []

    doc_id = 0

    for guide_file in sorted(guides_path.glob("*.md")):
        if guide_file.name == "README.md":
            continue

        content = guide_file.read_text()

        # Extract topic from filename
        topic = guide_file.stem.replace("_", " ").title()
        if topic[0:2].isdigit():
            topic = topic[3:]  # Remove number prefix

        # Split into chunks by ## headers
        chunks = []
        current_chunk = ""
        current_header = topic

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

        # Add last chunk
        if current_chunk.strip():
            chunks.append({
                "content": current_chunk.strip(),
                "header": current_header,
                "source": guide_file.name
            })

        # Add chunks to lists
        for chunk in chunks:
            documents.append(chunk["content"])
            metadatas.append({
                "source": chunk["source"],
                "topic": topic,
                "section": chunk["header"]
            })
            ids.append(f"doc_{doc_id}")
            doc_id += 1

    # Add to collection
    if documents:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    return len(documents)

def search_knowledge(collection, query, n_results=5):
    """Search the knowledge base"""

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    return results

def generate_response(query, context, api_key):
    """Generate response using OpenAI"""

    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    system_prompt = """You are Skimmer Assistant, a helpful expert for pool service technicians.

Answer questions using ONLY the provided context. Be specific with:
- Exact numbers (pH levels, chemical dosages, temperatures)
- Step-by-step procedures when applicable
- Safety warnings when relevant

If the context doesn't contain enough information, say so honestly.
Keep answers concise but complete. Format with bullet points for lists."""

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

# Main app logic
def main():
    # API Key input
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = ""

    # Sidebar for settings
    with st.sidebar:
        st.markdown("### ⚙️ Settings")

        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.openai_api_key,
            help="Get your API key from platform.openai.com"
        )

        if api_key:
            st.session_state.openai_api_key = api_key
            os.environ["OPENAI_API_KEY"] = api_key

        st.markdown("---")
        st.markdown("### 📚 Knowledge Base")

        if api_key:
            client, collection = init_chromadb()

            if collection:
                count = collection.count()

                if count == 0:
                    if st.button("📥 Load Topic Guides"):
                        with st.spinner("Loading guides..."):
                            loaded = load_guides(collection)
                            st.success(f"Loaded {loaded} chunks!")
                            st.rerun()
                else:
                    st.success(f"✅ {count} chunks loaded")

                    if st.button("🔄 Reload Guides"):
                        collection.delete(where={})
                        load_guides(collection)
                        st.rerun()

        st.markdown("---")
        st.markdown("### 📖 Topics Covered")
        st.markdown("""
        **Core Topics:**
        - Water Chemistry & Testing
        - Pumps, Filters & Heaters
        - Saltwater Pool Systems
        - Troubleshooting

        **Operations:**
        - Installation Procedures
        - Manual Vacuuming
        - Service Documentation
        - Leak Detection

        **Professional:**
        - CPO Certification
        - ADA Compliance
        - Safety & Liability
        - Technician Training

        **Systems:**
        - Automation (IntelliConnect)
        - Heater Safety Systems
        - Business Operations
        """)

    # Check for API key
    if not st.session_state.openai_api_key:
        st.info("👈 Please enter your OpenAI API key in the sidebar to get started.")
        st.markdown("""
        **To get an API key:**
        1. Go to [platform.openai.com](https://platform.openai.com)
        2. Sign up or log in
        3. Go to API Keys section
        4. Create a new key
        """)
        return

    # Initialize DB
    client, collection = init_chromadb()

    if not collection:
        st.error("Failed to initialize database. Check your API key.")
        return

    # Check if guides are loaded
    if collection.count() == 0:
        st.warning("📥 Click 'Load Topic Guides' in the sidebar to load the knowledge base.")
        return

    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                with st.expander("📚 Sources"):
                    for source in message["sources"]:
                        st.markdown(f"- **{source['topic']}** > {source['section']}")

    # Chat input
    if prompt := st.chat_input("Ask about pool service..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Search knowledge base
        with st.chat_message("assistant"):
            with st.spinner("Searching knowledge base..."):
                results = search_knowledge(collection, prompt)

                if results and results["documents"] and results["documents"][0]:
                    context = results["documents"][0]
                    metadatas = results["metadatas"][0]

                    # Generate response
                    response = generate_response(
                        prompt,
                        context,
                        st.session_state.openai_api_key
                    )

                    st.markdown(response)

                    # Show sources
                    sources = [
                        {"topic": m["topic"], "section": m["section"]}
                        for m in metadatas
                    ]

                    with st.expander("📚 Sources"):
                        for source in sources[:3]:
                            st.markdown(f"- **{source['topic']}** > {source['section']}")

                    # Save to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "sources": sources
                    })
                else:
                    st.markdown("I couldn't find relevant information in the knowledge base for that question.")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "I couldn't find relevant information in the knowledge base for that question."
                    })

if __name__ == "__main__":
    main()
