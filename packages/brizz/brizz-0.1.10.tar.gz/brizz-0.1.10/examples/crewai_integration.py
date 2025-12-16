"""Simple CrewAI integration example with Brizz SDK."""

import os
import sys

from crewai import Agent, Crew, Task
from dotenv import load_dotenv

from brizz import Brizz

load_dotenv()

# Initialize SDK
Brizz.initialize(
    base_url="http://localhost:4318",
    disable_batch=True,
    app_name="crewai-example",
)

# Check for API key (if using OpenAI as LLM)
if not os.getenv("OPENAI_API_KEY"):
    print("Set OPENAI_API_KEY environment variable")
    sys.exit(1)

# Create simple agent with automatic instrumentation
research_agent = Agent(
    role="Research Analyst",
    goal="Find and summarize information about AI topics",
    backstory="You are an experienced researcher with attention to detail "
    "and ability to synthesize complex information",
    verbose=True,
)

# Define task
research_task = Task(
    description="Research and summarize the current state of AI safety",
    expected_output="A 3-sentence summary of key AI safety developments",
    agent=research_agent,
)

# Create crew
crew = Crew(agents=[research_agent], tasks=[research_task], verbose=True)

# Execute crew with automatic instrumentation
result = crew.kickoff()

print(f"Crew Result: {result}")

# Emit custom event
Brizz.emit_event(
    name="ai.crew_completed",
    attributes={"agent_count": 1, "task_count": 1, "success": True},
)
