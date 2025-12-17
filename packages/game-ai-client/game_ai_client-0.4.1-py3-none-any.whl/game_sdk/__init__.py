from .client import GameClient
from .ai_client import AIGameClient
from .integration import GameIntegrationSpec, GenericGameAdapter, load_integration
from .mcts import (
    MCTS,
    GameEnv,
    # Strategy interfaces
    SearchAlgorithmStrategy,
    SelectionStrategy,
    ExpansionStrategy,
    SimulationStrategy,
    BackpropagationStrategy,
    # Strategy implementations
    MCTSStrategy,
    UCBSelectionStrategy,
    DefaultExpansionStrategy,
    RandomSimulationStrategy,
    DefaultBackpropagationStrategy,
)
from .utils import (
    symbol_to_int,
    build_generic_state,
    detect_move,
    simple_heuristic,
)
from .registration import (
    register_game,
    validate_integration,
    create_ai_integration_template,
)

__all__ = [
    # Clients
    "GameClient",
    "AIGameClient",
    "GameIntegrationSpec",
    "GenericGameAdapter",
    "load_integration",
    # Registration helpers
    "register_game",
    "validate_integration",
    "create_ai_integration_template",
    # Main MCTS (backward compatible)
    "MCTS",
    "GameEnv",
    # Strategy interfaces
    "SearchAlgorithmStrategy",
    "SelectionStrategy",
    "ExpansionStrategy",
    "SimulationStrategy",
    "BackpropagationStrategy",
    # Strategy implementations
    "MCTSStrategy",
    "UCBSelectionStrategy",
    "DefaultExpansionStrategy",
    "RandomSimulationStrategy",
    "DefaultBackpropagationStrategy",
    # Utilities
    "symbol_to_int",
    "build_generic_state",
    "detect_move",
    "simple_heuristic",
]
