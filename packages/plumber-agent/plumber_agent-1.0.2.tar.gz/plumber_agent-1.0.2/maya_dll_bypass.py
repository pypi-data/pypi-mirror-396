#!/usr/bin/env python3
"""
Maya DLL Bypass Strategy
Alternative Maya execution approach that avoids DLL import issues
"""

import subprocess
import tempfile
import json
import os

def create_maya_mel_wrapper(operation_type, params, output_dir):
    """Create a MEL script that executes Maya operations without Python DLL issues."""

    mel_script = f'''
// Maya MEL Script - Bypass Python DLL Issues
// Operation: {operation_type}
print("Maya MEL Script Starting - Operation: {operation_type}");

// Create basic scene
file -new -force;

// Example Maya operations via MEL
switch ("{operation_type}") {{
    case "create_sphere":
        // Create sphere
        polySphere -r 1 -sx 20 -sy 20 -ax 0 1 0 -cuv 2 -ch 1;
        rename "pSphere1" "test_sphere";
        print("Created sphere: test_sphere");

        // Get sphere info via MEL
        string $spheres[] = `ls -type "transform" "*sphere*"`;
        if (size($spheres) > 0) {{
            float $bbox[] = `exactWorldBoundingBox $spheres[0]`;
            print("Sphere bounding box: " + $bbox[0] + " " + $bbox[1] + " " + $bbox[2] + " " + $bbox[3] + " " + $bbox[4] + " " + $bbox[5]);
        }}
        break;

    case "create_cube":
        // Create cube
        polyCube -w 1 -h 1 -d 1 -sx 1 -sy 1 -sz 1 -ax 0 1 0 -cuv 4 -ch 1;
        rename "pCube1" "test_cube";
        print("Created cube: test_cube");
        break;

    case "scene_info":
        // Get scene information
        string $transforms[] = `ls -type "transform"`;
        print("Scene contains " + size($transforms) + " transforms");
        for ($transform in $transforms) {{
            print("Transform: " + $transform);
        }}
        break;

    default:
        print("Unknown operation: {operation_type}");
        break;
}}

// Save result to JSON file (via MEL file commands)
string $resultFile = "{output_dir.replace(chr(92), "/")}/maya_result.json";
string $resultJson = "{{" +
    "\\"status\\": \\"success\\", " +
    "\\"operation\\": \\"{operation_type}\\", " +
    "\\"message\\": \\"Maya MEL operation completed\\", " +
    "\\"maya_version\\": \\"" + `about -version` + "\\" " +
    "}}";

// Write result file
int $fileId = `fopen $resultFile "w"`;
if ($fileId > 0) {{
    fprint $fileId $resultJson;
    fclose $fileId;
    print("Result saved to: " + $resultFile);
}} else {{
    print("Failed to save result file: " + $resultFile);
}}

print("Maya MEL Script Completed");
quit -force;
'''

    return mel_script

def execute_maya_via_mel(operation_type, params, output_dir, maya_executable):
    """Execute Maya operation using MEL script to bypass Python DLL issues."""

    # Create MEL script
    mel_script = create_maya_mel_wrapper(operation_type, params, output_dir)

    # Write MEL script to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mel', delete=False, encoding='utf-8') as f:
        f.write(mel_script)
        mel_script_path = f.name

    try:
        # Execute Maya with MEL script
        cmd = [
            maya_executable,
            '-batch',
            '-command', f'source "{mel_script_path.replace(chr(92), "/")}"'
        ]

        print(f"Executing Maya MEL command: {' '.join(cmd)}")

        # Run Maya with MEL script
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,  # 1 minute timeout
            cwd=os.path.dirname(maya_executable)
        )

        print(f"Maya MEL execution completed with return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        if result.stderr:
            print(f"STDERR: {result.stderr}")

        # Check for result file
        result_file = os.path.join(output_dir, "maya_result.json")
        if os.path.exists(result_file):
            with open(result_file, 'r') as f:
                result_data = json.load(f)
            print(f"Maya operation result: {result_data}")
            return True, result_data
        else:
            return False, {"error": "No result file generated", "return_code": result.returncode}

    except subprocess.TimeoutExpired:
        return False, {"error": "Maya execution timed out"}
    except Exception as e:
        return False, {"error": f"Maya execution failed: {str(e)}"}
    finally:
        # Cleanup MEL script
        try:
            os.unlink(mel_script_path)
        except:
            pass

def test_maya_mel_execution():
    """Test Maya MEL execution."""
    print("Testing Maya MEL Execution")
    print("=" * 30)

    # Maya executable
    maya_exe = r"C:\Program Files\Autodesk\Maya2026\bin\maya.exe"

    if not os.path.exists(maya_exe):
        print(f"Maya not found at {maya_exe}")
        return False

    # Test output directory
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temp directory: {temp_dir}")

        # Test sphere creation
        success, result = execute_maya_via_mel("create_sphere", {}, temp_dir, maya_exe)

        if success:
            print("✅ Maya MEL execution successful!")
            print(f"Result: {result}")
            return True
        else:
            print("❌ Maya MEL execution failed")
            print(f"Error: {result}")
            return False

if __name__ == "__main__":
    test_maya_mel_execution()