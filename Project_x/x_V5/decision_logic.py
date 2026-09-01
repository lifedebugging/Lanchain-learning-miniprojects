import asyncio
from dataclasses import dataclass, asdict
from intent_router import normalization, keyword_intent, semantic_intent
from _init_ import get_ctx, AppStateContext
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
from pydantic import BaseModel, Field, ValidationError
from model_config import classifier_endpoint
from logging_handler import get_logger

log = get_logger("decision_logic")

class QueryLength(Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"

# class StrictOutput(BaseModel):
#     model_type : str = Field(description="Always return 'Fast' or 'Smart' depending on how complex user query is for example simple generic, facts, casual chat always use 'Fast' and for deep reasoning, complex use 'Smart'"),
#     tool : List = Field(description="tools being used, suggest tool")

class StrictOutput(BaseModel):
    category: str = Field(default="classifier", description="Intent category like GREETINGS, CODING, etc.")
    confidence: float = Field(default=0.0, description="Confidence score between 0 and 1")
    model: Literal["Fast", "Smart"] = Field(default="Fast", description="Model tier: Fast for simple queries, Smart for complex")
    tool: str = Field(default="none", description="Invoke 'get_time' for time queries, 'rag_subagent' for external documents related to 'How Organizations Use AI: Evidence from ChatGPT', or return 'none' if no tool is needed.")
    
@dataclass
class IntentResult:
    category: str
    confidence : float
    model : str
    tool : str
    source : str    
    
    
def classify_query_length(query : str) -> QueryLength:
    words = len(query.split())
    if words <= 10:
        return QueryLength.SHORT
    elif words <=50:
        return QueryLength.MEDIUM
    return QueryLength.LONG


async def safe_llm_classifier(query : str, timeout : float = 3.0) -> StrictOutput:
    try:
        llm_classifier = classifier_endpoint().with_structured_output(StrictOutput)
        
        print("classifier triggered")
        return await asyncio.wait_for(
            llm_classifier.ainvoke(query),
            timeout = timeout)
        
    except asyncio.TimeoutError:
        log.info(f"LLM classification timed out after {timeout}s for query: '{query}'")
        return StrictOutput(model="Fast", tool="None")
    
    except (ValidationError, Exception) as e:
        log.error(f"Classifier error: {e}")
        return StrictOutput(model="Fast", tool="None")
        
        
async def resolve_intent(
    query : str,
    keyword_results : Optional[List[Dict[str, Any]]],
    semantic_results : Optional[List[Dict[str, Any]]],
    length_tier : QueryLength,
    ctx : Any
) -> IntentResult:
    
    if length_tier == QueryLength.SHORT:
        if keyword_results:
            print("keyword triggered")
            return _pack(keyword_results[0], "keyword")
        # future change : add the timeout for both the keyword and semantic if taking too long to answer less than 3.0 sec
        # elif semantic_results and semantic_results[0].get("confidence", 0.0) >= 0.34: 
        #     return _pack(semantic_results[0], "semantic")
        else:
            return _fallback(ctx)
    
    if length_tier == QueryLength.MEDIUM:
        if semantic_results and semantic_results[0].get("confidence" , 0.0) >= 0.34:
            print("semantic triggered")
            return _pack(semantic_results[0], "semantic")
        
        else:
            llm_result = await safe_llm_classifier(query)
            if llm_result:
                return _pack(llm_result.model_dump(), "llm")
            
            return _fallback(ctx)
    
    # dead code because LONG is handled before resolve_intent. it never gets called
    # if length_tier == QueryLength.LONG:
    #     llm_result = await safe_llm_classifier(query)
    #     print(llm_result)
    #     if llm_result:
    #         try:
    #             return asdict(_pack(llm_result.model_dump(), "llm"))
    #         except Exception as e:
    #             return f"error: {e}"
        
    #     return _fallback(ctx)
    
    
def _pack(raw: Dict[str, Any], source: str) -> IntentResult:
    return IntentResult(
        category= raw.get("category", "uncategorized"),
        confidence=float(raw.get("confidence", 0.0)),
        model=raw.get("model", "Fast"),
        tool=raw.get("tool", "none"),
        source=source
    )


def _fallback(ctx: Any) -> IntentResult:
    """Guaranteed safe fallback state"""
    return IntentResult(
        category="uncategorized",
        confidence=0.0,
        model="Fast",
        tool=getattr(ctx, "tools", "none"),
        source="fallback"
    )


def predict_language(text: str, ctx: AppStateContext, k: int = 1):
    model = ctx.lang_model
    label, prob = model.predict(text, k)
    return [l.replace("__label__", "") for l in label]


async def Decision_logic(query: str, ctx: Any) -> Dict[str, Any]:
    
    try:
        raw_query = query
        normalized = normalization(raw_query)

        try:
            lang_results = predict_language(normalized, ctx)
            lang = lang_results[0]
            
            if lang != "en":
                return asdict(_fallback(ctx))
            
        except Exception as e:
            log.error(f"Language detection failed, proceeding as English. Error : {e}")
            
        length_tier = classify_query_length(normalized)
        
        keyword_results = None
        semantic_results = None
        
        if length_tier != QueryLength.LONG:
            
            # tasks = [
            #     keyword_intent(normalized),
            #     semantic_intent(normalized)
            # ]
            # # return_exceptions=True prevents one failed service from crashing the other
            # results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # keyword_results = results[0] if not isinstance(results[0], Exception) else None
            # semantic_results = results[1] if not isinstance(results[1], Exception) else None
            try:
                keyword_results = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, keyword_intent, normalized),
                    timeout=2.0
                    )
            except asyncio.TimeoutError:
                log.error("keyword intent timed out")
                return _fallback(ctx)
            
            except Exception as e:
                log.error("keyword intent failed", error=str(e))
                return _fallback(ctx)
                            
        
            # if keyword_results:
            #     semantic_results=None
                
            # else:
            #     return asdict(_fallback(ctx))
                
                # try:
                #     semantic_results = await asyncio.wait_for(
                #         asyncio.get_event_loop().run_in_executor(None, semantic_intent, normalized),
                #         timeout=15.0
                #         )
                # except asyncio.TimeoutError:
                #     log.error("semantic intent timed out")
                #     return asdict(_fallback(ctx))
                # except Exception as e:
                #     log.error("semantic intent failed", error=str(e))
                #     return asdict(_fallback(ctx))
                                
    
            result = await resolve_intent(
                query=normalized,
                keyword_results=keyword_results,
                semantic_results=semantic_results,
                length_tier=length_tier,
                ctx=ctx,
            )
            return asdict(result)
        
        else:
            llm_result = await safe_llm_classifier(query)
            if llm_result:
                return asdict(_pack(llm_result.model_dump(), "llm"))
            return asdict(_fallback(ctx))
            
            
    except Exception as e:
        log.fatal(f"catastrophic failure in decision logic: {e}")
        return asdict(_fallback(ctx))
        
