class Recommender:
    def recommend_next(self, user: int, prev_service: int, prev_service_revenue: float) -> int:
        raise NotImplementedError()