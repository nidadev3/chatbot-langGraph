from langgraph.graph import StateGraph,START,END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage,HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
import sqlite3
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from dotenv import load_dotenv
import sqlite3
import requests
import os

load_dotenv()

#llm
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite"
)

#stock api key
api_key = os.getenv("STOCK_API_KEY")

#tools
search_tool=DuckDuckGoSearchRun(region="us-en")

@tool
def calculator(first_num:float, second_num:float,operation:str)->dict:
    """
    Perform a basic arithmeti operation on two numbers.
    Supported operations:add, sub, mul, div
  
    """

    try:
        if operation=="add":
            result=first_num+second_num
        elif operation=="sub":
             result = first_num - second_num
        elif operation == "mul":
             result = first_num * second_num 
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}

        return {"first_num":first_num,"second_num":second_num, "operation":operation, "result":result}
    except Exception as e:
        return {"error":str(e)}


@tool
def get_stock_price(symbol:str)->dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"

    r = requests.get(url)
    return r.json()


tools=[search_tool, get_stock_price, calculator]
llm_with_tools=llm.bind_tools(tools)



#State
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Nodes
def chat_node(state:ChatState):
    """
    LLM node that may answer or request a tool call.
    
    """
    messages=state["messages"]
    response=llm_with_tools.invoke(messages)
    return {"messages":[response]}
tool_node=ToolNode(tools)


#checkpointer
conn = sqlite3.connect(database="chatbot.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)
