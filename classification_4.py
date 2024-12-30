import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from skimage.filters import threshold_otsu
from scipy.signal import butter, filtfilt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from scipy.stats import pearsonr

# Define the paths
data_path = r"C:\Users\Shree\Desktop\Projects\2023-hexoskin-study-data\cleaning_Data_3"
output_folder = r"C:\Users\Shree\Desktop\Projects\2023-hexoskin-study-data\classification_data_4"
os.makedirs(output_folder, exist_ok=True)

# List all CSV files in the data folder
files = [f for f in os.listdir(data_path) if f.endswith('.csv')]

# Set the new sampling rate (64 Hz)
sampling_rate = 256 // 4  # Accelerometer sampling at 64 Hz

# Define the window size for 10 seconds (64 Hz -> 64 samples/sec * 10 sec = 640 samples)
window_size = 10 * sampling_rate  # 640 samples

# High-pass filter to remove baseline drift
def high_pass_filter(signal, cutoff, fs, order=2):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    filtered_signal = filtfilt(b, a, signal)
    return filtered_signal

# Bandpass filter to remove high-frequency noise
def bandpass_filter(signal, lowcut, highcut, fs, order=1):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    filtered_signal = filtfilt(b, a, signal)
    return filtered_signal

for file_name in files:
    data_file = os.path.join(data_path, file_name)

    # Load the data
    data = pd.read_csv(data_file, header=None)
    data.columns = ['x', 'y', 'z']  # Assign column names
    data['magnitude'] = np.sqrt(data['x']**2 + data['y']**2 + data['z']**2)  # Calculate magnitude

    # Check if there are enough data points for the window size (640 samples for 10 seconds)
    if len(data) < window_size:
        print(f"Skipping {file_name}: not enough data points (less than {window_size})")
        continue  # Skip this file if it doesn't have enough data

    # Calculate the number of windows (total samples / window size)
    num_windows = len(data) // window_size

    # Compute total activity per window
    total_activity_per_window = [
        np.sum(data['magnitude'][i * window_size:(i + 1) * window_size])
        for i in range(num_windows)
    ]

    # If no valid windows, skip this file
    if not total_activity_per_window:
        print(f"Skipping {file_name}: no valid windows")
        continue

    # Apply Otsu's method to find the optimal threshold
    threshold = threshold_otsu(np.array(total_activity_per_window))

    # Classify activity based on the threshold
    def classify_activity(activity_value):
        if activity_value < threshold:
            return 'Low'
        else:
            return 'High'

    activity_classes = [classify_activity(activity) for activity in total_activity_per_window]

    # Save results to CSV
    output_data = pd.DataFrame({
        'Window ID': [f"Window-{i+1}" for i in range(num_windows)],
        'Total Activity': total_activity_per_window,
        'Activity Class': activity_classes
    })
    output_csv_file = os.path.join(output_folder, f'{file_name}_activity_classification.csv')
    output_data.to_csv(output_csv_file, index=False)

    # Plot histogram
    plt.figure(figsize=(8, 6))

    # Create the histogram
    n, bins, patches = plt.hist(
        total_activity_per_window,
        bins=30,
        edgecolor='black',
        alpha=0.7,
    )

    # Assign color based on the value of each bin relative to the threshold
    for i in range(len(patches)):
        # Get the total activity for the current bin
        bin_value = (bins[i] + bins[i+1]) / 2  # Take the midpoint of the bin
        color = 'green' if classify_activity(bin_value) == 'Low' else 'red'
        patches[i].set_facecolor(color)

    plt.title(f'Histogram of Summed Magnitude Values ({file_name})')
    plt.xlabel('Summed Magnitude')
    plt.ylabel('Frequency')
    plt.grid(True)

    # Save histogram as an image
    histogram_file = os.path.join(output_folder, f'{file_name}_histogram.png')
    plt.savefig(histogram_file)
    plt.close()

    print(f"Processed {file_name}: CSV saved to {output_csv_file}, histogram saved to {histogram_file}")
