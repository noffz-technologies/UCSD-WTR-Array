import scipy.io as sio


def display_mat_info(filename):
    """
  Reads a .mat file, displays header information, and variable contents.

  Args:
      filename (str): Path to the .mat file.
  """
    # Load data from the .mat file
    data = sio.loadmat(filename)

    # Display header information (variable names)
    print("Header Information (Variable Names):")
    for key in data.keys():
        if not key.startswith('__'):  # Exclude internal variables
            print(key)

    # Display variable contents
    print("\nVariable Contents:")
    for key, value in data.items():
        if not key.startswith('__'):  # Exclude internal variables
            print(f"{key}:\n{value}")  # Print variable name and content


# Get the filename from the user
filename = r"C:\Users\catnip\Downloads\pos2_2.49GHz\combined_data_2024-04-11_14-39-06"

if __name__ == "__main__":
    # Display information for the provided file
    display_mat_info(filename)
