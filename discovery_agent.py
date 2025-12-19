import re
import textwrap
import streamlit as st
from agno.agent import Agent
from dotenv import load_dotenv

# from agno.tools.jira import JiraTools
from agno.models.google import Gemini

# from agno.tools.github import GithubTools
from agno.tools.shopify import ShopifyTools

# from agno.tools.postgres import PostgresTools
from agno.tools.duckduckgo import DuckDuckGoTools

load_dotenv()
st.set_page_config(page_title="Shopify Architect Discovery", layout="wide")


@st.cache_resource
def get_discovery_agent():
    return Agent(
        model=Gemini(id="gemini-3-flash-preview"),  # , thinking_level="HIGH"
        tools=[ShopifyTools(), DuckDuckGoTools()],
        description="You are a Senior Staff Technical Architect at a Shopify Plus agency.",
        instructions=textwrap.dedent(
            """
        You are a high-performing Technical Architect. 
        Analyze the provided transcript and generate:
        
        1. ARCHITECTURAL OVERVIEW: High-level technical strategy.
        2. TECHNICAL RISKS: Identify Shopify API limits or integration hurdles.
        3. JIRA BACKLOG: Generate a list of tickets for the development team. 
           For each ticket, provide:
           - Title: Clear, action-oriented name (e.g., 'SPIKE: NetSuite Inventory Webhook Auth')
           - Description: A technical summary of 'Definition of Done'.
           - Priority: High/Medium/Low based on the project phase.
    """
        ),
        markdown=True,
    )


agent = get_discovery_agent()

with st.sidebar:
    st.title("⚙️ Agent Settings")
    st.info("Connected to: Gemini 3 Flash")
    # if st.button("Clear Session"):
    #     st.rerun()


def parse_sections(text):
    """Uses regex to find content between the predefined headers."""
    sections = {
        "Overview": "No overview generated.",
        "Risks": "No technical risks identified.",
        "Jira": "No tickets generated.",
    }

    # Regex pattern: Find header, then capture everything until the next # Header or end of string
    overview_match = re.search(
        r"# ARCHITECTURAL OVERVIEW(.*?)(?=# TECHNICAL RISKS|# JIRA BACKLOG|$)",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    risks_match = re.search(
        r"# TECHNICAL RISKS(.*?)(?=# ARCHITECTURAL OVERVIEW|# JIRA BACKLOG|$)",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    jira_match = re.search(
        r"# JIRA BACKLOG(.*?)(?=# ARCHITECTURAL OVERVIEW|# TECHNICAL RISKS|$)",
        text,
        re.DOTALL | re.IGNORECASE,
    )

    if overview_match:
        sections["Overview"] = overview_match.group(1).strip()
    if risks_match:
        sections["Risks"] = risks_match.group(1).strip()
    if jira_match:
        sections["Jira"] = jira_match.group(1).strip()

    return sections


st.title("🚀 Shopify Rapid Discovery")
st.caption(
    "Convert voice dumps and meeting notes into validated Technical Design Documents."
)

transcript_input = st.text_area(
    "Paste Transcript (Wispr Flow or Google Meet Notes):",
    height=300,
    placeholder="Enter the messy details here...",
)

if st.button("Generate Blueprint", type="primary"):
    if not transcript_input:
        st.warning("Please enter a transcript first.")
    else:
        with st.spinner("Agent is reasoning through the architecture..."):
            # Use Agno's .run() to get the response object
            response = agent.run(transcript_input)

            # Store result in session state to keep it persistent
            st.session_state.raw_result = response.content
            st.session_state.sections = parse_sections(response.content)

if "sections" in st.session_state:
    st.divider()

    # We create tabs to separate the 3 core requirements
    tab1, tab2, tab3 = st.tabs(["🏗️ Overview", "⚠️ Technical Risks", "🎫 Jira Backlog"])

    with tab1:
        st.markdown(st.session_state.sections["Overview"])

    with tab2:
        if st.session_state.sections["Risks"] != "No technical risks identified.":
            st.warning("Critical Technical Considerations")

        st.markdown(st.session_state.sections["Risks"])

    with tab3:
        st.markdown(st.session_state.sections["Jira"])
        if st.session_state.sections["Jira"] != "No tickets generated.":
            st.download_button(
                label="Download TDD as Markdown",
                data=st.session_state.sections["Jira"],
                file_name="discovery.md",
                mime="text/markdown",
            )

    with st.sidebar:
        if st.checkbox("Show Raw Agent Output"):
            st.code(st.session_state.raw_result)
