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
        self.plot1_datafile = config['experiment.data.plot1']
        self.plot1_scaler = config['experiment.data.scaler1']
        self.plot1_label = config['experiment.data.label1']
        self.plot2_datafile = config['experiment.data.plot2']
        self.plot2_scaler = config['experiment.data.scaler2']
        self.plot2_label = config['experiment.data.label2']
        self.title = config['experiment.data.title']
        self.xaxis = config['experiment.data.xaxis']

    def sanity_check(self):
        if self.n_min_transmitters != self.n_max_transmitters:
            raise SanityCheckError('Plot configuration operates exclusively on the starting number of transmitters')

    def compare(self):
        dataset1 = self._get_values(self.plot1_datafile, scaler=self.plot1_scaler)
        dataset2 = self._get_values(self.plot2_datafile, scaler=self.plot2_scaler)

        fig, ax = plt.subplots()
        ax.plot(dataset1['index'], dataset1['value'], '--', label=self.plot1_label)
        ax.plot(dataset2['index'], dataset2['value'], '-', label=self.plot2_label)
        ax.set_xlabel(self.xaxis)
        ax.set_ylabel('Communication success probability')
        ax.legend(loc='upper right')
        plt.axis([0, self._max_argument(dataset1, dataset2), 0, 1])
        plt.title(self.title)
        plt.savefig(os.path.join(self.experiment_dir, self.FILE_FIGURE))
        plt.show()

    def _get_values(self, file_name: str, scaler: float = 1.0) -> Dict[str, List[float]]:
        results_file = os.path.join(self.experiment_dir, file_name)
        df = pd.read_csv(results_file, delimiter='\t', header=None, skiprows=1).transpose()
        prob_index = df[0].astype(float).apply(lambda v: v*scaler).tolist()
        prob_values = df[1].tolist()
        return {"index": prob_index, "value": prob_values}

    def _max_argument(self, *args):
        max_val = 0.0
        for data in args:
            for val in data['index']:
                max_val = max(max_val, val)
        return max(1, max_val)
