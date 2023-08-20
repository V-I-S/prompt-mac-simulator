from tdma_sim_v1.utils.yamlUtils import read_yaml, flatten_yaml


class ExecutionConfig:
    """
    Main execution configuration. Expected unique yaml's content is:
        experiment:
            name:
            dir:
            header:
            description:
            model:
                network:
                node:
                executor:
            size:
                start:
                stop:
                step:
            topology:
                generator:
                evolution:
                    start:
                    stop:
                    step:
                instances-per-evolution:
            valuation:
                strategy:
                generator:
                max-instances-per-topology:
                max-steps-per-instance:
            sampling-frequency:
            execution-cores:
            target-percent:
            agents-for-optimal-calc:
              available-slots: 40
            data:
              title:
              xaxis:
              plot1:
              scaler1:
              label1:
              plot2:
              scaler2:
              label2:
    """

    config: dict = None

    @classmethod
    def configure(cls, file: str) -> None:
        cls.config = flatten_yaml(read_yaml(file))
