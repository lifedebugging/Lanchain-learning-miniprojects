import os
import uvicorn


from pydantic import BaseModel

# from error_handler import retry_with_backoffs
from model_config import log_routing_decision
from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from collections.abc import AsyncIterator

from _init_ import get_ctx, lifespan, AppStateContext
from decision_logic import Decision_logic
# from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
# from logging_handler import setup_logging, get_logger

from dotenv import load_dotenv

load_dotenv(override=True)

# structured query
class Query(BaseModel):
    query: str
    thread_id: str 


app = FastAPI(lifespan=lifespan)

#handler
@app.post("/route")
async def handler(query: Query, 
                  ctx: AppStateContext = Depends(get_ctx),   #telling the router it's dependency
                  ):
    # StreamingResponse for streaming output
    return StreamingResponse(main(query, ctx), 
                            media_type="text/plain", 
                            )

def predict_language(text: str,k: int=1, ctx: AppStateContext = get_ctx):
        label, prob = ctx.lang_model.predict(text, k)
        return list(zip([l.replace("__label__", "") for l in label], prob))


 
async def main(query : Query,  ctx: AppStateContext) -> AsyncIterator[str]:
    decision = await Decision_logic(query, ctx)
    
    tier = log_routing_decision(decision)
    # for tool in tools:
    #     print(f"Tools available: {tool.name}")

    agent_call = ctx.agent_lookup[tier]
    
    async for event in agent_call.astream_events({"messages" : [("human", query.query)]},
                                                    {"configurable": {"thread_id": query.thread_id}}, 
                                                    version="v2",
                                                    ):
            
        if event["event"] == "on_chat_model_stream":
            yield event["data"]["chunk"].text
    
             
if __name__ == "__main__":
    try:
        uvicorn.run("x_v5:app", host = "127.0.0.1", port = 8001, reload= True)
    except Exception as e:
        print(f"an error occured: {e}") 
