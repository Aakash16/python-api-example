from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flasgger import Swagger
import book_review
import logging
import signal, sys

app = Flask(__name__)
api = Api(app)
swagger = Swagger(app)

# Logging setup
logging.basicConfig(level=logging.INFO)

# Graceful shutdown for ECS
def handle_sigterm(*args):
    app.logger.info("Received SIGTERM, shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)


class UppercaseText(Resource):
    def get(self):
        text = request.args.get('text')
        if not text:
            return {"message": "Missing 'text' parameter"}, 400
        return jsonify({"text": text.upper()})


class Records(Resource):
    def get(self):
        count = request.args.get('count')
        sort = request.args.get('sort')
        try:
            books = book_review.get_all_records(count=count, sort=sort)
        except Exception as e:
            app.logger.error(f"Error fetching records: {e}")
            return {"error": "Internal Server Error"}, 500
        return {"books": books}, 200


class AddRecord(Resource):
    def post(self):
        data = request.json or {}
        if 'Book' not in data or 'Rating' not in data:
            return {"message": "Bad request, missing 'Book' or 'Rating'"}, 400
        try:
            success = book_review.add_record(data)
        except Exception as e:
            app.logger.error(f"Error adding record: {e}")
            return {"message": "Failed to add record"}, 500
        return {"message": "Record added successfully"} if success else {"message": "Failed to add record"}, 200


api.add_resource(AddRecord, "/add-record")
api.add_resource(Records, "/records")
api.add_resource(UppercaseText, "/uppercase")


@app.route("/health")
def health():
    return jsonify(status="healthy"), 200


# Only for local dev (Gunicorn runs in ECS)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
