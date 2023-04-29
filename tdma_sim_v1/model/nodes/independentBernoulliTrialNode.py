from random import randrange

from tdma_sim_v1.model.messages.vectorMessageBody import VectorMessageBody
from tdma_sim_v1.model.nodes.node import Node
from tdma_sim_v1.model.nodes.tdmaNode import TdmaNode


class IndependentBernoulliTrialNode(TdmaNode):

    def vote(self) -> float:
        pass

    def __init__(self, node_id: int, n_slots: int, n_selects: int):
        super().__init__(node_id, n_slots, n_selects)
        self.occupied_slots = []
        self.available_slots = n_slots
        self.n_selects = n_selects

    def trigger(self) -> int:
        for idx in range(self.available_slots):
            if randrange(0, 1000) < self.n_selects:
                self.occupied_slots += [idx]
        self.announce(VectorMessageBody(self.occupied_slots))
        return len(self.occupied_slots)
