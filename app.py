import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio

def create_app(chain, portfolio):
    st.title("📧 Simple Cold Email Generator (Groq + Chroma)")

    url = st.text_input("Enter job posting URL:", placeholder="https://careers.example.com/job123")
    submit = st.button("Generate Cold Email")

    if submit:
        with st.spinner("Fetching job posting..."):
            try:
                loader = WebBaseLoader([url])
                raw_text = loader.load().pop().page_content
                st.write("✅ Fetched job posting text.")

                portfolio.load_portfolio()

                skills = raw_text.lower().split()[:10]  # take first 10 words as keywords
                st.write(f"🔎 Keywords for matching: {skills}")

                relevant_links = portfolio.query_links(skills)
                if not relevant_links:
                    st.warning("No matching portfolio projects found!")
                else:
                    st.success(f"Found {len(relevant_links)} matching portfolio projects.")
                    email = chain.write_mail(raw_text, relevant_links)
                    st.subheader("📨 Generated Cold Email")
                    st.code(email, language="markdown")
            except Exception as e:
                st.error(f"❌ Error: {e}")

if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    chain = Chain()
    portfolio = Portfolio()
    create_app(chain, portfolio)
