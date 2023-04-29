import logging
import os
from typing import Dict, List

import matplotlib.pyplot as plt
import pandas as pd

from tdma_sim_v1.utils.exceptions.sanityCheckError import SanityCheckError


class Comparison:
    FILE_FIGURE = 'comparison_visualization.png'

    logger = logging.getLogger(__name__)

    def __init__(self, config: dict):
        self.experiment_name = config['experiment.name']
        self.experiment_dir = config['experiment.dir']
        self.n_slots = config['experiment.available-slots']
        self.bernoulli_file = config['experiment.data.bernoulli']
        self.selective_file = config['experiment.data.selective']

    def sanity_check(self):
        if self.n_min_transmitters != self.n_max_transmitters:
            raise SanityCheckError('Plot configuration operates exclusively on the starting number of transmitters')

    def compare(self):
        bernoulli = self._get_values(self.bernoulli_file, scaler=self.n_slots)
        selective = self._get_values(self.selective_file)

        fig, ax = plt.subplots()
        ax.plot(bernoulli['index'], bernoulli['value'], '--', label='Bernoulli-Trials Strategy calculation')
        ax.plot(selective['index'], selective['value'], '-', label='t-Slots Strategy calculation')
        ax.set_xlabel('Expected number of transmissions per agent  (BT: p•n, t-Slots: t)')
        ax.set_ylabel('Communication success probability')
        ax.legend(loc='upper right')
        plt.axis([0, self.n_slots, 0, 1])
        plt.title('Models comparison')
        plt.savefig(os.path.join(self.experiment_dir, self.FILE_FIGURE))
        plt.show()

    def _get_values(self, file_name: str, scaler: float = 1.0) -> Dict[str, List[float]]:
        results_file = os.path.join(self.experiment_dir, file_name)
        df = pd.read_csv(results_file, delimiter='\t', header=None, skiprows=1).transpose()
        prob_index = df[0].apply(lambda v: v*scaler).tolist()
        prob_values = df[1].tolist()
        return {"index": prob_index, "value": prob_values}
