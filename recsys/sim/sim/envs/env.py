import gym
import numpy as np
from gym.spaces import Discrete, Dict

from .config import RecEnvConfig
from .service import ServiceCatalog
from .user import UserCatalog


class RecEnv(gym.Env):

    metadata = {"render.modes": ["human"]}

    def __init__(self, config: RecEnvConfig):
        super(RecEnv, self).__init__()
        self.config = config

        self.service_catalog = ServiceCatalog(config.service_catalog_config)
        self.user_catalog = UserCatalog(config.user_catalog_config)

        # At each step you suggest a service, so each action is a single service ID
        self.action_space = Discrete(self.service_catalog.size())

        # We need to provide a user ID to the recommender and the initial service
        self.observation_space = Dict(
            user=Discrete(self.user_catalog.size()),
            service=Discrete(self.service_catalog.size()),
        )

        self.user = None
        self.session = None

        self.reset()

    def step(self, recommendation: int):
        assert self.action_space.contains(recommendation), str(recommendation)
        booking_time = self.user.consume(
            recommendation, self.session, self.service_catalog
        )
        return self.session.observe(), booking_time, self.session.finished, None

    def reset(self):
        self.user = self.user_catalog.sample_user()
        self.session = self.user.new_session(self.service_catalog)
        return self.session.observe()

    def render(self, mode="human", close=False):
        print(f"Current session: {self.session}")

    def seed(self, seed=None):
        np.random.seed(seed)
