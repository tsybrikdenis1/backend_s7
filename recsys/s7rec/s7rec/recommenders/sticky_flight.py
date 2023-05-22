import random

from .random import Random
from .recommender import Recommender


class StickyFlight(Recommender):
    def __init__(self, services_redis, flights_redis, catalog):
        self.fallback = Random(services_redis)
        self.services_redis = services_redis
        self.flights_redis = flights_redis
        self.catalog = catalog

    def recommend_next(self, user: int, prev_service: int, prev_service_revenue: float) -> int:
        service_data = self.services_redis.get(prev_service)
        if service_data is not None:
            service = self.catalog.from_bytes(service_data)
        else:
            raise ValueError(f"Service not found: {prev_service}")

        flight_data = self.flights_redis.get(service.flight)
        if flight_data is not None:
            flight_services = self.catalog.from_bytes(flight_data)
        else:
            raise ValueError(f"Flight not found: {prev_service}")

        index = random.randint(0, len(flight_services) - 1)
        return flight_services[index]
