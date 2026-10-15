from contextlib import asynccontextmanager
from typing import Any
from fastapi import FastAPI, Request
from fasttext import load_model
from pydantic import BaseModel, ConfigDict
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from model_config import endpoint,  MODEL_MAP
from langchain.agents import create_agent
from system_prompt import ReadOnly
from tools_handling import tool_call
from pathlib import Path
from dotenv import load_dotenv
import os

#override=True gives the os set variable absolute priority
load_dotenv(override=True)

# .../parent_folder/project_folder)
CURRENT_DIR = Path(__file__).resolve().parent

#Go up one more level to the parent folder (.../parent_folder)
MODEL_PATH = CURRENT_DIR.parent

#Navigate into the models folder
MODEL_PATH = MODEL_PATH / "models" / "lid.176.ftz"


class AppStateContext(BaseModel):
    #takes all sorts of datatypes eg. connection pool etc..
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    agent_lookup: Any = None
    tools: Any = None
    pool: Any = None #AsyncConnectionPool
    checkpointer: Any = None #AsyncPostgresSaver
    lang_model: Any = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    # db setup for short term memory
    # Create pool once at startup
    print("checkpointer connection pool starting up..")
    pool = AsyncConnectionPool(
        os.getenv("DB_URL"),
        min_size= 1,    #always keep 1 connection warm
        max_size= 10,   #never more than 10
        open= True      #open immediately
    )
    
    # Create checkpointer with pool (connection stays alive via pool)
    checkpointer = AsyncPostgresSaver(pool)
    # Setup once   - pool handles reconnections
    await checkpointer.setup()
    # async with AsyncPostgresSaver.from_conn_string(DB_URL) as checkpointer:
    #await checkpointer.setup()

    #tool call 
    async def get_tools():
        cached_tools = await tool_call()
        return cached_tools
        
    tools= await get_tools()
    
    sys_prompt = ReadOnly()
    
    agent_lookup = {}
    for tier, config in MODEL_MAP.items():
        model_endpoint = endpoint(config)
        
        raw_prompt_string = sys_prompt.prompt
        
        agent = create_agent(
            model_endpoint,
            tools,
            checkpointer = checkpointer,
            system_prompt= raw_prompt_string,
            )
        agent_lookup[tier] = agent
        
    
        
        
    #loading fasttext langdetect model (requires to load only once)
    lang_model= load_model(str(MODEL_PATH))
    
    # Instantiate the container
    state_container = AppStateContext(
        lang_model=lang_model,
        tools=tools,
        agent_lookup=agent_lookup,
        pool=pool,
        checkpointer=checkpointer,
    )
    
    # this Yield the context container directly to FastAPI
    yield {"context": state_container}
    
    print("checkpointer connection shutting down..")
    # lastly safe application shutdown cleanup
    await pool.close()   

def get_ctx(request: Request) -> AppStateContext:
    """Dependency provider to safely access app state."""
    return request.state.context


    
   
    
    
    