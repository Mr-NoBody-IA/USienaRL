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
from usienarl.exploration_policies import EpsilonGreedyExplorationPolicy, BoltzmannExplorationPolicy

# Import required src
# Require error handling to support both deployment and pycharm versions

try:
    from src.tabular_q_learning_agent import TabularQLearningAgent
    from src.openai_gym_environment import OpenAIGymEnvironment
    from src.benchmark_experiment import BenchmarkExperiment
except ImportError:
    from usienarl.agents.tabular_q_learning_agent_epsilon_greedy import TabularQLearningAgent
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


def _define_epsilon_greedy_exploration_policy() -> EpsilonGreedyExplorationPolicy:
    # Define attributes
    exploration_rate_max: float = 1.0
    exploration_rate_min: float = 0.001
    exploration_rate_decay: float = 0.001
    # Return the explorer
    return EpsilonGreedyExplorationPolicy(exploration_rate_max, exploration_rate_min, exploration_rate_decay)


def _define_boltzmann_exploration_policy() -> BoltzmannExplorationPolicy:
    # Define attributes
    temperature_max: float = 1.0
    temperature_min: float = 0.001
    temperature_decay: float = 0.001
    # Return the explorer
    return BoltzmannExplorationPolicy(temperature_max, temperature_min, temperature_decay)


def _define_epsilon_greedy_agent(model: TabularQLearning, exploration_policy: EpsilonGreedyExplorationPolicy) -> TabularQLearningAgent:
    # Define attributes
    batch_size: int = 100
    # Return the agent
    return TabularQLearningAgent("tql_egreedy_agent", model, exploration_policy, batch_size)


def _define_boltzmann_agent(model: TabularQLearning, exploration_policy: BoltzmannExplorationPolicy) -> TabularQLearningAgent:
    # Define attributes
    batch_size: int = 100
    # Return the agent
    return TabularQLearningAgent("tql_boltzmann_agent", model, exploration_policy, batch_size)


if __name__ == "__main__":
    # Parse the command line arguments
    workspace_path, experiment_iterations_number, cuda_devices, render_during_training, render_during_validation, render_during_test = command_line_parse()
    # Define the CUDA devices in which to run the experiment
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = cuda_devices
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
    # Define exploration_policies
    epsilon_greedy_exploration_policy: EpsilonGreedyExplorationPolicy = _define_epsilon_greedy_exploration_policy()
    boltzmann_exploration_policy: BoltzmannExplorationPolicy = _define_boltzmann_exploration_policy()
    # Define agents
    tql_epsilon_greedy_agent: TabularQLearningAgent = _define_epsilon_greedy_agent(inner_model, epsilon_greedy_exploration_policy)
    tql_boltzmann_agent: TabularQLearningAgent = _define_boltzmann_agent(inner_model, boltzmann_exploration_policy)
    # Define experiments
    experiment_egreedy: BenchmarkExperiment = BenchmarkExperiment("eg_experiment", success_threshold, environment,
                                                                  tql_epsilon_greedy_agent)
    experiment_boltzmann: BenchmarkExperiment = BenchmarkExperiment("b_experiment", success_threshold, environment,
                                                                    tql_boltzmann_agent)
    # Define experiments data
    testing_episodes: int = 100
    test_cycles: int = 10
    training_episodes: int = 100
    validation_episodes: int = 100
    max_training_episodes: int = 10000
    episode_length_max: int = 100
    # Run epsilon greedy experiment
    run_experiment(experiment_egreedy,
                   training_episodes,
                   max_training_episodes, episode_length_max,
                   validation_episodes,
                   testing_episodes, test_cycles,
                   render_during_training, render_during_validation, render_during_test,
                   workspace_path, __file__,
                   logger, None, experiment_iterations_number)
    # Run boltzmann experiment
    run_experiment(experiment_boltzmann,
                   training_episodes,
                   max_training_episodes, episode_length_max,
                   validation_episodes,
                   testing_episodes, test_cycles,
                   render_during_training, render_during_validation, render_during_test,
                   workspace_path, __file__,
                   logger, None, experiment_iterations_number)
