import asyncio
from dataclasses import dataclass, asdict
from intent_router import normalization, keyword_intent, semantic_intent
from _init_ import get_ctx, AppStateContext
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, ValidationError
from model_config import classifier_endpoint
from typing import NewType

class QueryLength(Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"

class StrictOutput(BaseModel):
    model_type : str = Field(description="type of model"),
    tool : List = Field(description="tools being used")
    
    
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


async def safe_llm_classifier(query : str, ctx: Any, timeout : float = 2.0) -> StrictOutput:
    try:
        llm_classifier = classifier_endpoint.with_structured_output(StrictOutput)
        
        return await  asyncio.wait_for(
            llm_classifier.ainvoke(query, ctx) ,
            timeout = timeout)
        
    except asyncio.TimeoutError:
        print(f"LLM classification timed out after {timeout}s for query: '{query}'")
        return StrictOutput(model_type="Fast", tool="None")
    
    except (ValidationError, Exception) as e:
        print(f"Classifier error: {e}")
        return StrictOutput(model_type="Fast", tool="None")
        

async def resolve_intent(
    query : str,
    keyword_results : Optional[List[Dict[str, Any]]],
    semantic_results : Optional[List[Dict[str, Any]]],
    length_tier : QueryLength,
    ctx : Any
) -> IntentResult:
    
    if length_tier == QueryLength.SHORT:
        if keyword_results and keyword_results[0].get("confidence") >= 0.9:
            return _pack(keyword_results[0], "keyword")
        
        if semantic_results and semantic_results[0].get("confidence", 0.0) >= 0.35:
            return _pack(semantic_results[0], "semantic")
        
        return _fallback(ctx)
    
    if length_tier == QueryLength.MEDIUM:
        if semantic_results and semantic_results[0].get("confidence" , 0.0) >= 0.35:
            return _pack(semantic_results[0], "semantic")
        
        llm_result = await safe_llm_classifier(query, ctx)
        if llm_result:
            return _pack(llm_result, "llm")
        
        return _fallback(ctx)
    
    if length_tier == QueryLength.LONG:
        llm_result = await safe_llm_classifier(query, ctx, timeout=4.0)
        if llm_result:
            return _pack(llm_result, "llm")
        
        return _fallback(ctx)
    
    
def _pack(raw: Dict[str, Any], source: str) -> IntentResult:
    return IntentResult(
        category= raw.get("category", "uncategorized"),
        confidence=float(raw.get("confidence", 0.0)),
        model=raw.get("model", "unknown"),
        tool=raw.get("tool", "none"),
        source=source
    )


def _fallback(ctx: Any) -> IntentResult:
    """Guaranteed safe fallback state"""
    return IntentResult(
        category="uncategorized",
        confidence=0.0,
        model="fast",
        tool=getattr(ctx, "tools", "none"),
        source="fallback"
    )

def predict_language(text: str,k: int=1, ctx: AppStateContext = get_ctx):
        label, prob = ctx.lang_model.predict(text, k)
        return list(zip([l.replace("__label__", "") for l in label], prob))


async def Decision_logic(query: Any, ctx: Any) -> Dict[str, Any]:
    try:
        raw_query = query.query
        
        normalized = normalization(raw_query)
        
        input_lang = NewType("en", str)
        
        try:
            lang_results = await predict_language(normalized, ctx)
            lang, confidence = lang_results[0]
            if lang != input_lang and confidence > 0.8:
                return asdict(_fallback(ctx))
            
        except Exception as e:
            print(f"Language detection failed, proceeeding as English. Error")
            
        length_tier = classify_query_length(normalized)
        
        keyword_results = None
        semantic_results = None
        
        if length_tier != QueryLength.LONG:
            
            tasks = [
                keyword_intent(normalized),
                semantic_intent(normalized)
            ]
            # return_exceptions=True prevents one failed service from crashing the other
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            keyword_results = results[0] if not isinstance(results[0], Exception) else None
            semantic_results = results[1] if not isinstance(results[1], Exception) else None
            
            if isinstance(results[0], Exception):
                print(f"keyword intent service failed: {results[0]}")
            if isinstance(results[1], Exception):
                print(f"semantic intent service failed: {results[1]}")
                
            result = await resolve_intent(
                query=normalized,
                keyword_results=keyword_results,
                semantic_results=semantic_results,
                length_tier=length_tier,
                ctx=ctx,
            )
            
            return asdict(result)
        
    except Exception as e:
        print(f"catastrophic failure in decision logic: {e}")
        return asdict(_fallback(ctx))
        
