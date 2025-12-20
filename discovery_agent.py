import json
import re
import streamlit as st
from agno.agent import Agent
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Optional
from pydantic import BaseModel, Field
from agno.models.google import Gemini
from agno.tools.shopify import ShopifyTools
from agno.models.perplexity import Perplexity
from agno.tools.duckduckgo import DuckDuckGoTools


class ShopifyConstraint(BaseModel):
    category: str = Field(..., description="API, Checkout, Data Model, or UI")
    requirement: str = Field(..., description="The technical mandate.")
    limit_warning: Optional[str] = Field(
        None, description="Platform limits (e.g., 2048 variants, 20/sec Plus API rate)."
    )
    priority: str = Field(..., description="Must-have vs Nice-to-have")


class JiraTicket(BaseModel):
    title: str
    description: str
    ticket_type: str = Field(..., description="Story, Task, or Spike")
    priority: str


class DiscoveryBlueprint(BaseModel):
    strategy_overview: str
    technical_constraints: List[ShopifyConstraint]
    backlog: List[JiraTicket]


load_dotenv()
st.set_page_config(page_title="Shopify Architect Discovery", layout="wide")


def extract_json_from_text(text: str) -> Optional[str]:
    """Extract JSON from text that might be wrapped in markdown code blocks or have extra text."""
    if not text or not text.strip():
        return None

    # Try to find JSON in markdown code blocks (```json ... ``` or ``` ... ```)
    json_block_pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
    match = re.search(json_block_pattern, text, re.DOTALL)
    if match:
        return match.group(1)

    # Try to find JSON object directly in the text
    json_object_pattern = r"\{.*\}"
    match = re.search(json_object_pattern, text, re.DOTALL)
    if match:
        return match.group(0)

    # If no pattern matches, return the original text (might be pure JSON)
    return text.strip()


@st.cache_resource
def get_discovery_agent():
    current_year = datetime.now().year
    json_example = {
        "strategy_overview": "Unified Shopify Markets architecture setup...",
        "technical_constraints": [
            {
                "category": "Checkout",
                "requirement": "International duties calculated via Shopify Markets.",
                "limit_warning": "Must use Checkout UI Extensions; checkout.liquid is deprecated.",
                "priority": "Must-have",
            }
        ],
        "backlog": [
            {
                "title": "Configure Shopify Markets for UK/EU",
                "description": "Set up localized domains and tax-inclusive pricing.",
                "ticket_type": "Task",
                "priority": "High",
            }
        ],
    }

    return Agent(
        # model=Gemini(id="gemini-2.0-flash-exp"),
        model=Perplexity(id="sonar"),
        tools=[ShopifyTools(), DuckDuckGoTools()],
        # output_schema=DiscoveryBlueprint,
        description=f"You are a Staff Technical Architect. You VALIDATE requirements against Shopify {current_year} limits.",
        instructions=[
            "1. Identify the 'Business Intent' from the transcript.",
            f"2. Cross-reference requests against Shopify {current_year} Limits:",
            "   - Variants: Now up to 2,048.",
            "   - API: Plus stores have 10x rate limits (20 req/sec REST, 1000 pts/sec GraphQL).",
            "   - Checkout: Must use Checkout UI Extensions (liquid is dead).",
            "3. If a request violates these or is high-risk, flag it in 'limit_warning'.",
            "4. Output strictly according to the DiscoveryBlueprint schema.",
            f"5. Here is a sample of the DiscoveryBlueprint JSON schema you must follow: {json_example}",
            "6. Limit to the five most critical constraints and five most critical backlog items.",
            "7. Limit strategy_overview to 3 sentences. Limit description for Jira tickets to 120 characters. ",
        ],
    )


agent = get_discovery_agent()

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
            response = agent.run(transcript_input)

            if isinstance(response.content, DiscoveryBlueprint):
                st.session_state.blueprint = response.content
            elif isinstance(response.content, str):
                try:
                    json_str = extract_json_from_text(response.content)

                    if not json_str:
                        st.error(
                            "No JSON found in agent response. Response appears to be empty or invalid."
                        )
                        st.write(
                            "Raw Output for debugging:",
                            response.content[:500] if response.content else "(empty)",
                        )
                    else:
                        blueprint_dict = json.loads(json_str)
                        blueprint = DiscoveryBlueprint(**blueprint_dict)
                        st.session_state.blueprint = blueprint
                        st.success("Successfully parsed JSON from agent response!")
                except json.JSONDecodeError as e:
                    st.error(f"Failed to parse JSON: {e}")
                    st.write(
                        "**Extracted JSON string:**",
                        json_str[:500] if json_str else "(none)",
                    )
                    st.write(
                        "**Raw Output for debugging:**",
                        response.content[:1000] if response.content else "(empty)",
                    )
                except ValueError as e:
                    st.error(f"Failed to validate JSON structure: {e}")
                    st.write(
                        "**Extracted JSON string:**",
                        json_str[:500] if json_str else "(none)",
                    )
                    st.write(
                        "**Raw Output for debugging:**",
                        response.content[:1000] if response.content else "(empty)",
                    )
            else:
                st.error("Unexpected response format.")

if "blueprint" in st.session_state:
    bp: DiscoveryBlueprint = st.session_state.blueprint
    st.divider()

    tab1, tab2, tab3 = st.tabs(["🏗️ Strategy", "⚠️ Constraints", "🎫 Jira Backlog"])

    with tab1:
        st.subheader("Architectural Strategy")
        st.markdown(bp.strategy_overview)

    with tab2:
        st.subheader("Technical Guardrails")
        if bp.technical_constraints:
            # Convert list of objects to list of dicts for the table
            st.table([c.model_dump() for c in bp.technical_constraints])
        else:
            st.info("No specific constraints identified.")

    with tab3:
        st.subheader("Validated Jira Tickets")
        for ticket in bp.backlog:
            with st.expander(
                f"{ticket.ticket_type}: {ticket.title} ({ticket.priority} Priority)"
            ):
                st.write(ticket.description)


with st.sidebar:
    st.title("⚙️ Agent Settings")
    st.info("Connected to: Perplexity Sonar")

    if "blueprint" in st.session_state:
        # Helper for easy copy-pasting
        full_md = f"# Strategy\n{bp.strategy_overview}\n\n# Tickets"
        full_md += "\n".join([f"\n**Title**:\n{t.title}\n\n**Description**:\n{t.description}\n\n**Ticket type**:\n{t.ticket_type}\n\n**Priority**:\n{t.priority}" for t in bp.backlog])
        full_md += f"\n\n# Technical Constraints"
        full_md += "\n".join([f"\n**Category**:\n{t.category}\n\n**Requirement**:\n{t.requirement}\n\n**Limit warning**:\n{t.limit_warning}\n\n**Priority**:\n{t.priority}" for t in bp.technical_constraints])

        st.download_button(
            label="Download TDD (.md)",
            data=full_md,
            file_name="discovery_output.md",
            mime="text/markdown",
        )
