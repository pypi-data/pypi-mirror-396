"""
Volcengine Provider
"""

# 延迟导入以支持可选依赖
__all__ = ["VolcengineChat", "VolcenginePodcast"]

def __getattr__(name: str):
    if name == "VolcengineChat":
        try:
            from .chat import VolcengineChat
            return VolcengineChat
        except ImportError as e:
            raise ImportError(
                f"VolcengineChat requires 'volcenginesdkarkruntime' package. "
                f"Install it with: pip install volcengine-python-sdk[ark]"
            ) from e
    elif name == "VolcenginePodcast":
        from .podcast import VolcenginePodcast
        return VolcenginePodcast
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
