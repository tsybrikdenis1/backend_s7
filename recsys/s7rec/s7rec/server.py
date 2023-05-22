import json
import logging
import time
from dataclasses import asdict
from datetime import datetime

from flask import Flask
from flask_redis import Redis
from flask_restful import Resource, Api, abort, reqparse

from s7rec.data import DataLogger, Datum
from s7rec.experiment import Experiments, Treatment
from s7rec.recommenders.random import Random
from s7rec.recommenders.sticky_flight import StickyFlight
from s7rec.service import Catalog

root = logging.getLogger()
root.setLevel("INFO")

app = Flask(__name__)
app.config.from_file("config.json", load=json.load)
api = Api(app)

services_redis = Redis(app, config_prefix="REDIS_SERVICES")
flights_redis = Redis(app, config_prefix="REDIS_FLIGHT")

data_logger = DataLogger(app)

catalog = Catalog(app).load(app.config["SERVICES_CATALOG"])
catalog.upload_services(services_redis.connection)
catalog.upload_flights(flights_redis.connection)

parser = reqparse.RequestParser()
parser.add_argument("service", type=int, location="json", required=True)
parser.add_argument("revenue", type=float, location="json", required=True)


class Hello(Resource):
    def get(self):
        return {
            "status": "alive",
            "message": "welcome to s7rec pet-project flight-services recommender",
        }


class Service(Resource):
    def get(self, service: int):
        data = services_redis.connection.get(service)
        if data is not None:
            return asdict(catalog.from_bytes(data))
        else:
            abort(404, description="Service not found")


class NextService(Resource):
    def post(self, user: int):
        start = time.time()

        args = parser.parse_args()

        treatment = Experiments.STICKY_FLIGHT.assign(user)
        if treatment == Treatment.T1:
            recommender = StickyFlight(services_redis.connection, flights_redis.connection, catalog)
        else:
            recommender = Random(services_redis.connection)

        recommendation = recommender.recommend_next(user, args.service, args.revenue)

        data_logger.log(
            "next",
            Datum(
                int(datetime.now().timestamp() * 1000),
                user,
                args.service,
                args.revenue,
                time.time() - start,
                recommendation,
            ),
        )
        return {"user": user, "service": recommendation}


class LastService(Resource):
    def post(self, user: int):
        start = time.time()
        args = parser.parse_args()
        data_logger.log(
            "last",
            Datum(
                int(datetime.now().timestamp() * 1000),
                user,
                args.service,
                args.revenue,
                time.time() - start,
            ),
        )
        return {"user": user}


api.add_resource(Hello, "/")
api.add_resource(Service, "/service/<int:service>")
api.add_resource(NextService, "/next/<int:user>")
api.add_resource(LastService, "/last/<int:user>")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7777)
