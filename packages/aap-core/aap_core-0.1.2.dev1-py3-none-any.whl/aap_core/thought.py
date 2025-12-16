from aap_core.types import BaseChain


class ChainOfThought(BaseChain):
    def with_self_consistency(self, max_branches: int = 1):
        pass


class TreeOfThought(BaseChain):
    pass


class GraphOfThought(BaseChain):
    pass
