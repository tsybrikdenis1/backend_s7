from .recommender import Recommender


class Random(Recommender):
    def __init__(self, service_redis):
        self.service_redis = service_redis

    def recommend_next(self, user: int, prev_service: int, prev_service_revenue: float) -> int:
        return int(self.service_redis.randomkey())
