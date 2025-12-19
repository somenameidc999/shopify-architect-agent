# 🚀 Shopify Discovery Automation Agent
An internal tool designed to convert messy discovery transcripts (Wispr Flow, Google Meet) 
into structured Technical Design Documents (TDD) and validated Jira backlogs.

---

## 🏗️ Core Architecture
This tool leverages **Agno** (formerly Phidata) and **Gemini 3 Flash** to perform 
agentic reasoning. Unlike basic GPT wrappers, it uses a **Plan-and-Learn** loop 
to validate architectural decisions against real-world Shopify constraints.

### The Stack:
- **Reasoning:** Gemini 3 Flash (Thinking Mode: HIGH)
- **Framework:** Agno (Agentic Orchestration)
- **UI:** Streamlit (Wide Layout)
- **Tools:** `ShopifyTools`, `DuckDuckGoTools`

---

## ✨ Key Features
- **Voice-to-Blueprint:** Paste 10-minute brain dumps from Wispr Flow and get a downloadable TDD.
- **Shopify Context:** Agent is programmed to prioritize **Shopify Functions** over 
Legacy Scripts and monitors **GraphQL rate limits**.
- **Automated Backlog:** Generates structured Jira tickets (Stories, Tasks, Spikes) 
ready for import.
- **Mermaid Diagrams:** (Optional) Renders architectural flowcharts directly in the UI.

---

## 🛠️ Installation & Setup

### Prerequisites:
- [uv](https://github.com/astral-sh/uv) (Extremely fast Python package manager)
- Google AI Studio API Key (Gemini 3 Flash access)

### 1. Clone & Init
```bash
git clone https://github.com/somenameidc999/shopify-architect-agent.git
cd shopify-architect-agent
uv init
```

### 2. Configure Environment
Create a `.env` file in the root:
```bash
GOOGLE_API_KEY=your_key_here
# Optional: For live store lookups
SHOPIFY_SHOP_URL=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_xxx
```

### 3. Run the App
```bash
uv run streamlit run discovery_agent.py
```

---

### 📖 Usage Workflow
**Record**: Use Wispr Flow during a discovery call to record high-level architectural intent.

**Input**: Paste the raw transcript or the "Gemini Notes" from Google Meet into the input box.

**Reason**: Click "Generate Blueprint." The agent will plan, research (if needed), and output the TDD.

**Export**: Download the Markdown file or copy the Jira tickets into the agency backlog.

---

### 📅 Roadmap
[ ] Jira API Integration: Direct "Push to Jira" button.

[ ] Knowledge Base: Point the agent to our agency's Internal-Best-Practices.pdf.

[ ] Cost Tracking: Dashboard to monitor token usage per discovery.

---