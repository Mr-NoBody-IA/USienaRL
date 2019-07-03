# Import packages

import tensorflow
import numpy
import logging

# Import required src

from usienarl import Environment, Agent
from usienarl import Model


class Experiment:
    """
    Experiment with a certain model/parameters on a certain environment in which the agent guided by the model operates.
    It contains all data and methods to perform any kind of experiments.

    The standard experiment run is the following:
    - setup of the experiment
    - train for an interval of episodes (in training mode, also executes pre-training if necessary)
    - validate for a certain number of episodes (in exploit mode)
    - if validation is successful run a certain number of tests, otherwise train for another interval
    - run all the tests, each one for the required number of episodes (in exploit mode)

    The training mode updates the model parameters, the exploit mode just run the model to get the prediction on the
    best next action to perform by the agent on the environment.

    Any experiment requires a name for the experiments itself (usually after its environment), a validation and success threshold.
    The validation threshold is checked after any training interval, to check if it the proper time to exit training and start testing.
    The success threshold is checked during testing to determine whether or not the experiment is successful.

    An experiment can run only on one environment and with only one combination of model, memory and explorer.
    The batch size is required when specifying the memory (when the memory is not None) in order to choose how many
    samples to use when updating the model.

    Use the method conduct to run the experiment first in training and, after validation, in test mode.
    Use the method setup to prepare the environment for the next run.

    Attributes:
        - name: a string representing the name of the experiment, usually correlated with the name of the environment
        - environment: an environment representing the setting of the experiment (e.g. an OpenAI gym environment)
        - model: the temporal_difference model moving the agent operating on the environment
    """

    def __init__(self,
                 name: str,
                 validation_success_threshold: float, test_success_threshold: float,
                 environment: Environment,
                 agent: Agent,
                 pre_train_episodes: int):
        # Define the experiment name
        self.name: str = name
        # Define environment and agent attributes
        self.environment: Environment = environment
        self.agent: Agent = agent
        # Define experiment internal attributes
        self._validation_success_threshold: float = validation_success_threshold
        self._test_success_threshold: float = test_success_threshold
        self._pre_train_episodes: int = pre_train_episodes

    def setup(self,
              experiment_number: int,
              logger: logging.Logger) -> bool:
        """
        Setup the experiment, generating the model and resetting both tensorflow graph and the environment.

        :param experiment_number: number to append to the experiment name in all scopes and print statements (if not less than zero)
        :param logger: the logger currently used to print the experiment information, warnings and errors
        :return: a boolean equals to true if the generation of the model is successful, false otherwise
        """
        logger.info("Preparing experiment " + self.name + "_" + str(experiment_number) + "...")
        # Reset the tensorflow graph
        tensorflow.reset_default_graph()
        # Execute the setup on the environment and on the agent and return if not both of them setup correctly
        if not self.environment.setup():
            logger.info("Environment setup failed. Cannot setup the experiment!")
            return False
        if not self.agent.setup():
            logger.info("Agent setup failed. Cannot setup the experiment!")
            return False

        # Generate the model and return the success/failure state of this generation
        # return self.model.generate(self.name + "_" + str(experiment_number),
        #                            self.environment.observation_space_type, self.environment.observation_space_shape,
        #                            self.environment.action_space_type, self.environment.action_space_shape,
        #                            logger)

    def _pre_train(self,
                   episodes: int, session,
                   logger: logging.Logger):
        """
        Execute pre-training. Useful for preparing buffers or memories for the model. It is used only by some
        experiment types.

        :param episodes: the length, in episodes, of pre-training
        :param session: the session of tensorflow currently running
        :param logger: the logger currently used to print the experiment information, warnings and errors
        """
        # Empty method, definition should be implemented on a child class basis
        pass

    def _train(self,
               episodes: int, start_step: int, session,
               render: bool = False):
        """
        Execute an interval of training of the model on the environment with the given parameters.
        It also write TensorBoard summaries and save the model at the end of the interval.

        How the training is done depends on the type of experiment.

        :param episodes: the length, in episodes, of training
        :param start_step: the last step of the agent in the environment in the last interval (if any)
        :param session: the session of tensorflow currently running
        :param render: boolean parameter deciding whether or not to render during training
        :return: the float average of the score obtained in the played episodes and the step counter
        """
        # Empty method, definition should be implemented on a child class basis
        pass

    def _inference(self,
                   episodes: int, session,
                   render: bool = False):
        """
        Execute the model in inference mode on the environment, to compute the validation score or the test score
        depending on the validation boolean given parameter.

        The inference mode is universal for all kinds of experiments and models.

        :param episodes: the number of episodes in which to exploit the model on the environment
        :param session: the session of tensorflow currently running
        :param render: boolean parameter deciding whether or not to render during exploitation
        :return: the float average of the score obtained in the played episodes and the step counter
        """
        # Empty method, definition should be implemented on a child class basis
        pass

    def _train_step(self,
                    session,
                    state_current: numpy.ndarray,
                    render: bool = False):
        """
        Execute a train step in the environment.

        :param session: the session of tensorflow currently running
        :param state_current: the current state of the environment wrapped in a numpy array (ndarray)
        :param render: a boolean flag stating if the environment should be rendered in the step
        :return: the next state, the reward and the completion flag
        """
        # Get the action decided by the agent with train policy
        action = self.agent.act_pre_train(session, state_current)
        # Get the next state with relative reward and completion flag
        state_next, reward, episode_done = self.environment.step(action, session)
        # Render if required
        if render:
            self.environment.render(session)
        # Return the next state, the reward and the completion flag
        return state_next, reward, episode_done

    def _pre_train_step(self,
                        session,
                        state_current: numpy.ndarray,
                        render: bool = False):
        """
        Execute a pre-train step in the experiment.

        :param session: the session of tensorflow currently running
        :param state_current: the current state of the environment wrapped in a numpy array (ndarray)
        :param render: a boolean flag stating if the environment should be rendered in the step
        :return: the next state, the reward and the completion flag
        """
        # Get the action decided by the agent with pre-train policy
        action = self.agent.act_pre_train(session, state_current)
        # Get the next state with relative reward and completion flag
        state_next, reward, episode_done = self.environment.step(action, session)
        # Render if required
        if render:
            self.environment.render(session)
        # Return the next state, the reward and the completion flag
        return state_next, reward, episode_done

    def _inference_step(self,
                        session,
                        state_current: numpy.ndarray,
                        render: bool = False):
        """
        Execute an inference step in the environment.

        :param session: the session of tensorflow currently running
        :param state_current: the current state of the environment wrapped in a numpy array (ndarray)
        :param render: a boolean flag stating if the environment should be rendered in the step
        :return: the next state, the reward and the completion flag
        """
        # Get the action decided by the agent with inference policy
        action = self.agent.act_inference(session, state_current)
        # Get the next state with relative reward and completion flag
        state_next, reward, episode_done = self.environment.step(action, session)
        # Render if required
        if render:
            self.environment.render(session)
        # Return the next state, the reward and the completion flag
        return state_next, reward, episode_done

    def conduct(self,
                training_episodes_per_interval: int, validation_episodes_per_interval: int, max_training_episodes: int,
                episodes_per_test: int, number_of_tests: int,
                summary_path: str, metagraph_path: str,
                logger: logging.Logger,
                print_trainable_variables: bool = False,
                render_during_training: bool = False, render_during_validation: bool = False, render_during_test: bool = False,
                experiment_number: int = -1):
        """
        Conduct the experiment of the given number of training (up to the given maximum) and validation episodes
        per interval, with the associated given number of episodes per test and the given number of tests after
        the validation has passed.

        An interval of training is always considered to stop the training exactly when the model performs well enough
        to validate, having an average score greater than the required validation threshold.

        Conducting an experiment will generate a tensorflow session for that experiment. The tensorflow graph is reset
        and the default one is substituted with the one required by the ongoing experiment.

        :param training_episodes_per_interval: the number of training episodes per interval before trying to validate the model
        :param validation_episodes_per_interval: the number of validation episodes per interval after the training in such interval
        :param max_training_episodes: the maximum number of training episodes allowed in one interval
        :param episodes_per_test: the number of episodes to play for each test after validation has passed
        :param number_of_tests: the number of tests to execute after validation has passed
        :param summary_path: the string path of the TensorBoard summary directory to save during model training
        :param metagraph_path: the string path of the saved model directory to save at the end of each training interval
        :param logger: the logger currently used to print the experiment information, warnings and errors
        :param print_trainable_variables: boolean flag to print all the trainable variable of the model in the experiment at the end of the experiment
        :param render_during_training: boolean flag to render the environment during training (with automatic frame rate)
        :param render_during_validation: boolean flag to render the environment during validation (with automatic frame rate)
        :param render_during_test: boolean flag to render the environment during test (with automatic frame rate)
        :param experiment_number: number to append to the experiment name in all scopes and print statements (if not less than zero). Used to differentiate multiple copies of the same experiment
        :return: the final average score over all the tests, the best average score in a test among all the test and the training episodes required to validate the model
        """
        if experiment_number >= 0:
            logger.info("Conducting experiment " + self.name + "_" + str(experiment_number) + "...")
        else:
            logger.info("Conducting experiment " + self.name + "...")
        logger.info("Tensorboard summary path: " + summary_path)
        logger.info("Saved model metagraph path: " + metagraph_path)
        # Prepare the TensorBoard summary writer and the model saver
        if experiment_number >= 0:
            model_saver = tensorflow.train.Saver(self.agent.get_trainable_variables(self.name + "_" + str(experiment_number)))
        else:
            model_saver = tensorflow.train.Saver(self.agent.get_trainable_variables(self.name))
        summary_writer = tensorflow.summary.FileWriter(summary_path, graph=tensorflow.get_default_graph())
        # Tensorflow gpu configuration
        tensorflow_gpu_config = tensorflow.ConfigProto()
        tensorflow_gpu_config.gpu_options.allow_growth = True
        # Define the session
        with tensorflow.Session(config=tensorflow_gpu_config) as session:
            # Initialize the environment and the agent
            self.environment.initialize(session)
            self.agent.initialize(session)
            # Execute pre-training if the agent requires pre-training
            if self.agent.require_pre_train:
                logger.info("Pre-training for " + str(self._pre_train_episodes) + " episodes...")
                self._pre_train(self._pre_train_episodes, session)
            # Define experiment variables
            training_episodes_counter: int = 0
            training_steps_counter: int = 0
            # Execute training until max training episodes number is reached or the validation score is above the threshold
            while training_episodes_counter < max_training_episodes:
                # Run train for training interval episodes and get the average score
                logger.info("Training for " + str(training_episodes_per_interval) + " episodes...")
                training_score, training_step = self._train(experiment_number, summary_writer, model_saver, metagraph_path, training_episodes_per_interval, training_steps_counter, session, logger, render_during_training)
                # 
                # Increase training episodes and steps counter
                training_episodes_counter += training_episodes_per_interval
                training_steps_counter += training_step
                # Run inference for validation interval episodes and get the average score
                logger.info("Validating for " + str(validation_episodes_per_interval) + " episodes...")
                validation_score, validation_step = self._inference(validation_episodes_per_interval, session, render_during_validation)
                # Otherwise print intermediate results
                logger.info("Average score over " + str(validation_episodes_per_interval) + " episodes after " + str(training_episodes_counter) + " training episodes: " + str(validation_score))
                # Check for validation
                if self._validate(training_episodes_counter, training_steps_counter, validation_score):
                    logger.info("Validation of the model is successful")
                    break
            # Test the model, getting the average score per test and the final average score over all tests
            scores = []
            for test in range(number_of_tests):
                logger.info("Testing for " + str(episodes_per_test) + " episodes...")
                score: float = self._inference(episodes_per_test, session, render_during_test)
                logger.info("Average score over " + str(episodes_per_test) + " episodes: " + str(score))
                scores.append(score)
            # Get the final average score over all the test and the best score registered among all tests
            final_score: float = sum(scores) / episodes_per_test * number_of_tests
            best_score: float = numpy.max(scores)
            # Print final results and outcome of the experiment
            logger.info("Final average score is " + str(final_score) + " with " + str(training_episodes_counter) + " training episodes")
            logger.info("Best average score over " + str(episodes_per_test) + " is: " + str(best_score))
            if self._test(training_episodes_counter, training_steps_counter, final_score):
                logger.info("The experiment is successful")
            else:
                logger.info("The experiment is not successful")
            if print_trainable_variables:
                self.model.print_trainable_variables(self.name, session)
            return final_score, best_score, training_episodes_counter

    def _validate(self,
                  total_training_episodes: int, total_training_steps: int,
                  average_score: float) -> bool:
        pass

    def _test(self,
              total_training_episodes: int, total_training_steps: int,
              average_score: float) -> bool:
        pass
