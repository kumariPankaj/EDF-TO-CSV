import numpy as np
import pandas as pd
import skfuzzy as fuzz
import os
import matplotlib.pyplot as plt

# Define feature calculation functions
def amplitude_stability(r_peaks):
    return np.std(r_peaks)

def rr_interval_variability(r_peaks):
    rr_intervals = np.diff(r_peaks)
    return np.std(rr_intervals)

def snr(signal, noise):
    signal_power = np.sum(signal ** 2)
    noise_power = np.sum(noise ** 2)
    return 10 * np.log10(signal_power / noise_power)

# Heuristic Fusion to Calculate Quality Value with Weights
def quality_value(amplitude_stability, rr_variability, snr_value, w1=0.4, w2=0.3, w3=0.3):
    return w1 * amplitude_stability + w2 * rr_variability + w3 * snr_value

# Fuzzy Logic Classification
def fuzzy_classification(quality_val):
    quality = np.arange(0, 1.1, 0.1)

    excellent = fuzz.trimf(quality, [0.8, 1, 1])
    acceptable = fuzz.trimf(quality, [0.4, 0.6, 0.8])
    unacceptable = fuzz.trimf(quality, [0, 0, 0.4])

    quality_val = np.clip(quality_val, 0, 1)

    excellent_membership = fuzz.interp_membership(quality, excellent, quality_val)
    acceptable_membership = fuzz.interp_membership(quality, acceptable, quality_val)
    unacceptable_membership = fuzz.interp_membership(quality, unacceptable, quality_val)

    if excellent_membership > acceptable_membership and excellent_membership > unacceptable_membership:
        return 'Excellent'
    elif acceptable_membership > excellent_membership and acceptable_membership > unacceptable_membership:
        return 'Barely Acceptable'
    else:
        return 'Unacceptable'

# Segmented Signal Processing
def segment_signal(signal, window_size=10, sample_rate=1000):
    windows = []
    step = window_size * sample_rate
    for i in range(0, len(signal), step):
        window = signal[i:i + step]
        windows.append(window)
    return windows

# Create the folder to save results
folder_path = r"C:\Users\Shree\Desktop\Projects\2023-hexoskin-study-data\Fuzzy_SQI_Results_6"
os.makedirs(folder_path, exist_ok=True)

# Read ECG data, R-Peaks, and Activity Classifications
r_peak_data_path = r"C:\Users\Shree\Desktop\Projects\2023-hexoskin-study-data\R-Peak_data_5"
classification_data_path = r"C:\Users\Shree\Desktop\Projects\2023-hexoskin-study-data\classification_data_4"

r_peak_files = os.listdir(r_peak_data_path)
classification_files = os.listdir(classification_data_path)

# Process each participant's data
for r_file, c_file in zip(r_peak_files, classification_files):
    r_peak_file_path = os.path.join(r_peak_data_path, r_file)
    classification_file_path = os.path.join(classification_data_path, c_file)

    # Create a subfolder for each participant to store results
    participant_folder = os.path.join(folder_path, r_file.split('.')[0])  # Folder for each participant
    os.makedirs(participant_folder, exist_ok=True)

    # Read the R-peak and classification data
    try:
        r_peak_df = pd.read_csv(r_peak_file_path, encoding='ISO-8859-1')
    except Exception as e:
        print(f"Error reading R-peak file {r_file}: {e}")
        continue

    try:
        classification_df = pd.read_csv(classification_file_path, encoding='ISO-8859-1')
    except Exception as e:
        print(f"Error reading Classification file {c_file}: {e}")
        continue

    if 'R-Peak Index' not in r_peak_df.columns:
        print(f"The R-peak file is missing the 'R-Peak Index' column. Available columns are: {', '.join(r_peak_df.columns)}")
        continue

    if 'Activity Class' not in classification_df.columns:
        print(f"The classification file is missing the 'Activity Class' column. Available columns are: {', '.join(classification_df.columns)}")
        continue

    r_peaks = r_peak_df['R-Peak Index'].dropna().values
    activity_classes = classification_df['Activity Class'].tolist()

    # Assuming ECG signal is also present in R-peak file
    try:
        ecg_signal = r_peak_df['ECG'].values
    except KeyError:
        print(f"The R-peak file {r_file} does not contain ECG signal data.")
        continue

    # Segment the signal
    windows = segment_signal(ecg_signal)

    # Initialize a list to store results for this participant
    sqi_results = []

    # For each window (segment), calculate Fuzzy SQI, classify the signal quality, and compute Quality Value
    for idx, window in enumerate(windows):
        if idx >= len(activity_classes):
            break

        activity_class = activity_classes[idx]

        # Calculate features for the current window
        amp_stability = amplitude_stability(r_peaks)
        rr_variability = rr_interval_variability(r_peaks)
        snr_value = snr(window, ecg_signal)
        quality_val = quality_value(amp_stability, rr_variability, snr_value)

        # Classify signal quality using fuzzy logic
        classification = fuzzy_classification(quality_val)

        # Store results for the segment (window)
        sqi_results.append({
            'Participant': r_file.split('.')[0],
            'Window_Index': idx,
            'Activity_Class': activity_class,
            'Fuzzy_SQI': quality_val,
            'Signal_Quality': classification
        })

    # Remove segment result CSV files
    for file in os.listdir(participant_folder):
        if file.endswith('_results.csv'):
            os.remove(os.path.join(participant_folder, file))

    # Visualization for each participant
    # Histograms: Distribution of Fuzzy SQI across Activity Classes
    plt.figure()
    plt.hist([res['Fuzzy_SQI'] for res in sqi_results], bins=10, alpha=0.7, label=f'Fuzzy SQI Distribution ({r_file})')
    plt.xlabel('Fuzzy SQI')
    plt.ylabel('Frequency')
    plt.title(f'Fuzzy SQI Distribution for {r_file}')
    plt.savefig(os.path.join(participant_folder, f"{r_file}_fuzzy_sqi_histogram.png"))
    plt.close()

    # Boxplots: Signal Quality Comparison by Activity Class
    plt.figure()
    activity_classes_unique = list(set([res['Activity_Class'] for res in sqi_results]))
    plt.boxplot([
        [res['Fuzzy_SQI'] for res in sqi_results if res['Activity_Class'] == ac]
        for ac in activity_classes_unique
    ], labels=activity_classes_unique)
    plt.xlabel('Activity Class')
    plt.ylabel('Fuzzy SQI')
    plt.title(f'Signal Quality Comparison by Activity Class for {r_file}')
    plt.savefig(os.path.join(participant_folder, f"{r_file}_fuzzy_sqi_boxplot.png"))
    plt.close()

    # Line Plots: Temporal Trends of Fuzzy SQI
    plt.figure()
    plt.plot([res['Window_Index'] for res in sqi_results], [res['Fuzzy_SQI'] for res in sqi_results],
             label=f'Signal Quality Trend ({r_file})')
    plt.xlabel('Time Window')
    plt.ylabel('Fuzzy SQI')
    plt.title(f'Temporal Trends of Signal Quality for {r_file}')
    plt.savefig(os.path.join(participant_folder, f"{r_file}_signal_quality_trend.png"))
    plt.close()

    print(f"Results for {r_file} saved in: {participant_folder}")

# Display Summary
print(f"Summary of results saved in: {folder_path}")
