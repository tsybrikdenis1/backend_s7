from collections import Counter
from dataclasses import dataclass
import numpy as np


@dataclass
class Booking:
    service: int
    revenue: float
    flight: str = None


class Session:
    def __init__(
        self, user: int, embedding: np.array, first_booking: Booking, budget: int
    ):
        self.user = user
        self.embedding = embedding
        self.budget = budget
        self.booking = [first_booking]
        self.finished = False

    def observe(self):
        return {"user": self.user, "service": self.booking[-1].service}

    def update(self, booking: Booking, budget_decrement: int):
        self.booking.append(booking)
        self.budget -= budget_decrement

    def finish(self):
        self.finished = True

    def flight_counts(self):
        return Counter([pb.flight for pb in self.booking])

    def __contains__(self, service):
        return any([pb.service == service for pb in self.booking])

    def __repr__(self):
        return (
            f"{self.user}:{self.booking}:{self.budget}" + "." if self.finished else ""
        )
