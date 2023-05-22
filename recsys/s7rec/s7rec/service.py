import itertools
import json
import pickle
from dataclasses import dataclass


@dataclass
class Service:
    service: int
    flight: str
    service_class: str
    encrypt: int

class Catalog:
    """
    A helper class used to load service data upon server startup
    and store the data to redis.
    """

    def __init__(self, app):
        self.app = app
        self.services = []

    def load(self, catalog_path):
        self.app.logger.info(f"Loading services from {catalog_path}")
        with open(catalog_path) as catalog_file:
            for j, line in enumerate(catalog_file):
                data = json.loads(line)
                self.services.append(Service(data["service"], data["flight"], data["service_class"], data["encrypt"]))
        self.app.logger.info(f"Loaded {j+1} services")
        return self

    def upload_services(self, redis):
        self.app.logger.info(f"Uploading services to redis")
        for service in self.services:
            redis.set(service.service, self.to_bytes(service))
        self.app.logger.info(f"Uploaded {len(self.services)} services")

    def upload_flights(self, redis):
        self.app.logger.info(f"Uploading flights to redis")
        sorted_services = sorted(self.services, key=lambda t: t.flight)
        for j, (flight, flight_catalog) in enumerate(
            itertools.groupby(sorted_services, key=lambda t: t.flight)
        ):
            flight_services = [t.service for t in flight_catalog]
            redis.set(flight, self.to_bytes(flight_services))
        self.app.logger.info(f"Uploaded {j+1} flights")

    def to_bytes(self, instance):
        return pickle.dumps(instance)

    def from_bytes(self, bts):
        return pickle.loads(bts)