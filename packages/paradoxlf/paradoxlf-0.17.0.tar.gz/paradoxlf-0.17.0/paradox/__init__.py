from .engine import LatentMemoryEngine
from . import encoder, decoder, visualization
from .evolution import GeneticOptimizer
from .autonomous import AutoAgent
from .safety import GuardRail

__version__ = "0.17.0"
__all__ = ["LatentMemoryEngine", "encoder", "decoder", "visualization", "GeneticOptimizer", "AutoAgent", "GuardRail", "__version__"]
