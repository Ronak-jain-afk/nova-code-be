from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv
from flask_cors import CORS


load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow all origins (good for dev)


# Judge0 API (via RapidAPI)
JUDGE0_URL = "https://judge0-ce.p.rapidapi.com/submissions"

# Store your API key securely (e.g., environment variable)
API_KEY = os.getenv("JUDGE0_API_KEY", "YOUR_RAPIDAPI_KEY_HERE")

HEADERS = {
    "Content-Type": "application/json",
    "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
    "X-RapidAPI-Key": API_KEY
}

@app.route("/run", methods=["POST"])
def run_code():
    try:
        data = request.json
        source_code = data.get("code")
        language_id = data.get("language_id")
        stdin = data.get("input", "")

        if not source_code or not language_id:
            return jsonify({"error": "code and language_id are required"}), 400

        # Step 1: Create a submission
        submission_data = {
            "source_code": source_code,
            "language_id": language_id,
            "stdin": stdin
        }

        submission_res = requests.post(
            f"{JUDGE0_URL}?base64_encoded=false&wait=true",
            json=submission_data,
            headers=HEADERS
        )

        if submission_res.status_code not in [200, 201]:
            return jsonify({
                "error": "Failed to create submission",
                "details": submission_res.text
             }), 500


        result = submission_res.json()

        # Step 2: Return result to frontend
        return jsonify({
            "stdout": result.get("stdout"),
            "stderr": result.get("stderr"),
            "compile_output": result.get("compile_output"),
            "message": result.get("message"),
            "status": result.get("status", {}).get("description")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
