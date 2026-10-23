from flask import Flask, request
import yaml

app = Flask(__name__)

@app.route("/parse", methods=["POST"])
def parse_yaml():
    data = request.data.decode("utf-8")
    parsed = yaml.load(data, Loader=yaml.Loader)  # intentionally unsafe
    return str(parsed)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)

