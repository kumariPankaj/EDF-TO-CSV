import os
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

# Define paths
input_folder = r"C:\Users\Shree\Desktop\Projects\2023-hexoskin-study-data\overall"
output_folder = r"C:\Users\Shree\Desktop\Projects\2023-hexoskin-study-data\synchronizing_Data_2"
os.makedirs(output_folder, exist_ok=True)  # Ensure output folder exists

# Define a function to resample data
def resample_data(data, original_fs, target_fs):
    time_original = np.linspace(0, len(data) / original_fs, len(data), endpoint=False)
    time_new = np.linspace(0, len(data) / original_fs, int(len(data) * target_fs / original_fs), endpoint=False)
    interpolator = interp1d(time_original, data, kind='linear', fill_value='extrapolate')
    return interpolator(time_new)

# Process CSV files
for file_name in os.listdir(input_folder):
    if file_name.endswith(".csv"):
        print(f"Processing file: {file_name}")
        
        # Load the CSV
        file_path = os.path.join(input_folder, file_name)
        df = pd.read_csv(file_path)
        print(f"Columns: {df.columns}")
        
        # Define relevant columns (adjust based on actual column names in your data)
        ecg_column = '4113:ECG_I'
        accel_columns = ['4145:accel_X', '4146:accel_Y', '4147:accel_Z']
        
        # Ensure relevant columns exist
        if ecg_column not in df.columns or not all(col in df.columns for col in accel_columns):
            print(f"Skipping {file_name} due to missing columns.")
            continue
        
        # Extract ECG and accelerometer data
        ecg_data = df[ecg_column].dropna().values
        accel_data = df[accel_columns].dropna().values
        
        # Sampling rates
        fs_ecg = 256  # ECG data is at 256 Hz
        fs_accel = 64  # Accelerometer data is at 64 Hz
        
        # Resample accelerometer data to match ECG sampling rate
        accel_resampled = np.array([resample_data(accel_data[:, i], fs_accel, fs_ecg) for i in range(accel_data.shape[1])]).T
        
        # Calculate accelerometer magnitude
        accel_magnitude = np.sqrt(np.sum(accel_resampled**2, axis=1))
        
        # Generate timestamps (assuming the first sample starts at time 0)
        timestamps = np.linspace(0, len(ecg_data) / fs_ecg, len(ecg_data), endpoint=False)
        
        # Ensure all arrays are of the same length
        min_length = min(len(timestamps), len(ecg_data), len(accel_magnitude))
        timestamps = timestamps[:min_length]
        ecg_data = ecg_data[:min_length]
        accel_magnitude = accel_magnitude[:min_length]
        
        # Create the cleaned DataFrame
        cleaned_df = pd.DataFrame({
            'Timestamp': timestamps,
            'ECG': ecg_data,
            'Accel_Magnitude': accel_magnitude
        })
        
        # Save the cleaned file
        output_file_path = os.path.join(output_folder, f"cleaned_{file_name}")
        cleaned_df.to_csv(output_file_path, index=False)
        print(f"Cleaned file saved: {output_file_path}")
        
        # Plot the data
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, ecg_data, label='ECG')
        plt.plot(timestamps, accel_magnitude, label='Accel Magnitude', alpha=0.7)
        plt.xlabel('Time (s)')
        plt.ylabel('Signal')
        plt.legend()
        plt.title(f"ECG and Accelerometer Data for {file_name}")
        
        # Show the timestamps on the x-axis
        plt.xticks(timestamps[::int(len(timestamps)/10)], rotation=45)  # Show every 10th timestamp for better readability
        
        # Save the plot
        plot_file_path = os.path.join(output_folder, f"plot_{os.path.splitext(file_name)[0]}.png")
        plt.savefig(plot_file_path)
        plt.close()
        print(f"Plot saved: {plot_file_path}")
