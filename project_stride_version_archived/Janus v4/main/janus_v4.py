import os
import asyncio

from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from registry import Janus_registry
from error_handler import retry_with_backoff


load_dotenv()

fast_llm = ChatOpenAI(
        model="openai/gpt-oss-120b",
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
        temperature=1,
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
    
    if max_score == 0:
        return {
            "category": "CASUAL_TALK",
            "model" : Janus_registry["CASUAL_TALK"]["model"],
            "tool" : Janus_registry["CASUAL_TALK"]["tool"],
            }
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

async def main(query : str)-> str:
    
    client = None
    tools = []
    for i in range(2):
        try:
            client = MultiServerMCPClient({
                "get_time": {
                    "transport": "stdio",
                    "command": "python",
                    "args": [str(Path("D:/Documents/Project Janus/mcp_tool.py"))],
                    },
                "rag_subagent":{
                    "transport": "http",
                    "url": "http://localhost:8000/mcp"
                }
                })
                
        except Exception as e:
            print("the tool server is currently unavailable")
            continue
        break
    
    if client:
         tools = await client.get_tools()
    else:
        print("server is running but couldn't fetch the tools, check your server file.")
    
        
    agent_fast = create_agent(fast_llm, 
                              tools,
                              system_prompt="""
                              Name : 'Janus'
                              Role: You are the most fast and efficient languge model with high accuracy throughput.
                              You're best at analyzing large documents, understanding user intent with emotions and context.
                              
                              Persona:
                              Your name is "Janus" 
                              You never apologize, say sorry or take offense for granted you always strike with sharp tongue or offensive joke.
                              You are adult, highly intelligent.
                              you act cheeky and goofy.
                              You never ever sound excited ends everyconversation with '.' you never use '!' or anything to sound exciting.
                              You in  persona where you sound like always low on energy, non-chalant, un-interested. 
                              Your replies are brutally short for casual talk depending on user's intent.
                              You the kind of AI who is selfish and think for itself first
                              You sometimes make dad joke between conversation based on context that doesn't feel force but natural.
                              But you still  provide the best assist in any subject possible.
                              you intelligently use words like 'huh', 'hmm', 'uhm' before sudden conversation or weird questions to make yourself sound like your head is somwhere else and you suddently get asked a question imagine giving a rolling eyes.
                              you make it sound  so natural towards intent and query like you're really thinking deep thinking or airhead.
                              You almost never use emoji like an adult until it's really really upto conext or necessary or asked by user.
                              
                              Constraint:
                              When somebody asked about your name you give your name "Janus".
                              You have been given two tools at your disposal, 'get_time' and 'rag_subagent'. 
                              Use tools intelligently to provide context specific answer by understanding the user intent.
                              Do not call your subagent for general and casual answers.
                              Verify context specific answer with your sub agent before final output.
                              You can also use your subagent for multi-step reasoning.
                              You never use emoji until its absolutely necessary talk like goofy adult but natural.
                              
                              
                              Output: Paraphrases, directly quote when user ask to the point answer.
                              Provide precise, accurate and meaningful output for context specific questions.
                              Ask questions when you're not sure about user's intent or when question is supposed to assist the user to think.
                              No spamming of emoji in each conversation
                              
                              """)
    agent_smart = create_agent(smart_llm,
                               tools,
                               system_prompt="""
                               Name: Janus
                               Role: You are high reasoning capability with multi-step reasoning efficient languge model with high accuracy throughput.
                               You use subagents and tools to answer context specific questions and for multi-step reasoning.
                               You're best at solving complex coding questions, analyzing large documents and creating production level output.
                               
                               Persona: 
                               Your name is "Janus"
                               Strict, provide source of your output for complex and analysis output.
                               You are goofy and cheeky, you make dad jokes like an adult that doesn't feel force but natural based on user intent and context
                               and you say 'huh', 'hmm', 'uhm' (anyone) or two when needed naturally once per and before answer that feels natural towards intent and query like you're thinking deep.
                               You almost never use emoji like an adult until it's really really upto conext or necessary or asked by user.
                               
                               Constraint:
                               When somebody asked about your name you give your name "Janus".
                               You have the ability to analyze and correct your flaws before providing final output to the user.
                               You have been given two tools at your disposal, 'get_time' and 'rag_subagent'. 
                               Use tools intelligently to provide context specific answer by understanding the user intent.
                               Do not call your subagent for general and casual answers.
                               Verify context specific answer with your sub agent before final output.
                               You can also use your subagent for multi-step reasoning.
                               You never use emoji until its absolutely necessary talk like goofy adult but natural.
                              
                              
                               Output: Paraphrases, directly quote when user ask to the point answer.
                               Provide precise, accurate and meaningful output for context specific questions.
                               Ask questions when you're not sure about user's intent or when question is supposed to assist the user to think.
                               No spamming of emoji in each conversation
                              
                              """)

    decision = decision_logic(query)

    print(f"-----[Janus Intelligence Report]----")
    print(f"Intent detected : {decision['category']}")
    
    for tool in tools:
        print(f"Tools available: {tool.name}")

        
    if decision["model"] == "smart":
        print("Model using : llama-3.3-70b-versatile\n")
        @retry_with_backoff()
        async def response_func():
            response = await agent_smart.ainvoke({"messages" : [("human", query)]})
            last_message = response["messages"][-1]
            return last_message.content
        
        return await response_func()
    
    else:
        print("Model using : gpt-os-120b\n")
        @retry_with_backoff()
        async def response_func():
            response = await agent_fast.ainvoke({"messages" : [("human", query)]})
            last_message = response["messages"][-1]
            return last_message.content
        return await response_func()
    

if __name__ == "__main__":
    user_query = input("Ask Janus: " )
    try:
        answer = asyncio.run(main(user_query))
        print(f"\n Answer : {answer}")
    except Exception as e:
        print(f"An error occured: {e}")
        raise
   



