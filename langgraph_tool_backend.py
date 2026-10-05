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

#llm
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite"
)

#tools
search_tools=DuckDuckGoSearchRun(region="us-en")

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

