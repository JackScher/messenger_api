from api import create_app
from flask import jsonify


app = create_app()


@app.route('/routes', methods=['GET'])
def get_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,
            "methods": list(rule.methods),
            "rule": str(rule)
        })
    return jsonify(routes)


if __name__ == "__main__":
    app.run("localhost", 5000)
