import os
import shutil
from pathlib import Path

def build(folder_name):
    # Create the destination folder if it doesn't exist
    folder_path = Path(folder_name)

    if not folder_path.exists():
        folder_path.mkdir(parents=True, exist_ok=True)
        print("Done")
    else:
        print(f"Folder '{folder_name}' already exists.")

    # Path to the current package directory (where this file is located)
    current_dir = Path(__file__).parent

    # List of files you want to copy from the package
    files_to_copy = [
     
"ART.py",
"Backpropagation.py",
"city.py",
"deltaRule.py",
"ErrorBackpropagation.py",
"FuzzyLogicTipping.py",
"Hebb’s rule.py",
"HopfieldNetwork.py",
"Kohonen Self.py",
"McCullochPitts ANDNOT.py",
"McCullochPittsXOR.py",
"MembershipOperators.py",
"RadialBasis.py",
"SigmoidFunction.py",
"SimplegenericAlgo.py",
"SimpleLinearNeuralNetwork.py"

    ]

    # Copy each file into the destination folder
    for file_name in files_to_copy:
        source_file = current_dir / file_name
        destination_file = folder_path / file_name

        if source_file.exists():
            shutil.copy(source_file, destination_file)
        else:
            print(f"File '{file_name}' not found in the package directory.")
