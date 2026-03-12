from flask import Flask, request, jsonify
import trimesh
import tempfile
import os

app = Flask(__name__)

# Material cost rates (per cm³)
rates = {
    "PLA": 0.38,
    "ABS": 0.5,
    "NYLON": 1.35,
    "HP PREMIUM NYLON": 2
}

@app.route('/analyze', methods=['POST'])
def analyze():

    # Get material from request
    material = request.form.get("material", "PLA").upper()

    if 'file' not in request.files:
        return jsonify({"error": "No STL file uploaded"}), 400

    file = request.files['file']

    # Save STL temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as temp:
        file.save(temp.name)

        mesh = trimesh.load(temp.name)

        volume_mm3 = mesh.volume
        surface_area = mesh.area

    os.remove(temp.name)

    # Convert mm³ → cm³
    volume_cm3 = volume_mm3 / 1000

    # Get rate
    rate = rates.get(material, 0.38)

    # Calculate cost
    cost = volume_cm3 * rate

    return jsonify({
        "surface_area_mm2": surface_area,
        "volume_mm3": volume_mm3,
        "volume_cm3": volume_cm3,
        "material": material,
        "cost": round(cost, 2)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)