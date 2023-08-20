import os
import re
from typing import List, Pattern, Dict

from matplotlib import pyplot as plt
from numpy import arange

from tdma_sim_v2.lab.execution import Execution


class Comparison:
    FILE_FIGURE = 'comparison_visualization.png'
    EXPERIMENT_FILE_REGEX = re.compile(r'result_per_topology_evolution_.*.tsv')
    CALCULATION_FILE_REGEX = re.compile(r'result_calculation_data_.*.tsv')

    def __init__(self, execution: Execution, config: dict):
        self.execution = execution
        self.config = config
        self.experiment_dir = config['experiment.dir']
        self.experiment_model = self.config['experiment.model.node']
        self.strategy_evolution_rng: range = range(config['experiment.strategy.evolution.start'],
                                                   config['experiment.strategy.evolution.stop'] + 1,
                                                   max(1, config['experiment.strategy.evolution.step']))
    def plot(self):
        self._plot_experiments(self._determine_files(self.EXPERIMENT_FILE_REGEX),
                               self._determine_files(self.CALCULATION_FILE_REGEX))


    def _determine_files(self, regex: Pattern) -> List[str]:
        selected_files = []
        for root, dirs, files in os.walk(self.experiment_dir):
            for file in files:
                if regex.match(file):
                    selected_files.append(file)
        return selected_files

    def _plot_experiments(self, experiments: List[str], calculations: List[str]) -> None:
        """Any model derivations in plot mechanism comes from the file naming, so the comparisons may be easily made."""
        print(f'Summarizing results in the plot...')
        ax = self._prepare_plot()
        lines = []
        if self.experiment_model == 'BtNode':
            calculations.reverse()  # reverse, as BT for some reson mixes the order
        for file in calculations:
            # tolerance = int(self.calculation_file_regex.match(file).group(2))
            data = self.execution.get_calculation_results(file)
            lines.append(self._add_calculation_data_to_plot(ax, data))
        for file in experiments:
            model = self.experiment_model
            # tolerance = int(self.experiment_file_regex.match(file).group(2))
            complete_file = file.replace('per_topology_evolution', 'full')
            print(complete_file)
            data = self.execution.get_experiment_results(file, model, complete_file)
            lines.append(self._add_experiment_data_to_plot(ax, data))
        self._finalize_plot(ax, lines)

    def _prepare_plot(self):
        fig, ax = plt.subplots()
        ax.set_ylabel('Communication success probability')
        return ax

    def _add_experiment_data_to_plot(self, ax, experiment: Dict[str, List[float]]):
        print(f'Plotting experiment for comparison...')

        print(experiment['index'])
        print(experiment['stderr'])
        return ax.errorbar(experiment['index'], experiment['value'], experiment['stderr'], fmt='o', markersize=1.0,
                           color='black', label=None)

    def _add_calculation_data_to_plot(self, ax, calculation: Dict[str, List[float]]):
        print(f'Plotting calculation for comparison...')
        return ax.plot(calculation['index'], calculation['value'], label=None)

    def _finalize_plot(self, ax, lines: List):
        if self.experiment_model == 'BtNode':
            # plt.axis([0, 1, 0, 1])
            plt.axis([0, 0.4, 0, 1]) # extra
            plt.xticks([r for r in arange(0.0, 0.41, 0.05)],
                       ["0.00"] + [f'{r:0.2f}' for r in arange(0.05, 0.41, 0.05)])  # extra
            plt.title('Bernoulli-Trials Strategy')
            ax.set_xlabel('Agent\'s transmission probability in the single slot (p)')
        elif self.experiment_model == 'tSlotsNode':
            plt.axis([0, self.strategy_evolution_rng.stop, 0, 1])
            plt.xticks([r for r in range(0, 41, 5)], [r for r in range(0, 41, 5)])  # extra
            plt.title('t-Slots Strategy')
            ax.set_xlabel('Cardinality of agent\'s transmission set (t)')
        else:
            print('Error: Plotting issue, unrecognized agents'' strategy')
        lines[0][0].set_label("Calculation data (k=10)")
        lines[1][0].set_label("Calculation data (k=20)")
        lines[3][0].set_label("Simulation data")
        ax.legend(loc='upper right')
        plt.savefig(os.path.join(self.experiment_dir, self.FILE_FIGURE))
        plt.show()
