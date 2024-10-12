from dotenv import find_dotenv, load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from langchain.load import dumps, loads
from dash import Dash, dcc, html, callback, Output, Input, State
from dash import dash_table
import pandas as pd

# Activate API keys
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

# Set up the OpenAI LLM with GPT-4 or GPT-3.5-turbo-0125
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0125")

# TavilySearchResults tool to help search the web
tavily_tool = TavilySearchResults()
tools = [tavily_tool]

# Modified system prompt for structured response
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """You are an assistant. 
        Please return only the murder statistics for each city in the following structured format:
        
        City: <city name>
        Year: <year>, Murder Count: <number>
        
        Repeat this format for each year and each city. 
        Do not include any additional text or explanations.
        """),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)


# Create the agent with search and extraction tools
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
)

# Function to process user input, execute agent, and get the response
def process_chat(agent_executor, user_input, chat_history):
    response = agent_executor.invoke({
        "input": user_input,
        "chat_history": chat_history
    })
    return response["output"]

# Function to extract data for multiple cities
def extract_murder_data(response):
    # Split the response by "City:" to handle each city separately
    city_data = response.split("City:")

    # Initialize a dictionary to store data for each city
    city_tables = {}

    for city_info in city_data:
        if city_info.strip():  # Check if city_info is not empty
            # Split the city info into lines by "Year:"
            lines = city_info.strip().splitlines()

            if len(lines) > 1:  # Ensure there are lines to process
                city_name = lines[0].strip()  # Extract the city name from the first line

                # Initialize a list to store Year and Murder Count for this city
                data = []

                # Parse the remaining lines for Year and Murder Count
                for line in lines[1:]:
                    if "Year:" in line and "Murder Count:" in line:
                        parts = line.split(", Murder Count:")
                        if len(parts) == 2:
                            year = parts[0].replace("Year:", "").strip()
                            murder_count = parts[1].strip()

                            # Append the data to the list
                            data.append({"Year": year, "Murder Count": murder_count})

                if data:
                    # Store the data in a DataFrame for this city
                    df = pd.DataFrame(data)
                    city_tables[city_name] = df

    return city_tables




# Dash web app with enhanced styling
app = Dash(__name__, external_stylesheets=["https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"])

app.layout = html.Div(
    className="container mt-4",  # Bootstrap container with top margin
    children=[
        html.H2(
            "Ask me anything. I'm your personal assistant that can search the web and extract data",
            className="text-center mb-4",  # Center text with bottom margin
            style={"color": "#2c3e50"}
        ),
        dcc.Input(
            id="my-input", 
            type="text", 
            debounce=True, 
            placeholder="look for {City} homicide data from {year} to {year} and extract in a table",
            className="form-control mb-3",  # Use Bootstrap class for input styling
            style={"width": "50%", "height": "40px", "border-radius": "10px"}
        ),
        html.Button(
            "Submit", 
            id="submit-query", 
            className="btn btn-primary mb-4",  # Bootstrap button style
            style={"backgroundColor": "#2980b9", "color": "white", "padding": "10px 20px", "border-radius": "8px"}
        ),
        dcc.Store(id="store-it", data=[]),  # To store the chat history
        html.P(id="response-space", className="text-muted", style={"font-size": "16px"}),  # Output space for assistant's response
        html.Div(id="table-container", className="mt-4")  # Div to hold all city tables with margin on top
    ]
)

# Callback to interact with the agent, handle user input, and update the response and tables
@callback(
    Output("response-space", "children"),
    Output("store-it", "data"),
    Output("table-container", "children"),  # Output for multiple tables
    Input("submit-query", "n_clicks"),
    State("my-input", "value"),
    State("store-it", "data"),
    prevent_initial_call=True
)
def interact_with_agent(n, user_input, chat_history):
    if len(chat_history) > 0:
        chat_history = loads(chat_history)  # Deserialize the chat history (convert from JSON to Python object)

    # Process the user input through the agent
    response = process_chat(agent_executor, user_input, chat_history)
    
    # Debugging: print the raw response from LLM
    print("LLM Response:", response)  # Add this to see the LLM response format

    # Append the interaction to the chat history
    chat_history.append(HumanMessage(content=user_input))
    chat_history.append(AIMessage(content=response))

    history = dumps(chat_history)  # Serialize the chat history (convert from Python object to JSON)

    # Extract data for multiple cities
    city_tables = extract_murder_data(response)

    # Generate a separate Dash DataTable for each city
    tables = []
    for city, df in city_tables.items():
        tables.append(html.H3(f"{city}", className="mt-4", style={"color": "#3498db"}))  # City name header with margin
        tables.append(
            dash_table.DataTable(
                columns=[{"name": col, "id": col} for col in df.columns],
                data=df.to_dict('records'),
                style_cell={"textAlign": "center", "padding": "10px"},  # Center the text and add padding
                style_header={
                    "backgroundColor": "#2980b9",
                    "color": "white",
                    "fontWeight": "bold",
                    "border": "1px solid black"
                },
                style_data={
                    "border": "1px solid black",
                    "backgroundColor": "#ecf0f1"
                }
            )
        )

    # Return the assistant's response, the updated chat history, and the city tables
    return f"Assistant: {response}", history, tables


# Run the Dash web server
if __name__ == '__main__':
    app.run_server(debug=True)
