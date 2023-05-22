from typing import Dict, Optional
from urllib.parse import urlunsplit

import requests

from .recommender import Recommender
from ..envs import RemoteRecommenderConfig

SCHEME = "http"


class ConsoleRecommender(Recommender):
    """Provide recommendations manually, ftw"""

    def __init__(self, config: RemoteRecommenderConfig):
        self.config = config

    def recommend(self, observation: Dict[str, int], reward: float, done: bool) -> int:
        previous_service_info = self.load_service_info(observation["service"])
        print(
            f"Got previous service {self.format(previous_service_info)} for user {observation['user']} with reward {reward}"
        )

        recommendation = None
        while recommendation is None:
            print("Enter recommended service:")
            recommendation = self.parse_input()

        return recommendation

    def parse_input(self) -> Optional[int]:
        try:
            recommendation = int(input())
        except ValueError as va:
            return None

        service_info = self.load_service_info(recommendation)
        if service_info is None:
            print(f"Could not load service {recommendation}")
            return None
        else:
            print(f"Recommending service {self.format(service_info)}")
            return recommendation

    def load_service_info(self, service) -> Optional[Dict]:
        url = urlunsplit(
            (SCHEME, f"{self.config.host}:{self.config.port}", f"service/{service}", {}, "")
        )
        response = requests.get(url)

        if response.status_code != 200:
            return None

        return response.json()

    def format(self, service_info):
        return f"'{service_info['flight']}' service-class: '{service_info['service_class']}' service_id '{service_info['service']}'"

    def __repr__(self):
        return "console"
