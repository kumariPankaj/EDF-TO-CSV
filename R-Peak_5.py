import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import neurokit2 as nk

# Define the paths
filePath = r"C:\Users\Shree\Desktop\Projects\2023-hexoskin-study-data\synchronizing_Data_2"
output_Path = r"C:\Users\Shree\Desktop\Projects\2023-hexoskin-study-data\R-Peak_data_5"
plot_Path = r'C:\Users\Shree\Desktop\Projects\2023-hexoskin-study-data\R_peak_plots_5'

# Get the list of files
fileNames = [f for f in os.listdir(filePath)]
fileList = fileNames[:150]  # Limit to the first 150 files

# Ensure output directories exist
os.makedirs(output_Path, exist_ok=True)
os.makedirs(plot_Path, exist_ok=True)

# Define constants
sampling_rate = 256  # Adjust the sampling rate if needed
window_size = 10 * sampling_rate  # 10-second window size

# Process each file
for fileName in fileList:
    print(f"Checking file: {fileName}")
    
    # Skip files that don't contain ECG data or are classification files
    if not fileName.endswith('.csv') or 'Window ID' in fileName or 'Total Activity' in fileName or 'Activity Class' in fileName:
        print(f"Skipping {fileName}")
        continue

    try:
        print(f"Processing {fileName}")
        # Load the cleaned CSV file
        ecg_data = pd.read_csv(rf"{filePath}\{fileName}")

        # Check the first few rows of the CSV file to find the correct column for ECG data
        print(f"Columns available in {fileName}: {ecg_data.columns}")
        
        # Extract the ECG signal (adjust column name if needed)
        if 'ECG' in ecg_data.columns:
           ecg_signal = pd.to_numeric(ecg_data['ECG'], errors='coerce').dropna()
        else:
            print(f"ECG signal column not found in {fileName}")
            continue  # Skip this file if the ECG column is not found

        # Detect R-peaks using NeuroKit2
        r_peaks = nk.ecg_findpeaks(ecg_signal, sampling_rate=sampling_rate)["ECG_R_Peaks"]

        # Create a timestamp for each R-peak based on the sampling rate and peak index
        timestamps = r_peaks / sampling_rate  # Convert indices to timestamps in seconds

        # Create a DataFrame for the results
        r_peak_data = pd.DataFrame({
            'R-Peak Index': r_peaks,
            'R-Peak Value': ecg_signal[r_peaks],  # Get the ECG value at each R-peak
            'Timestamp (s)': timestamps
        })

        # Merge the original ECG data with the R-peak information
        ecg_data['R-Peak Index'] = pd.Series([r_peaks[r_peaks.searchsorted(i)] + 2 if r_peaks.searchsorted(i) < len(r_peaks) else None for i in range(len(ecg_signal))])
        ecg_data['R-Peak Value'] = pd.Series([ecg_signal[i] if i in r_peaks else None for i in range(len(ecg_signal))])

        # Save the results to a new CSV file
        output_file_path = os.path.join(output_Path, fileName)
        ecg_data.to_csv(output_file_path, index=False)

        # Create a folder for the plots for this file
        file_plot_path = os.path.join(plot_Path, os.path.splitext(fileName)[0])
        os.makedirs(file_plot_path, exist_ok=True)

        # Plot each 10-second segment
        num_segments = len(ecg_signal) // window_size
        for i in range(num_segments):
            start = i * window_size
            end = start + window_size
            segment = ecg_signal[start:end]
            peaks_in_segment = [peak for peak in r_peaks if start <= peak < end]

            # Plot the segment
            plt.figure(figsize=(10, 6))
            plt.plot(range(start, end), segment, label="ECG Signal", color="blue")
            plt.scatter(peaks_in_segment, ecg_signal[peaks_in_segment], color="red", label="R-Peaks")
            plt.title(f"ECG Signal Segment {i + 1} (File: {fileName})")
            plt.xlabel("Sample Index")
            plt.ylabel("Amplitude")
            plt.legend()
            plt.grid()

            # Save the plot
            plot_file_path = os.path.join(file_plot_path, f"segment_{i + 1}.png")
            plt.savefig(plot_file_path)
            plt.close()

        # Handle the last segment if it's smaller than window_size
        if len(ecg_signal) % window_size != 0:
            start = num_segments * window_size
            segment = ecg_signal[start:]
            peaks_in_segment = [peak for peak in r_peaks if peak >= start]

            # Plot the remaining segment
            plt.figure(figsize=(10, 6))
            plt.plot(range(start, start + len(segment)), segment, label="ECG Signal", color="blue")
            plt.scatter(peaks_in_segment, ecg_signal[peaks_in_segment], color="red", label="R-Peaks")
            plt.title(f"ECG Signal Remaining Segment (File: {fileName})")
            plt.xlabel("Sample Index")
            plt.ylabel("Amplitude")
            plt.legend()
            plt.grid()

            # Save the plot
            plot_file_path = os.path.join(file_plot_path, "remaining_segment.png")
            plt.savefig(plot_file_path)
            plt.close()

        print(f"Processed and saved: {fileName}")

    except Exception as e:
        print(f"Error processing {fileName}: {e}")
