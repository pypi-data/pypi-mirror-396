"""
Agentic Reliability Framework (ARF)
Production-grade multi-agent AI for reliability monitoring
"""

from .__version__ import __version__

__all__ = [
    "__version__",
    "EnhancedReliabilityEngine",
    "SimplePredictiveEngine",
    "BusinessImpactCalculator",
    "AdvancedAnomalyDetector",
    "create_enhanced_ui",
    "get_engine",
    "get_agents",
    "get_faiss_index",
    "get_business_metrics",
    "enhanced_engine",
]

# Lazy imports via __getattr__
def __getattr__(name: str):
    if name == "EnhancedReliabilityEngine":
        from .app import EnhancedReliabilityEngine
        return EnhancedReliabilityEngine
    elif name == "SimplePredictiveEngine":
        from .app import SimplePredictiveEngine
        return SimplePredictiveEngine
    elif name == "BusinessImpactCalculator":
        from .app import BusinessImpactCalculator
        return BusinessImpactCalculator
    elif name == "AdvancedAnomalyDetector":
        from .app import AdvancedAnomalyDetector
        return AdvancedAnomalyDetector
    elif name == "create_enhanced_ui":
        from .app import create_enhanced_ui
        return create_enhanced_ui
    elif name in {"get_engine", "get_agents", "get_faiss_index", "get_business_metrics", "enhanced_engine"}:
        from .lazy import get_engine, get_agents, get_faiss_index, get_business_metrics, enhanced_engine
        
        # Return the specific function based on the name
        if name == "get_engine":
            return get_engine
        elif name == "get_agents":
            return get_agents
        elif name == "get_faiss_index":
            return get_faiss_index
        elif name == "get_business_metrics":
            return get_business_metrics
        elif name == "enhanced_engine":
            return enhanced_engine
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
