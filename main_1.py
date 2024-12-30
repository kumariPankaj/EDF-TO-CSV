import os
import mne
import pandas as pd
# import sync

# Define the paths
edf_dir_path = r"C:\Users\Shree\Desktop\Projects\2023-hexoskin-study-data\hexoskin"  # Directory containing EDF files
csv_dir_path = r"C:\Users\Shree\Desktop\Projects\2023-hexoskin-study-data\overall"  # Directory to save CSV files

# Ensure the CSV directory exists
os.makedirs(csv_dir_path, exist_ok=True)

# Iterate over files in the EDF directory
for filename in os.listdir(edf_dir_path):
    file_path = os.path.join(edf_dir_path, filename)

    # Check if the file is an EDF file
    if file_path.endswith(".edf"):
        try:
            # Load the EDF file
            raw = mne.io.read_raw_edf(file_path, preload=True)

            # Extract data and metadata
            data = raw.get_data()               # Get signals
            times = raw.times                   # Get timestamps
            channel_names = raw.ch_names        # Get channel names

            # Check for shape consistency
            if data.shape[0] != len(channel_names):
                raise ValueError("Mismatch between data and channel names")

            # Create a DataFrame
            df = pd.DataFrame(data.T, columns=channel_names)  # Transpose data for proper format
            df['Time (s)'] = times                           # Add timestamps

            # Save DataFrame to CSV
            csv_file_path = os.path.join(csv_dir_path, f"{os.path.splitext(filename)[0]}.csv")
            df.to_csv(csv_file_path, index=False)

            print(f"EDF data from {filename} has been successfully saved to {csv_file_path}")
        except Exception as e:
            print(f"An error occurred while processing the file {filename}: {e}")
    else:
        print(f"Skipping non-EDF file: {filename}")
