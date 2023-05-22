import json

import numpy as np
import scipy.special as ss

from .config import UserCatalogConfig
from .session import Session, Booking
from .service import ServiceCatalog


class User:
    def __init__(
        self,
        user,
        interests,
        interest_neighbours,
        consume_bias,
        consume_sharpness,
        session_budget,
        flight_discount_gamma,
    ):
        self.user = user
        self.interests = interests
        self.interest_neighbours = interest_neighbours
        self.consume_bias = consume_bias
        self.consume_sharpness = consume_sharpness
        self.session_budget = session_budget
        self.flight_discount_gamma = flight_discount_gamma

    def new_session(self, service_catalog: ServiceCatalog):
        session_interest = np.random.choice(self.interests)
        session_interest_embedding = service_catalog.get_embedding(session_interest)

        nearest_services = service_catalog.get_nearest(
            session_interest_embedding, self.interest_neighbours
        )

        first_service = np.random.choice(
            [service for service in nearest_services[0] if service >= 0]
        )
        first_flight = service_catalog.get_flight(first_service)
        first_booking = Booking(first_service, 1.0, first_flight)

        return Session(
            self.user, session_interest_embedding, first_booking, self.session_budget
        )

    def consume(
        self, recommendation: int, session: Session, service_catalog: ServiceCatalog
    ):
        booking = self.buy(recommendation, session, service_catalog)
        budget_decrement = 1 if np.random.random() > booking.revenue else 0

        session.update(booking, budget_decrement)

        if session.budget <= 0:
            session.finish()

        return booking.revenue

    def buy(
        self, recommendation: int, session: Session, service_catalog: ServiceCatalog
    ) -> Booking:
        flight = service_catalog.get_flight(recommendation)

        # Users don't want to buy the same service twice
        if recommendation in session:
            return Booking(recommendation, 0.0, flight)

        recommendation_embedding = service_catalog.get_embedding(recommendation)
        score = np.dot(recommendation_embedding, session.embedding)
        raw_revenue = ss.expit((score - self.consume_bias) * self.consume_sharpness)

        # Users get upset when we recommend them the same service multiple times
        flight_discount = np.power(
            self.flight_discount_gamma, session.flight_counts()[flight]
        )
        revenue = np.around(raw_revenue * flight_discount, decimals=2)

        return Booking(recommendation, revenue, flight)

    def __repr__(self):
        return f"{self.user}"


class UserCatalog:
    def __init__(self, config: UserCatalogConfig):
        self.config = config
        self.users = []
        with open(config.user_catalog_path) as users_file:
            for line in users_file:
                user_data = json.loads(line)
                self.users.append(
                    User(
                        user_data["user"],
                        user_data["interests"],
                        user_data.get(
                            "interest_neighbours", config.default_interest_neighbours
                        ),
                        user_data.get("consume_bias", config.default_consume_bias),
                        user_data.get(
                            "consume_sharpness", config.default_consume_sharpness
                        ),
                        user_data.get("session_budget", config.default_session_budget),
                        user_data.get(
                            "flight_discount_gamma",
                            config.default_flight_discount_gamma,
                        ),
                    )
                )

    def sample_user(self):
        return np.random.choice(self.users)

    def size(self):
        return len(self.users)
