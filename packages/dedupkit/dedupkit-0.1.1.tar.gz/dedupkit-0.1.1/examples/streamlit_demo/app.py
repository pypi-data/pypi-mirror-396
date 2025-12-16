import streamlit as st
from dedupkit import Deduplicator
from dedupkit.providers import LocalEmbeddingProvider
from dedupkit.storage import MemoryStorage


@st.cache_resource
def get_deduplicator():
    """Create deduplicator once, reuse across reruns."""
    dedup = Deduplicator(
        embedding=LocalEmbeddingProvider(),
        storage=MemoryStorage(),
        threshold=0.7
    )

    # Pre-load sample items
    samples = [
        ("Login button is not working", "BUG-001"),
        ("Payment form crashes on submit", "BUG-002"),
        ("Profile picture upload fails", "BUG-003"),
        ("Cannot reset password", "BUG-004"),
    ]
    for text, item_id in samples:
        dedup.add(text, item_id=item_id, metadata={"source": text})

    return dedup


def render_sidebar(dedup: Deduplicator):
    st.header("➕ Add Items")

    # Input fields
    new_text = st.text_area("Text", height=100, placeholder="Enter text to add...")
    new_id = st.text_input("ID (optional)", placeholder="e.g., BUG-001")

    # Add button
    if st.button("Add Item", type="primary"):
        if new_text.strip():
            item_id = dedup.add(
                text=new_text,
                item_id=new_id if new_id.strip() else None,
                metadata={"source": new_text}
            )
            st.success(f"✅ Added: {item_id}")
        else:
            st.error("Text cannot be empty")

    # Show count
    st.divider()
    st.metric("Total Items", len(dedup))


def render_main(dedup: Deduplicator):
    st.header("🔍 Check for Duplicates")

    query = st.text_area("Enter text to check", height=100, placeholder="Enter text to find duplicates...")
    threshold = st.slider("Similarity Threshold", 0.0, 1.0, 0.70, 0.05)

    if st.button("Check", type="primary"):
        if query.strip():
            result = dedup.check(query, threshold=threshold)

            st.divider()

            # Show result status
            if result.is_duplicate:
                st.warning(f"⚠️ Found {len(result.matches)} potential duplicate(s)!")
            else:
                st.success("✅ No duplicates found")

            # Show matches
            for match in result.matches:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{match.id}**")
                        if match.metadata and "source" in match.metadata:
                            st.caption(match.metadata["source"])
                        st.progress(match.similarity)
                    with col2:
                        st.metric("Similarity", f"{match.similarity:.0%}")
        else:
            st.error("Enter text to check")


def main():
    st.set_page_config(page_title="DedupKit Demo", page_icon="🔍")
    st.title("🔍 DedupKit Demo")
    st.markdown("Semantic deduplication using embeddings")

    dedup = get_deduplicator()

    # === Sidebar: Add Items ===
    with st.sidebar:
        render_sidebar(dedup)

    # === Main: Check for Duplicates ===
    render_main(dedup)


if __name__ == "__main__":
    main()