1. Tool Caching

    Change: Added cached_tools global with get_tools() wrapper

    Impact: MCP client initializes once per app lifecycle, not per request

    Why: Eliminated redundant overhead on every /route call

2. Embedding Model Split

    Semantic Router: all-MiniLM-L6-v2

    RAG Agent: intfloat/e5-small-v2

    Impact: Intent classification stays fast; RAG retrieval quality improved

    Why: Single-model compromise was hurting both use cases

3. LLM Placement Confirmed

    Decision: ChatOpenAI instances remain inside lifespan

    Impact: Proper async initialization order with checkpointer

    Why: Module-level definitions would break async resource readiness

Want it as a git commit -m one-liner or keep the bullet format?
