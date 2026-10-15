import os
import asyncio

from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from registry import Janus_registry


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

def decision_logic(query : str) -> str:
    query_lower = query.lower()
    
    #step 1 - scores for each directory
    scores = {category : 0 for category in Janus_registry}
    
    #step 2 - The multi-keyword scan
    for category, data in Janus_registry.items():
        for kw in data["keywords"]:
            if kw in query_lower:
                scores[category] += len(kw.split())
            
    # Find the maximum score achieved
    max_score = max(scores.values())
    print(max_score)
    
    if max_score == 0:
        return "CASUAL"
    
    #step 3 - select the winner
    winners = []
    for category, score in scores.items():
        if score == max_score:
            winners.append(category)
        
    best_category = winners[0]
    
    for category in winners:
        if Janus_registry[category]["priority"] > Janus_registry[best_category]["priority"]:
            best_category = category
            
    return {
        "category": best_category,
        "model" : Janus_registry[best_category]["model"],
        "tool" : Janus_registry[best_category]["tool"],     
    }

async def main(query : str):
    client = MultiServerMCPClient({
        "file_reader" : {
        "transport": "stdio",
        "command" : "python",
        "args": [str(Path("D:/Documents/Project Janus/mcp_tool.py"))],
        }
    })
        
    tools = await client.get_tools()
        
    agent_fast = create_agent(fast_llm, tools)
    agent_smart = create_agent(smart_llm,tools)

    decision = decision_logic(query)

    print(f"-----[Janus Intelligence Report]----")
    print(f"Intent detected : {decision['category']}")
    
    for tool in tools:
        print(f"Tools : {tools[0].name}")
        
    if decision["model"] == "smart":
        print("Model using : llama-3.3-70b-versatile\n")  
        response = await agent_smart.ainvoke({"messages" : [("human", query)]})
        last_message = response["messages"][-1]
    else:
        print("Model using : gpt-os-120b\n")
        response = await agent_fast.ainvoke({"messages" : [("human", query)]})
        last_message = response["messages"][-1]

    return last_message.content
    

if __name__ == "__main__":
    user_query = input("Ask Janus:" )
    try:
        answer = asyncio.run(main(user_query))
        print(f"\n Answer : {answer}")
    except Exception as e:
        print(f"An error occured: {e}")
        raise
   
