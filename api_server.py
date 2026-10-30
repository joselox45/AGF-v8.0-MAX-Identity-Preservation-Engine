from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json
import uuid
import subprocess

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route("/")
def health_check():
    return jsonify({"status": "AGF API is running", "version": "v12.3.3", "engine": "Flask"})

@app.route("/api/v1/verify", methods=["POST"])
def verify_images():
    if "original" not in request.files or "generated" not in request.files:
        return jsonify({"error": "Faltan las imágenes 'original' o 'generated'"}), 400

    file_orig = request.files["original"]
    file_gen = request.files["generated"]
    mode = request.form.get("mode", "preservation")

    unique_id = uuid.uuid4().hex
    orig_path = f"temp_orig_{unique_id}.jpg"
    gen_path = f"temp_gen_{unique_id}.jpg"
    output_path = f"termux_sealed/audit_{unique_id}.json"
    
    file_orig.save(orig_path)
    file_gen.save(gen_path)

    try:
        cmd = [
            sys.executable, "tools/agf_composite_scorer.py",
            orig_path, gen_path, "blaze_face_short_range.tflite", 
            "--mode", mode, "--output", output_path
        ]
        
        res = subprocess.run(cmd, capture_output=True, text=True)
        
        if res.returncode != 0:
            reason_msg = "Scorer failed without explicit reason"
            for line in res.stdout.split('\n'):
                if "BLOCKED" in line or "❌" in line:
                    reason_msg = line.strip()
                    break
                    
            return jsonify({
                "verdict": "BLOCKED", 
                "reason": reason_msg, 
                "stderr": res.stderr[-300:], 
                "agf_score": 0.0
            }), 200
            
        if not os.path.exists(output_path):
            return jsonify({
                "verdict": "BLOCKED", 
                "reason": "No output file produced by scorer", 
                "agf_score": 0.0
            }), 200
            
        with open(output_path, "r") as f:
            data = json.load(f)
            
        os.remove(output_path)
        return jsonify(data)

    except Exception as e:
        return jsonify({"verdict": "BLOCKED", "reason": f"API Exception: {str(e)}", "agf_score": 0.0}), 200

    finally:
        if os.path.exists(orig_path): os.remove(orig_path)
        if os.path.exists(gen_path): os.remove(gen_path)

if __name__ == "__main__":
    os.makedirs("termux_sealed", exist_ok=True)
    app.run(host="0.0.0.0", port=8000, debug=False)
