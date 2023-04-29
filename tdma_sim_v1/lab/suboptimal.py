import itertools
import logging
import os
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple

from tdma_calc.api import *

from tdma_sim_v1.utils.buffered_report_writer import BufferedReportWriter


class Suboptimal:
    FILE_FIGURE = 'suboptimal_resiliency.png'
    BT_COLUMNS = (0, 3)
    TSLOTS_COLUMNS = (0, 5)

    logger = logging.getLogger(__name__)
    reporter: BufferedReportWriter

    def __init__(self, config: dict):
        self.experiment_name = config['experiment.name']
        self.experiment_dir = config['experiment.dir']
        self.n_min_transmitters = config['experiment.size.start']
        self.n_max_transmitters = config['experiment.size.stop'] + 1
        self.transmitters_step = config['experiment.size.step']
        self.n_slots = config['experiment.available-slots']
        self.agents_optimal_calc = config['experiment.agents-for-optimal-calc']

    def suboptimal(self):
        self.reporter = BufferedReportWriter(self.experiment_dir, 'report_suboptimal.asv',
                                             ['agents', 'config_bt', 'prob_bt', 'config_tslots', 'prob_tslots'], 1, 'a')
        bt = bernoulli_optimal_probability_choice(self.agents_optimal_calc, self.n_slots)[0]
        tslots = tslots_optimal_selects_choice(self.agents_optimal_calc, self.n_slots)[0]
        for agents in range(self.n_min_transmitters, self.n_max_transmitters, self.transmitters_step):
            self._calculate_suboptimal_results(agents, self.n_slots, bt, tslots)
        self.reporter.close()

    def suboptimal_plot(self):
        bernoulli = self._retrieve_calculated_values(self.BT_COLUMNS)
        selective = self._retrieve_calculated_values(self.TSLOTS_COLUMNS)

        fig, ax = plt.subplots()
        ax.plot(bernoulli['index'], bernoulli['value'], '--', label='Bernoulli-Trials strategy')
        ax.plot(selective['index'], selective['value'], '-', label='t-Slots strategy')
        ax.set_xlabel('Actual number of agents (k)')
        ax.set_xticks(list(range(0, int(bernoulli['index'][-1]+1), 2)))
        ax.set_ylabel('Communication success probability')
        ax.legend(loc='upper right')
        plt.axis([bernoulli['index'][0], bernoulli['index'][-1]//2, 0, 1])
        plt.title(f'Models comparison, the suboptimal configuration')
        plt.savefig(os.path.join(self.experiment_dir, self.FILE_FIGURE))
        plt.show()

    def _calculate_suboptimal_results(self, agents: int, slots: int, bt_config: float, tslots_config: int):
        bt_prob = bernoulli_success_probability(agents, slots, bt_config)
        tslots_prob = tslots_success_probability(agents, slots, tslots_config)
        print(f'Agents: {agents}, Slots: {slots}\nBernoulli({bt_config}): {bt_prob}\nt-Slots({tslots_config}): {tslots_prob}')
        self.reporter.write(f'{agents} & {slots} & {bt_config:.4f} & {bt_prob:.4f} & {tslots_config} & {tslots_prob:.4f}')

    def _retrieve_calculated_values(self, strategy_columns: Tuple[int, int]) -> Dict[str, List[float]]:
        results_file = os.path.join(self.experiment_dir, 'report_suboptimal.asv')
        df = pd.read_csv(results_file, delimiter='&', header=None, skiprows=1)
        agents_index = df[strategy_columns[0]].tolist()
        slots_values = df[strategy_columns[1]].tolist()
        return {"index": agents_index, "value": slots_values}
