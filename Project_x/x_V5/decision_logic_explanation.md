```
class QueryLength(Enum):
    SHORT = "short"
    
```

Using an `Enum` inside a class crate a localizer, restricted data type that limits property's values to strictly predefined set


When you declare an Enum within a class, the compiler stops treating that data as a generic, loosely validated primitive (like an integer or a string). Instead, it wraps the data in a dedicated type sandbox.

```
@dataclass
class IntentResult(frozen=True):
    category: str
    confidence : float
    model : str
    tool : str
    source : str   

```
using @dataclass which automatically generates sepcial utility methods such as `__init__`, `__repr__`,`__eq__`

__init__: Automatically creates the setup function to accept and assign your variables.
__repr__: Provides a clean, readable text printout of the object and its values
__eq__: Allows you to directly compare two object instances to see if their values match


The purpose of this class is simple store the final intent result.


```
def classify_query_length(query : str) -> QueryLength:
    words = len(query.split())
    if words <= 10:
        return QueryLength.SHORT
    elif words <=50:
        return QueryLength.MEDIUM
    return QueryLength.LONG
```

takes query as str, return QueryLength

breakdown:
1. takes query, use `.split` to str break it down, use `len` on top of it count the string length.
2. if len <= 10: return QueryLength.SHORT basically "short" vice versa for each length


```
async def safe_llm_classifier(query : str, ctx: Any, timeout : float = 2.0) -> Optional[Dict[str, Any]]:
    try:
        return await  asyncio.wait_for(llm_classifier(query, ctx) ,timeout = timeout)
    except asyncio.TimeoutError:
        print(f"LLM classification timed out after {timeout}s for query: '{query}'")
    return None
```

this is creating async function as usual.
takes query, ctx, timeout, return `Dict` which is `Optional`
putting it in a try block (because well its sensitive and we need to safeguard it)
`return await` then using `asyncio.wait_for(aw, timeout)` this is basically use to execute task with strict maximum time limit.

If the task is done in timee, its result is returned. If the time limit expires, the task is automatically cancelles and
an `asyncio.TimeoutError` is raised.

Note : wait_for handles the execution, you don't need a .invoke() method here.

```
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
        
        if semantic_results and semantic_results[0].get("confidence", 0.0) >= 0.0:
            return _pack(semantic_results[0], "semantic")
        
        return _fallback(ctx)
    
    if length_tier == QueryLength.MEDIUM:
        if semantic_results and semantic_results[0].get("confidence" , 0.0) >= 0.34:
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
    
```

this is the async function define again
takes query, keyword_results, semantic_results, lenght_tier, ctx, return `Intentresult`

simple waterfall method if query is short check with `==`.

```
if keyword_results and keyword_results[0].get("confidence") >= 0.9:
            return _pack(keyword_results[0], "keyword")
```

here u must be thinking Why check `keyword_results` before `keyword_results[0]`?

This is about preventing fatal crashes through a Python feature called short-circuiting.

Because `keyword_results` is allowed to be None (if the search failed) or an empty list [] (if no matches were found), trying to check [0] immediately is dangerous.

    If it is None, asking for [0] throws a TypeError.

    If it is [], asking for [0] throws an IndexError.

In Python, when you use the and operator, it reads left to right. If the first part (keyword_results) is empty or None, Python says, "This is already false, I don't even need to look at the second part," and it skips it entirely. Putting keyword_results first acts as a shield to guarantee that [0] actually exists before the code tries to touch it.

if this fails it fallsback to semantic 
If the code reaches this line, it inherently means the keyword check failed (either the score was < 0.9 or there were no keyword results). It then asks, "Is the semantic confidence > 0.0?" If yes, it exits the function.

similarly, for `semantic_results`


```
def _pack(raw: Dict[str, Any], source: str) -> IntentResult:
    return IntentResult(
        category= raw.get("category", "uncategorized"),
        confidence=float(raw.get("confidence", 0.0)),
        model=raw.get("model", "unknown"),
        tool=raw.get("tool", "none"),
        source=source
    )
```

this takes in raw Dict[str, Any] basically what i get from `intent_routing` and again return `intentresult`.

where one extra attr is added is `source` which u get from the above async function return value.
 return _pack(semantic_results[0], "semantic"),
 return _pack(keyword_results[0], "keyword"),
 return _pack(llm_result, "llm")  -> here "llm" fill the `source` gap.


```
def _fallback(ctx: Any) -> IntentResult:
    """Guaranteed safe fallback state"""
    return IntentResult(
        category="uncategorized",
        confidence=0.0,
        model="fast",
        tool=getattr(ctx, "tools", "none"),
        source="fallback"
    )
```

This is a guranteed fallback state

if everything fails this will make sure it doesn't break down in the middle but routes safely.



26/7

Updated `safe_llm_cassifier`:

1. Using strucutred output with `.with_structured_output`
2. it protects SLA (service level agreement) by inforcing hard latency celing `.wait_for` with timeout out 2 seconds
3. graceful error and fallback boundaries *with `try/except` block*

```
except asyncio.TimeoutError:
        logger.warning(f"Classifier timed out (> {timeout}s). Falling back to default.")
        return StrictOutput(model_type="Fast", tool="None") # Safe default fallback
        
    except (ValidationError, Exception) as e:
        logger.error(f"Classifier output parsing error: {e}")
        return StrictOutput(model_type="Fast", tool="None")  # Safe error fallback
```
Using `ValidationERror` from `Pydantic` which validates if the output is strictly validated provide fail safe and fast mechanism 
and returning `return StrictOutput(model_type="Fast", tool="None")` to fallback.



## Final Decision logic

it's almost same with few tweaks:

```
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
```
Simple explanation:

creating a `task` and simply using `.gather()` to invoke those task
why?
it execute fast signals concurrently if needed
inside `gather()` return_exceptions=True 
because return_exceptions=True prevents one failed service from crashing the other

storing the result[0] and results [1] at respective keyword_results and semantic_results variable.

where
```
if isinstance(results[0], Exception):
    print(f"keyword intent service failed: {results[0]}")
if isinstance(results[1], Exception):
    print(f"semantic intent service failed: {results[1]}")
```

basically if there is exception print that message since we are using return_exeception=True it will return Exception
so if there is any print the message and return asdict(result)

btw By using asdict(result), you convert that dataclass into a clean dict:

common for reuturning api reonse in fastapi/flask etc, db insertion, logging etc.



