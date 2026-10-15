import os
import asyncio

from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv


load_dotenv()

fast_llm = ChatOpenAI(
        model="openai/gpt-oss-120b",
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
        temperature=0,
)

smart_llm = ChatOpenAI(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    temperature=0,
)

def router_logic(query : str) -> str:
    query_lower = query.lower()
    
    #step 1 - weight dictionary
    weights = {
    # complex words
    "analyse" : 3 , "anology" :1, "write code" : 3, "script" : 3, "debug" : 3, "algorithm" : 3,
    "function" : 3, "theory" : 2, "physics" : 2, "write" : 3 ,"describe" : 1, "explain" : 1,

    #simple word logic
    "how to" : -1, "what is": -1, "solve" : 1, "why" : 1, "how does" : 1, "add" : -1, "+" : -1, "-": -1, "*" : -1, "calculate" : -1, "list": -1,
        "translate" : -1, "who is" : -1, "meaning": -1,
    }

    #step 2 - scoring system
    score = 0
    for words, points in weights.items():
        if words in query:
            score += points
        
    #step 3 - length heuristic
    is_len = 0
    if len(query) > 60:
        is_len = 1
    else:
        is_len = -1

    #step 3 - final decision
    if score > 0 or is_len > 0: # Added explicit check
        return "complex"
    else:
        return "simple"

async def main(query : str):
    client = MultiServerMCPClient({
        "file_reader" : {
        "transport": "stdio",
        "command" : "python",
        "args": [str(Path("D:/Documents/Project Janus/mcp_tool.py"))],
        }
    })
        
    tools = await client.get_tools()
        
    agent1 = create_agent(fast_llm, tools)
    agent2 = create_agent(smart_llm,tools)

    decision = router_logic(query)

    if "complex" in decision:
        print("Using Smart Model llama-3.3-70b-versatile\n")  
        response = await agent2.ainvoke({"messages" : [("human", query)]})
        last_message = response["messages"][-1]
    else:
        print("Using Fast Model gpt-os-120b\n")
        response = await agent1.ainvoke({"messages" : [("human", query)]})
        last_message = response["messages"][-1]

    return last_message.content
    

if __name__ == "__main__":
    user_query = input("Ask Janus:" )
    try:
        answer = asyncio.run(main(user_query))
        print(f"\n Answer : {answer}")
    except Exception as e:
        print(f"An error occured: {e}")
   
