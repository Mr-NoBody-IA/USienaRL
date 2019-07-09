# Import packages

import logging

# Import required src

from usienarl import SpaceType


class ExplorationPolicy:
    """
    TODO: summary
    """

    def __init__(self):
        # Define empty exploration policy attributes
        self._agent_action_space_type: SpaceType = None
        self._agent_action_space_shape = None
        self._supported_action_space_types: [] = []

    def generate(self,
                 logger: logging.Logger,
                 agent_action_space_type: SpaceType, agent_action_space_shape) -> bool:
        """
        Generate the exploration policy. Checks if the exploration policy is compatible with the given action space and
        define the exploration policy itself.

        :param logger: the logger used to print the exploration policy information, warnings and errors
        :param agent_action_space_type: the space type of the agent action space
        :param agent_action_space_shape: the space shape of the agent action space
        :return: True if generation is successful, False otherwise
        """
        logger.info("Generating exploration policy...")
        # Set action space type and shape
        self._agent_action_space_type = agent_action_space_type
        self._agent_action_space_shape = agent_action_space_shape
        # Check if action space type is supported
        action_space_type_supported: bool = False
        for space_type in self._supported_action_space_types:
            if self._agent_action_space_type == space_type:
                action_space_type_supported = True
                break
        if not action_space_type_supported:
            logger.error("Error during setup of exploration policy: action space type not supported")
            return False
        # Define the exploration policy
        self._define()
        # Return success
        return True

    def _define(self):
        """
        Define the exploration policy. This is always called during generation.
        """
        raise NotImplementedError()

    def initialize(self,
                   logger: logging.Logger,
                   session):
        """
        Reset the exploration policy to its starting state, usually resetting the exploration rate to its max value.

        :param logger: the logger used to print the exploration policy information, warnings and errors
        :param session: the session of tensorflow currently running, if any
        """
        raise NotImplementedError()

    def act(self,
            session,
            all_actions, best_action):
        """
        Act according to the model actions and/or predicted action.

        :param session: the session of tensorflow currently running, if any
        :param all_actions: all the action values predicted by the model
        :param best_action: the best (usually highest) action value predicted by the model
        """
        # Abstract method, definition should be implemented on a child class basis
        raise NotImplementedError()

    def update(self,
               session):
        """
        Update the exploration policy, usually changing the exploration rate.

        :param session: the session of tensorflow currently running, if any
        """
        raise NotImplementedError()
