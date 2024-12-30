import os
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt

# Input folder containing ECG and synchronized accelerometer data
input_folder = r"C:\Users\Shree\Desktop\Projects\2023-hexoskin-study-data\synchronizing_Data_2"

# Output folder to save segmented and filtered data and plots
output_folder = r"C:\Users\Shree\Desktop\Projects\2023-hexoskin-study-data\cleaning_Data_3"
os.makedirs(output_folder, exist_ok=True)  # Create the folder if it doesn't exist

# Function to load data from a file (modify if the format is different)
def load_data(file_path):
    # Use pandas to load the data, skipping the header and selecting only numeric columns
    data = pd.read_csv(file_path)  # Read the CSV file
    # Select only numeric columns (ignores headers and any non-numeric data like 'Timestamp')
    numeric_data = data.select_dtypes(include=[np.number]).values
    return numeric_data

# Butterworth bandpass filter design
def bandpass_filter(signal, lowcut, highcut, fs=250):
    # Calculate the Nyquist frequency
    nyquist = 0.5 * fs  # Nyquist frequency is half of the sampling rate

    # Normalize the frequencies
    low = lowcut / nyquist
    high = highcut / nyquist

    # Ensure low < high and that frequencies are in the range [0, 1]
    if low <= 0 or high >= 1 or low >= high:
        raise ValueError("Filter frequencies must be between 0 and 1 after normalization, and lowcut must be less than highcut.")

    # Design the filter
    b, a = butter(1, [low, high], btype='band')
    filtered_signal = filtfilt(b, a, signal)
    return filtered_signal

# Parameters for filtering
lowcut = 0.5  # Lower cutoff frequency in Hz
highcut = 45  # Upper cutoff frequency in Hz

# Process files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".txt") or filename.endswith(".csv"):  # Adjust extensions as needed
        file_path = os.path.join(input_folder, filename)
        print(f"Processing file: {filename}")

        try:
            # Load the data (assuming ECG is the first column, accelerometer follows)
            data = load_data(file_path)
            ecg_signal = data[:, 0]  # ECG data
            accelerometer_data = data[:, 1:]  # Accelerometer data (multi-column)

            # Apply the bandpass filter to the ECG signal
            filtered_ecg = bandpass_filter(ecg_signal, lowcut, highcut)

            # Combine ECG and accelerometer data for the entire dataset
            combined_data = np.column_stack((filtered_ecg, accelerometer_data))

            # Save the entire cleaned data into one CSV file
            output_file = os.path.join(output_folder, f"cleaned_{filename}")
            np.savetxt(output_file, combined_data, delimiter=',')
            print(f"Data saved to: {output_file}")

            # Plot cleaned ECG and accelerometer data for inspection
            time = np.linspace(0, len(filtered_ecg) / 250, len(filtered_ecg))  # Assuming fs = 250 Hz

            # Plot ECG and accelerometer data
            plt.figure(figsize=(12, 8))

            # Plot ECG data
            plt.subplot(2, 1, 1)
            plt.plot(time, filtered_ecg, label="Cleaned ECG Signal", color="blue")
            plt.title(f"Cleaned ECG Signal - {filename}")
            plt.xlabel("Time (s)")
            plt.ylabel("Amplitude")
            plt.legend()
            plt.grid()

            # Plot accelerometer data
            plt.subplot(2, 1, 2)
            for i in range(accelerometer_data.shape[1]):
                plt.plot(time, accelerometer_data[:, i], label=f"Accelerometer Axis {i + 1}")
            plt.title(f"Accelerometer Data - {filename}")
            plt.xlabel("Time (s)")
            plt.ylabel("Amplitude")
            plt.legend()
            plt.grid()

            plt.tight_layout()

            # Save the plot as a PNG image in the output folder
            plot_file = os.path.join(output_folder, f"plot_{filename.split('.')[0]}.png")
            plt.savefig(plot_file)
            print(f"Plot saved to: {plot_file}")

            # Close the plot to avoid overlapping with the next one
            plt.close()

        except Exception as e:
            print(f"Error processing file {filename}: {e}")
