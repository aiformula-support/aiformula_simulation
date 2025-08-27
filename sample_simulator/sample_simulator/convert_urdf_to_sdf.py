"""Convert urdf file to sdf file

Parameters:
----------
`urdf_path`: Source urdf file path
`sdf_path`: Converted sdf file path

Examples:
----------
>>> python3 convert_urdf_to_sdf.py /path/to/robot.urdf /path/to/robot.sdf
"""

import subprocess
from pathlib import Path

def convert_urdf_to_sdf(urdf_path: str, sdf_path: str) -> None: 
    urdf_path = Path(urdf_path)
    sdf_path = Path(sdf_path)    
    result = subprocess.run(
        ["gz", "sdf", "-p", str(urdf_path)],
        capture_output=True,
        text=True,
        check=True
    ).stdout

    out = result.replace('sample_vehicle/xacro', 'ai_mobility_1')
    sdf_path.write_text(out, encoding="utf-8")
