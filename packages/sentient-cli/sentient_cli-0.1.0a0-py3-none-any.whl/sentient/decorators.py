"""Sentient SDK decorators for marking agent entry points."""


def sentient(func):
    """
    Decorator to mark the Sentient agent entry function.
    
    The platform discovers this function at runtime when deploying to Lambda.
    Only one function per module should be decorated with @sentient.
    
    Example:
        ```python
        from sentient import sentient
        
        @sentient
        def my_agent(input: str):
            return {"output": "Hello!"}
        ```
        
        Or with streaming:
        ```python
        @sentient
        async def my_agent(input: str):
            async for chunk in some_streaming_logic():
                yield chunk
        ```
    """
    setattr(func, "_sentient_entry_point", True)
    return func

