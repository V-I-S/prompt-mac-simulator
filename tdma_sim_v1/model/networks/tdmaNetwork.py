from typing import List, Tuple, Optional

from tdma_sim_v1.model.messages.message import Message
from tdma_sim_v1.model.messages.vectorMessageBody import VectorMessageBody
from tdma_sim_v1.model.networks.network import Network
from tdma_sim_v1.model.nodes.node import Node
from tdma_sim_v1.model.nodes.tdmaNode import TdmaNode


class TdmaNetwork(Network):

    def __init__(self, nodes: List['Node'], n_slots: int):
        super().__init__(nodes)
        self.slots = [0 for _ in range(n_slots)]

    def reset(self, valuation: List[float]) -> None:
        super().reset(valuation)
        self.slots = [0 for _ in range(len(self.slots))]

    def is_communication_success(self) -> bool:
        for n in self.nodes:
            if not self.__has_dedicated_channel(n):
                return False
        return True

    def is_communication_success_percentile(self, percentile: float) -> bool:
        jammed_nodes = 0
        for n in self.nodes:
            if not self.__has_dedicated_channel(n):
                jammed_nodes += 1
        return jammed_nodes/len(self.nodes) < (100 - percentile) / 100

    def deliver(self) -> Tuple[Optional['Message'], bool]:
        if not self.relay:
            self.logger.debug('Network relay is empty, sentiment: %.3f', self._count_votes())
            return None, None
        msg = self.relay.pop(0)
        if not isinstance(msg.body, VectorMessageBody):
            self.logger.error('TDMA Network expects slots allocation message from its nodes')
            raise AssertionError('Bad MessageBody Type, expected \'VectorMessageBody\'')

        for s in msg.body.vector:
            self.slots[s] += 1
        return msg, False

    def __has_dedicated_channel(self, node: Node) -> bool:
        assert isinstance(node, TdmaNode)
        if not node.occupied_slots:
            self.logger.error('Node %s did not occupy any slot!', node)
        for s in node.occupied_slots:
            if self.slots[s] == 1:
                return True
        return False
