import os
import subprocess
import tempfile
import shutil

def run_fbx_converter(input_file):
    # Path to the FbxConverter executable
    addon_dir = os.path.dirname(__file__)
    exe_path = os.path.join(addon_dir, "FbxConverter.exe")

    # Create a temporary file for the conversion
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".fbx")
    temp_file.close()

    # Command to run
    command = [exe_path, input_file, temp_file.name, "/v", "/l", "/f201300", "/e", "/binary"]
    
    # Run the command
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Replace the original file with the converted file
        shutil.move(temp_file.name, input_file)
        return {'INFO': result.stdout.decode()}
    except subprocess.CalledProcessError as e:
        os.remove(temp_file.name)  # Clean up the temporary file if there's an error
        return {'ERROR': e.stderr.decode()}


def run_kn5_converter(input_file, output_type):
    # Path to the KN5Converter executable
    addon_dir = os.path.dirname(__file__)
    exe_path = os.path.join(addon_dir, "kn5conv.exe")

    # Determine the output file name based on the input file and output type
    output_file = os.path.splitext(input_file)[0] + f".{output_type}"

    # Command to run the KN5 converter
    command = [exe_path, output_type, input_file]
    
    # Run the KN5 converter
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        info = result.stdout.decode()
    except subprocess.CalledProcessError as e:
        return {'ERROR': e.stderr.decode()}

    # If output type is "fbx", run the FBX converter on the created FBX file
    if output_type == "fbx":
        fbx_result = run_fbx_converter(output_file, output_file)
        if 'ERROR' in fbx_result:
            return fbx_result
        info += f"\n{fbx_result['INFO']}"

    return {'INFO': info}