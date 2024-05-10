import os
import numpy as np
from scipy.io import loadmat, savemat
from datetime import datetime


def combine_mat_files(root_dir, filenames, output_name):
    """
    Combines "data" field from multiple .mat files into a single file.

    Args:
        root_dir (str): Root directory containing the .mat files.
        filenames (list): List of filenames (without extension).
        output_name (str): Name of the output file (without extension).
    """
    # Initialize empty list to store combined data
    combined_data = []

    # Initialize header information dictionary
    header_info = {}

    # Construct full file paths
    full_filenames = [os.path.join(root_dir, f"{filename}.mat") for filename in filenames]

    # Iterate through filenames and accumulate data
    for filename in full_filenames:
        try:
            mat_contents = loadmat(filename)  # Load .mat file
            data = np.transpose(mat_contents["data"])  # Load "data" field
            combined_data.append(data)
            # Extract header information from the first file
            if not header_info:
                header_info = {key: value for key, value in mat_contents.items() if key != "data"}
        except KeyError:
            print(f"Warning: 'data' field not found in {filename}. Skipping.")

    # Get the creation time of the first file
    first_file_ctime = os.path.getctime(full_filenames[0])

    # Format the creation time as a human-readable string
    creation_time_str = datetime.fromtimestamp(first_file_ctime).strftime('%Y-%m-%d_%H-%M-%S')

    # Format the creation time as part of the output file name
    output_filename = f"{output_name}_{creation_time_str}.mat"

    # Save the combined data and header information to a new .mat file
    savemat(os.path.join(root_dir, output_filename), {"data": np.vstack(combined_data), **header_info})
    print(f"Combined data saved to: {os.path.join(root_dir, output_filename)}")
    print(np.vstack(combined_data))


# Define filenames (assuming j ranges from 0 to 7)
filenames = [f"pos2_2.49GHz_ch{j}" for j in range(1, 9)]

# Specify root directory (replace with your actual directory path)
root_dir = r"C:\Users\catnip\Downloads\pos2_2.49GHz"

if __name__ == "__main__":
    # Combine data and save as a new .mat file
    combine_mat_files(root_dir, filenames, output_name="combined_data")
