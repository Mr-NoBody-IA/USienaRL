#
# Copyright (C) 2019 Luca Pasqualini
# University of Siena - Artificial Intelligence Laboratory - SAILab
#
#
# USienaRL is licensed under a BSD 3-Clause.
#
# You should have received a copy of the license along with this
# work. If not, see <https://opensource.org/licenses/BSD-3-Clause>.

# Import packages

import logging
import os

# Import usienarl

from usienarl import run_experiment, command_line_parse
from usienarl.td_models import TabularQLearning
from usienarl.agents import TabularQLearningAgentEpsilonGreedy, TabularQLearningAgentBoltzmann, TabularQLearningAgentDirichlet

# Import required src
# Require error handling to support both deployment and pycharm versions

try:
    from src.openai_gym_environment import OpenAIGymEnvironment
    from src.benchmark_experiment import BenchmarkExperiment
except ImportError:

    from benchmarks.src.openai_gym_environment import OpenAIGymEnvironment
    from benchmarks.src.benchmark_experiment import BenchmarkExperiment

# Define utility functions to run the experiment


def _define_tql_model() -> TabularQLearning:
    # Define attributes
    learning_rate: float = 0.001
    discount_factor: float = 0.99
    buffer_capacity: int = 1000
    minimum_sample_probability: float = 0.01
    random_sample_trade_off: float = 0.6
    importance_sampling_value_increment: float = 0.4
    importance_sampling_value: float = 0.001
    # Return the _model
    return TabularQLearning("model",
                            learning_rate, discount_factor,
                            buffer_capacity,
                            minimum_sample_probability, random_sample_trade_off,
                            importance_sampling_value, importance_sampling_value_increment)


def _define_epsilon_greedy_agent(model: TabularQLearning) -> TabularQLearningAgentEpsilonGreedy:
    # Define attributes
    weight_copy_step_interval: int = 25
    batch_size: int = 100
    exploration_rate_max: float = 1.0
    exploration_rate_min: float = 0.001
    exploration_rate_decay: float = 0.001
    # Return the agent
    return TabularQLearningAgentEpsilonGreedy("tql_agent", model, batch_size,
                                              exploration_rate_max, exploration_rate_min, exploration_rate_decay)


def _define_boltzmann_agent(model: TabularQLearning) -> TabularQLearningAgentBoltzmann:
    # Define attributes
    batch_size: int = 100
    temperature_max: float = 1.0
    temperature_min: float = 0.001
    temperature_decay: float = 0.001
    # Return the agent
    return TabularQLearningAgentBoltzmann("tql_agent", model, batch_size,
                                          temperature_max, temperature_min, temperature_decay)


def _define_dirichlet_agent(model: TabularQLearning) -> TabularQLearningAgentDirichlet:
    # Define attributes
    batch_size: int = 100
    alpha: float = 1.0
    dirichlet_trade_off_min: float = 0.5
    dirichlet_trade_off_max: float = 1.0
    dirichlet_trade_off_update: float = 0.001
    # Return the agent
    return TabularQLearningAgentDirichlet("tql_agent", model,  batch_size,
                                          alpha, dirichlet_trade_off_min, dirichlet_trade_off_max, dirichlet_trade_off_update)


def run(workspace: str,
        experiment_iterations: int,
        render_training: bool, render_validation: bool, render_test: bool):
    # Define the logger
    logger: logging.Logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    # Frozen Lake environment:
    #       - general success threshold to consider the training and the experiment successful is 0.78 over 100 episodes according to OpenAI guidelines
    environment_name: str = 'FrozenLake-v0'
    success_threshold: float = 0.78
    # Generate the OpenAI environment
    environment: OpenAIGymEnvironment = OpenAIGymEnvironment(environment_name)
    # Define model
    inner_model: TabularQLearning = _define_tql_model()
    # Define agents
    tql_agent_epsilon_greedy: TabularQLearningAgentEpsilonGreedy = _define_epsilon_greedy_agent(inner_model)
    tql_agent_boltzmann: TabularQLearningAgentBoltzmann = _define_boltzmann_agent(inner_model)
    tql_agent_dirichlet: TabularQLearningAgentDirichlet = _define_dirichlet_agent(inner_model)
    # Define experiments
    experiment_epsilon_greedy: BenchmarkExperiment = BenchmarkExperiment("experiment_epsilon_greedy", success_threshold, environment,
                                                                         tql_agent_epsilon_greedy)
    experiment_boltzmann: BenchmarkExperiment = BenchmarkExperiment("experiment_boltzmann", success_threshold, environment,
                                                                    tql_agent_boltzmann)
    experiment_dirichlet: BenchmarkExperiment = BenchmarkExperiment("experiment_dirichlet", success_threshold, environment,
                                                                    tql_agent_dirichlet)
    # Define experiments data
    testing_episodes: int = 100
    test_cycles: int = 10
    training_episodes: int = 100
    validation_episodes: int = 100
    max_training_episodes: int = 10000
    episode_length_max: int = 100
    # Run experiments
    run_experiment(experiment_epsilon_greedy,
                   training_episodes,
                   max_training_episodes, episode_length_max,
                   validation_episodes,
                   testing_episodes, test_cycles,
                   render_training, render_validation, render_test,
                   workspace, __file__,
                   logger, None, experiment_iterations)
    run_experiment(experiment_boltzmann,
                   training_episodes,
                   max_training_episodes, episode_length_max,
                   validation_episodes,
                   testing_episodes, test_cycles,
                   render_training, render_validation, render_test,
                   workspace, __file__,
                   logger, None, experiment_iterations)
    run_experiment(experiment_dirichlet,
                   training_episodes,
                   max_training_episodes, episode_length_max,
                   validation_episodes,
                   testing_episodes, test_cycles,
                   render_training, render_validation, render_test,
                   workspace, __file__,
                   logger, None, experiment_iterations)


if __name__ == "__main__":
    # Parse the command line arguments
    workspace_path, experiment_iterations_number, cuda_devices, render_during_training, render_during_validation, render_during_test = command_line_parse()
    # Define the CUDA devices in which to run the experiment
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = cuda_devices
    # Run this experiment
    run(workspace_path, experiment_iterations_number, render_during_training, render_during_validation, render_during_test)
