from flask import Flask, request, jsonify
from flask_cors import CORS
from gradio_client import Client, handle_file
import tempfile
import os

app = Flask(__name__)
CORS(app)

SPACE_ID = "BABOUMAHA/breast-cancer-detector"

print("Connecting to Hugging Face Space...")
client = Client(SPACE_ID)
print("Connected.")


@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    uploaded_file = request.files["file"]

    if not uploaded_file.filename.endswith(".csv"):
        return jsonify({"error": "Please upload a valid CSV file"}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        uploaded_file.save(tmp.name)
        tmp_path = tmp.name

    try:
        result = client.predict(
            file=handle_file(tmp_path),
            api_name="/predict",
        )
        return jsonify({"data": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        os.remove(tmp_path)


if __name__ == "__main__":
    app.run(debug=True, port=5050)