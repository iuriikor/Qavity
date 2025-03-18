import subprocess
import os

def run_artiq_in_clang64_visible(script_path):
    batch_file = 'C:/Users/CavLev/Documents/Qavity/controllers/sinara/run_artiq_script.bat'
    try:
#         # Path to MSYS2 clang64 executable - update this path as needed
#         msys2_path = "C:/msys64"
#
#         # Create a batch file to run the command in clang64
#         batch_content = f"""@echo off
# call {msys2_path}\\msys2_shell.cmd -clang64 -here -no-start -defterm -c "artiq_run {script_path}; echo 'Command completed';"
# """
#
#         # Write the batch file
#         batch_file = "run_artiq.bat"
#         with open(batch_file, "w") as f:
#             f.write(batch_content)
#

        # Execute the batch file
        # subprocess.run(
        #     'C:\\Users\\CavLev\\Documents\\Experiment_control_scripts\\artiq\\artiq-master\\artiq_run_script.bat')
        subprocess.run([batch_file, script_path])
        # Clean up the batch file
        # os.remove(batch_file)

        return "Command executed in MSYS2 window"

    except Exception as e:
        print("Exception occurred:", str(e))
        return None