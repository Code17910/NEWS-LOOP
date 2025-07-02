from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)


# ✅ Configure your Gemini API Key
GEMINI_API_KEY = "AIzaSyAvzL_13CNVzpP0KVeGiwUEvdEWl3Ro5NU"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    import sys
    try:
        user_input = request.form.get("user_input", "").strip()
        user_link = request.form.get("user_link", "").strip()
        # image_file = request.files.get("image_input")

        def extract_probability(text):
            import re
            match = re.search(r"(\d{1,3}) ?%", text)
            if match:
                prob = int(match.group(1))
                if 0 <= prob <= 100:
                    return prob
            if any(word in text.lower() for word in ["very likely", "highly likely", "almost certainly"]):
                return 90
            if any(word in text.lower() for word in ["likely", "probably"]):
                return 75
            if any(word in text.lower() for word in ["possibly", "maybe"]):
                return 50
            if any(word in text.lower() for word in ["unlikely", "doubtful"]):
                return 25
            if any(word in text.lower() for word in ["very unlikely", "almost certainly not"]):
                return 10
            return None


        def call_gemini_api(prompt):
            headers = {
                "Content-Type": "application/json"
            }
            params = {
                "key": GEMINI_API_KEY
            }
            data = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ]
            }
            response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data)
            print("Gemini raw response:", response.text, file=sys.stderr)
            if response.status_code == 200:
                resp_json = response.json()
                try:
                    return resp_json["candidates"][0]["content"]["parts"][0]["text"]
                except Exception as e:
                    return f"Gemini API error: Could not parse response: {e}"
            else:
                return f"Gemini API error: {response.text}"

        try:


            if user_link:
                prompt = f"Analyze the content of this link and check for facts or misinformation: {user_link}. Estimate the probability (in percentage) that the news is truthful. Respond with your reasoning and a probability percentage."
                text = call_gemini_api(prompt)
                prob = extract_probability(text)
                reply = text
                if prob is not None:
                    reply += f"\n\nEstimated Truth Probability: {prob}%"
                if not reply.strip():
                    reply = "No response from Gemini API."
                return jsonify({"reply": reply})

            elif user_input:
                prompt = f"Analyze the following message for facts or misinformation. Estimate the probability (in percentage) that the news is truthful. Respond with your reasoning and a probability percentage. Message: {user_input}"
                text = call_gemini_api(prompt)
                prob = extract_probability(text)
                reply = text
                if prob is not None:
                    reply += f"\n\nEstimated Truth Probability: {prob}%"
                if not reply.strip():
                    reply = "No response from Gemini API."
                return jsonify({"reply": reply})

            else:
                return jsonify({"reply": "Please provide text, an image, or a link."}), 400
        except Exception as inner_e:
            print("Gemini inner exception:", inner_e, file=sys.stderr)
            return jsonify({"reply": f"Gemini API error: {inner_e}"}), 500

    except Exception as e:
        print("Flask outer exception:", e, file=sys.stderr)
        return jsonify({"reply": f"Flask error: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)

