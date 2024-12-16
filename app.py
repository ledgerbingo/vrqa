from flask import Flask, render_template, request, jsonify
from google import genai
import cv2
import threading
import base64
import time

app = Flask(__name__)

# Initialize the genai client
client = genai.Client(
    api_key="YOUR_GEMINI_API_KEY"  # Replace with your actual API key
)

# Capture camera feed
camera_frame = None
def capture_camera():
    global camera_frame
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if ret:
            _, buffer = cv2.imencode('.jpg', frame)
            camera_frame = base64.b64encode(buffer).decode('utf-8')
        time.sleep(0.03)  # Slight delay for efficiency

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    question = request.json.get('question', '')
    if not question:
        return jsonify({"error": "No question provided."}), 400

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=question
        )
        return jsonify({"response": response.text})
    except Exception as e:
        app.logger.error(f"Error while processing request: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/camera_feed')
def camera_feed():
    if camera_frame:
        return jsonify({"frame": camera_frame})
    return jsonify({"error": "No frame available."}), 500

if __name__ == '__main__':
    threading.Thread(target=capture_camera, daemon=True).start()
    app.run(debug=True)
