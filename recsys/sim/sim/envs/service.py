import faiss
import pandas as pd
import numpy as np

from sim.envs.config import ServiceCatalogConfig


class ServiceCatalog:
    def __init__(self, config: ServiceCatalogConfig):
        self.config = config
        self.service_embeddings = np.load(config.service_embeddings_path)
        self.index = self.build_service_index()

        service_meta = pd.read_json(config.service_meta_path, lines=True).sort_values(
            "service"
        )
        # Check that meta is consistent with embeddings
        assert np.array_equal(service_meta["service"].values, np.arange(self.size()))
        self.service_flights = service_meta["flight"].values

    def build_service_index(self) -> faiss.Index:
        index = faiss.index_factory(
            self.service_embeddings.shape[1], "Flat", faiss.METRIC_INNER_PRODUCT
        )
        index.add(self.service_embeddings)
        return index

    def get_embedding(self, service):
        return self.service_embeddings[service]

    def get_flight(self, service):
        return self.service_flights[service]

    def get_nearest(self, query, k):
        dist, ind = self.index.search(query[np.newaxis, :], k)
        return ind

    def size(self):
        return self.service_embeddings.shape[0]
