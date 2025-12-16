# Conversational Graph

A Python package for building stateful, graph-based conversational agents. Control the flow of your AI conversations with precision using states, transitions, and tools.

## Installation

```bash
pip install conversational-graph-dev
```

## Features

- **Graph-Based Flow Control**: Define conversations as a graph of states and transitions.
- **State Management**: Manage conversation context and strict progression between logical steps.
- **Tool Integration**: Integrate HTTP request tools to specific states.
- **Data Modeling**: Strongly typed data extraction using Pydantic models.

## Quick Start

Here is a simple example of how to build a strict conversational flow for a loan assistant.

```python
from conversational_graph import ConversationalGraph, ConversationalDataModel, PreDefinedTool, HttpToolRequest

get_weather = PreDefinedTool().http_tool(HttpToolRequest(
        name="get_weather",
        description="Called when the user asks about the weather. This function will return the weather for the given location.",
        url="https://api.open-meteo.com/v1/forecast?latitude=21.1702&longitude=81.2402&current=temperature_2m",
        method="GET"
    )
)

# Provide Data Model with validation rules in descriptions for each field.
class LoanFlow(ConversationalDataModel):
    loan_type: str = Field(None, description="Type of loan: personal, home")
    annual_income: int = Field(None, description="Annual income of the applicant in INR")
    credit_score: int = Field(None, description="Credit score of the applicant. Must be between 300 and 850")
    property_value: int = Field(None, description="Value of the property for home loan in INR")
    loan_amount: int = Field(None, description="Desired loan amount in INR. MUST be greater than ₹11 lakh for approval")

loan_application = ConversationalGraph(
        name="Loan Application",
        DataModel= LoanFlow,
        off_topic_threshold=5,
        graph_type="STRICT"
    )
    
# Start Greeting
q0 = loan_application.state(
    name="Greeting",
    instruction="Welcome user and start the conversation and tell the weather",
    tool=get_weather
)

# Loan Type Selection
q1 = loan_application.state(
    name="Loan Type Selection",
    instruction="Ask user to select loan type. We only offer personal loan and home loan at the moment.",
)

# Personal Loan Details
q1a = loan_application.state(
    name="Personal Loan Details",
    instruction="Collect annual income and credit score for personal loan. Annual income must be > ₹5 lakh and credit score > 500."
)

# Home Loan Details
q1b = loan_application.state(
    name="Home Loan Details",
    instruction="Collect annual income, credit score, and property value for home loan. Annual income must be > ₹6 lakh, credit score > 650, and property value must be reasonable."
)

# Merged State → Loan Amount Collection
q2 = loan_application.state(
    name="Loan Amount Collection",
    instruction="Collect the desired loan amount. Minimum loan amount is ₹11 lakh for approval."
)


q2a = loan_application.state(
    name="Loan Amount Rejection",
    instruction="Inform user that the requested loan amount is below the minimum requirement of ₹11 lakh and politely end the application process."
)   

q2b = loan_application.state(
    name="Loan Amount Acceptance",
    instruction="Proceed to the next step of the application process as the requested loan amount meets the minimum requirement."
)

q3 = loan_application.state(
    name="Loan Application Complete",
    instruction="Inform user that the application has been submitted successfully"
)

# Master / Off-topic handler
q_master = loan_application.state(
    name="Off-topic Handler",
    instruction="Handle off-topic or inappropriate inputs respectfully and end the call politely",
    master=True
)


# Define Transitions

# Greeting → Loan Type Selection
loan_application.transition(
    from_state=q0,
    to_state=q1,
    condition="User ready to apply for loan"
)

# Branch from Loan Type Selection
loan_application.transition(
    from_state=q1,
    to_state=q1a,
    condition="User wants personal loan"
)

loan_application.transition(
    from_state=q1,
    to_state=q1b,
    condition="User wants home loan"
)

# Merge all branches → Loan Amount Collection
loan_application.transition(
    from_state=q1a,
    to_state=q2,
    condition="Personal loan details collected and verified"
)

loan_application.transition(
    from_state=q1b,
    to_state=q2,
    condition="Home loan details collected and verified"
)

# Loan Amount → Review and Confirm
loan_application.transition(
    from_state=q2,
    to_state=q2a,
    condition="Loan application rejected due to insufficient amount (< ₹11 lakh)"
)

loan_application.transition(
    from_state=q2,
    to_state=q2b,
    condition="Loan amount meets minimum requirement (≥ ₹11 lakh)"
)

# Review → Complete
loan_application.transition(
    from_state=q2b,
    to_state=q3,
    condition="User confirms submission of loan application"
)



```

## Core Concepts

### ConversationalGraph
The main entry point. It holds all your states and transitions.
- `name`: Name of your conversational graph.
- `DataModel`: A Pydantic model class that defines the schema for data you want to collect during the conversation.
- `off_topic_threshold`: Number of times the conversation can go off-topic before the flow jumps to the master state.
- `graph_type`: Currently supports "STRICT" for rigid flows.

### State
A node in the conversation graph.
- `name`: Name of the state.
- `instruction`: Instructions for the LLM on what to do in this state.
- `tool`: A Python function to execute in this state (optional).
- `master`: If True, this state acts as a master state (optional).
- `required_fields`: List of field names (matching your DataModel) that must be collected or present before the tool can run or the state is considered 'complete' (optional).

### Transition
Defines the valid paths between states.
- `from_state`: Source state name.
- `to_state`: Destination state name.
- `condition`: Description of when this transition should happen. The LLM uses this to decide the next step.


### Edge Cases
- There can be `zero or one` master state.
- Tools must be accessible.
- Every transition must point to an existing state.
- There can only be `one` start state.
