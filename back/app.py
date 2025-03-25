part_list = {
    'gear': ["gear", "cog", "toothed wheel", "gear wheel"],
    'rod': ["rod", "shaft", "bar", "cylinder"],
    "bracket" : ["bracket", "mount", "support"],
    "plate" : ["plate", "sheet", "panel"],
    "bearing" : ["ball bearing", "roller bearing"]
}

#Main app file
import os
# Core flask web framework
from flask import Flask, request, jsonify
#Runs external commands, used to run OpenSCAD
import subprocess

app = Flask(__name__)

# Builds URL path
@app.route('/generate', methods=['POST'])

def generate_cad():
    # Grab user text as input
    user_input = request.json.get('text', '')
    
    #generate SCAD code
    scad_code = generate_scad_from_text(user_input)
    
    
    if "Invalid" in scad_code:
        return jsonify({"message": scad_code}), 400
    
    
    #save SCAD code to a file
    with open('model.scad', 'w') as f:
        f.write(scad_code)
        
    # Use OpenSCAD to convert SCAD to STL (if openSCAD is installed on machinel)
    subprocess.run(["openscad", "-o", "model.stl", "model.scad"])
    
    # return a success message to the frontend
    return jsonify({"message": "STL File Generated Successfully!"}), 200


#includes scad code for certain part types
#TEMPORARY, TO BE REPLACED WITH NLP CODE FOR TEXT DETECTION
def generate_scad_from_text(text):
  text = text.lower()
  
  if "gear" in text:
      diameter = float(get_value_from_text(text, "diameter"))
      teeth = float(get_value_from_text(text, "teeth"))
      return generate_gear_scad(diameter, teeth)
  
  elif "rod" in text:
      length = float(get_value_from_text(text, "length"))
      diameter = float(get_value_from_text(text,"diameter"))
      return generate_rod_scad(length, diameter)
  
  elif "bracket" in text:
      length = float(get_value_from_text(text, "length"))
      width = float(get_value_from_text(text, "width"))
      return generate_bracket_scad(length, width)
      
  else:
      return "Invalid part type"

def get_value_from_text(text, key):
    import re
    pattern = re.compile(rf"{key}\s*[:\-]?\s*(\d+)\s*(mm|in|cm|ft)?", re.IGNORECASE)
    match = pattern.search(text)
    return match.group(1) if match else '0'

def generate_gear_scad(diameter, teeth):
    return f"""
    module gear(teeth, diameter) {{
        difference() {{
            circle(d=diameter);
            for (i = [0:teeth-1]) {{
                rotate(i * (360/teeth)) translate([diameter/2, 0, 0]) circle(d=2);
            }}
        }}
    }}

    gear({teeth}, {diameter});
    """
    
def generate_rod_scad(length, diameter):
    return f"""
    cylinder(h={length}, d={diameter});
    """

def generate_bracket_scad(length, width):
    return f"""
    cube([{length}, {width}, 10]);  # Bracket with 10mm height
    """

if __name__=='__main__':
    app.run(debug=True)
