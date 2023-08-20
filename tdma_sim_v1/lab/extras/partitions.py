import os
from typing import Dict

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class Partitions:
    FILE_FIGURE = 'partition_visualization.png'
    ANOMALIES_FILE_FORMAT = 'result_anomalies_{}_tolerance-0.tsv'
    UNU = "unused"
    SUC = "success"
    COL = "collision"

    def __init__(self, config: dict):
        self.config = config
        self.experiment_dir = config['experiment.dir']
        self.experiment_model = self.config['experiment.model.node']

    def plot(self):
        data_frame = self._ensure_experiments_exact_data_file_present()
        results = self._average_collected_partitions(data_frame)
        for r in results:
            print(f'{r}: {results[r]}')
        self._plot_collected_partitions(results)

    def _ensure_experiments_exact_data_file_present(self) -> pd.DataFrame:
        print(f'Reading exact data file...')
        file = self.ANOMALIES_FILE_FORMAT.format(self.experiment_model)  # impl. only for tolerance = 0
        path = os.path.join(self.experiment_dir, file)
        if not os.path.isfile(path):
            raise IOError(f'Experiment results not recorded: {file}')
        return pd.read_csv(path, delimiter='\t')

    def _average_collected_partitions(self, df: pd.DataFrame) -> Dict[float, Dict[str, float]]:
        steps = df['step'].unique()
        return {s: self._extract_means(s, df) for s in steps}

    def _extract_means(self, step: float, df: pd.DataFrame) -> Dict[str, float]:
        partition = df[df['step'] == step]['end-picture'].apply(lambda t: eval(t))
        mean_unused = partition.apply(lambda t: t[0]).mean()
        mean_success = partition.apply(lambda t: t[1]).mean()
        mean_collision = partition.apply(lambda t: t[2]).mean()
        return {self.UNU: mean_unused, self.SUC: mean_success, self.COL: mean_collision}

    def _plot_collected_partitions(self, data: Dict[float, Dict[str, float]]) -> None:
        bar_width = 0.27

        mean_unused = [data[i][self.UNU] for i in data]
        mean_success = [data[i][self.SUC] for i in data]
        mean_collision = [data[i][self.COL] for i in data]

        if self.experiment_model == 'BtNode':
            br1 = np.arange(1, max(data)/10 + 1)
        else:
            br1 = np.arange(1, max(data) + 1)
        br2 = [x + bar_width for x in br1]
        br3 = [x + bar_width for x in br2]

        fig, ax = plt.subplots(figsize=(12, 5))

        print(f'{br1} - {mean_unused}')
        plt.bar(br1, mean_unused, color='lightgrey', width=bar_width, label='Unused slots')
        plt.bar(br2, mean_success, width=bar_width, label='Collision-free slots')
        plt.bar(br3, mean_collision, color='orange', width=bar_width, label='Collisions')

        if self.experiment_model == 'BtNode':
            plt.xticks([r + bar_width for r in range(0, 101, 10)], [r/100 for r in range(0, 101, 10)])
            plt.axis([0, max(data)/10 + 1.5, 0, 100])
        else:
            plt.xticks([r + bar_width for r in data], [r for r in data])
            plt.axis([0, max(data) + 1.5, 0, 100])
        plt.title('Unused slots vs. collision-free transmissions vs. collisions')
        ax.set_xlabel('Cardinality of agent\'s transmission set (t)')
        ax.set_ylabel('Number of slots')
        plt.legend()

        plt.savefig(os.path.join(self.experiment_dir, self.FILE_FIGURE))
        plt.show()
