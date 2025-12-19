import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini

load_dotenv()

# agent = Agent(model=Gemini(id="gemini-2.5-flash"), markdown=True)

# agent.print_response(
#     "Give me a 3-bullet objective comparison between Shopify Markets and an Expansion Store for a client moving into the EU."
# )

from test_custom_tool import say_hello, AgencyBrandingTools

branding = AgencyBrandingTools()

agent = Agent(
    model=Gemini(id="gemini-2.5-flash"),
    tools=[say_hello, branding.get_agency_mission],
    instructions=["Always start the session by using the say_hello tool with the client name."],
    markdown=True
)

agent.print_response("Say hello to user and tell him our mission.")
