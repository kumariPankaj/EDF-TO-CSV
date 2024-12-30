import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from scipy import stats
import glob

# Create the directory to save results
output_dir = "Results_Analysis"
os.makedirs(output_dir, exist_ok=True)

# Path to the folder containing CSV files
data_folder = 'C:/Users/Shree/Desktop/Projects/2023-hexoskin-study-data/Fuzzy_SQI_Results_6/'

# Get list of all CSV files in the folder
csv_files = glob.glob(os.path.join(data_folder, '*.csv'))

# Initialize an empty DataFrame to combine all CSV files
df = pd.DataFrame()

# Read and combine all CSV files
for file in csv_files:
    temp_df = pd.read_csv(file)
    df = pd.concat([df, temp_df], ignore_index=True)

# 1. Comparison Between Participants
# Aggregated Metrics Calculation
df['Excellent'] = (df['Signal_Quality'] == 'Excellent')
excellent_percentage = df.groupby('Participant')['Excellent'].mean() * 100
mean_fuzzy_sqi = df.groupby('Participant')['Fuzzy_SQI'].mean()
median_fuzzy_sqi = df.groupby('Participant')['Fuzzy_SQI'].median()

# Difference Analysis (using Kruskal-Wallis test)
participants = df['Participant'].unique()
kruskal_results = stats.kruskal(*[df[df['Participant'] == participant]['Fuzzy_SQI'] for participant in participants])

# Visualization: Boxplot and Histogram
# Boxplot for signal quality by participant
plt.figure(figsize=(10, 6))
sns.boxplot(x='Participant', y='Fuzzy_SQI', data=df)
plt.title('Signal Quality Distribution by Participant')
plt.xlabel('Participant')
plt.ylabel('Fuzzy SQI')
boxplot_participant_path = os.path.join(output_dir, "boxplot_signal_quality_by_participant.png")
plt.savefig(boxplot_participant_path)
plt.close()

# Histogram for percentage of "Excellent" quality
plt.figure(figsize=(10, 6))
sns.histplot(excellent_percentage, bins=10, kde=True)
plt.title('Percentage of Excellent Time Windows by Participant')
plt.xlabel('Percentage of Excellent Time Windows')
plt.ylabel('Frequency')
histogram_participant_path = os.path.join(output_dir, "histogram_excellent_quality_by_participant.png")
plt.savefig(histogram_participant_path)
plt.close()

# 2. Comparison Between Activity Classes
# Data Aggregation
activity_classes = df['Activity_Class'].unique()
activity_class_mean = df.groupby('Activity_Class')['Fuzzy_SQI'].mean()
activity_class_excellent_percentage = df[df['Signal_Quality'] == 'Excellent'].groupby('Activity_Class').size() / df.groupby('Activity_Class').size() * 100

# Statistical Analysis (Mann-Whitney U test between low and high activity classes)
low_activity_data = df[df['Activity_Class'] == 'Low']['Fuzzy_SQI']
high_activity_data = df[df['Activity_Class'] == 'High']['Fuzzy_SQI']
mann_whitney_result = stats.mannwhitneyu(low_activity_data, high_activity_data)

# Visualization: Boxplot and Bar Chart
# Boxplot for signal quality by activity class
plt.figure(figsize=(10, 6))
sns.boxplot(x='Activity_Class', y='Fuzzy_SQI', data=df)
plt.title('Signal Quality Distribution by Activity Class')
plt.xlabel('Activity Class')
plt.ylabel('Fuzzy SQI')
boxplot_activity_path = os.path.join(output_dir, "boxplot_signal_quality_by_activity.png")
plt.savefig(boxplot_activity_path)
plt.close()

# Bar Chart for percentage of "Excellent" quality per activity class
plt.figure(figsize=(10, 6))
activity_class_excellent_percentage.plot(kind='bar', color='purple')
plt.title('Percentage of Excellent Time Windows by Activity Class')
plt.xlabel('Activity Class')
plt.ylabel('Percentage')
bar_chart_activity_path = os.path.join(output_dir, "bar_chart_excellent_quality_by_activity.png")
plt.savefig(bar_chart_activity_path)
plt.close()

# 3. Temporal Analysis
# Time-Based Aggregation: Add Timestamp if needed
df['Timestamp'] = pd.to_datetime(df['Window_Index'], unit='s')  # Assuming Window_Index is in seconds

# Temporal Trend Calculation for each participant
plt.figure(figsize=(10, 6))
for participant in df['Participant'].unique():
    participant_data = df[df['Participant'] == participant]
    plt.plot(participant_data['Timestamp'], participant_data['Fuzzy_SQI'], label=f'Participant {participant}')
plt.title('Temporal Trend of Signal Quality per Participant')
plt.xlabel('Timestamp')
plt.ylabel('Fuzzy SQI')
line_plot_path = os.path.join(output_dir, "temporal_trend_signal_quality.png")
plt.savefig(line_plot_path)
plt.close()

# 4. Detailed Visualization
# 1. Histograms
plt.figure(figsize=(10, 6))
sns.histplot(df['Fuzzy_SQI'], bins=30, kde=True)
plt.title('Distribution of Fuzzy SQI Values for All Participants')
plt.xlabel('Fuzzy SQI')
plt.ylabel('Frequency')
histogram_path = os.path.join(output_dir, "fuzzy_sqi_histogram_all.png")
plt.savefig(histogram_path)
plt.close()

# For specific activity classes
plt.figure(figsize=(10, 6))
sns.histplot(df[df['Activity_Class'] == 'Low']['Fuzzy_SQI'], bins=30, kde=True, color='blue', label='Low Activity')
sns.histplot(df[df['Activity_Class'] == 'Medium']['Fuzzy_SQI'], bins=30, kde=True, color='orange', label='Medium Activity')
sns.histplot(df[df['Activity_Class'] == 'High']['Fuzzy_SQI'], bins=30, kde=True, color='green', label='High Activity')
plt.title('Distribution of Fuzzy SQI Values by Activity Class')
plt.xlabel('Fuzzy SQI')
plt.ylabel('Frequency')
plt.legend()
histogram_activity_path = os.path.join(output_dir, "fuzzy_sqi_histogram_by_activity.png")
plt.savefig(histogram_activity_path)
plt.close()

# 2. Line Plots
plt.figure(figsize=(10, 6))
for participant in df['Participant'].unique():
    participant_data = df[df['Participant'] == participant]
    plt.plot(participant_data['Timestamp'], participant_data['Fuzzy_SQI'], label=f'Participant {participant}')
plt.title('Temporal Trend of Signal Quality per Participant')
plt.xlabel('Timestamp')
plt.ylabel('Fuzzy SQI')
line_plot_path = os.path.join(output_dir, "temporal_trend_signal_quality.png")
plt.savefig(line_plot_path)
plt.close()

# 3. Boxplots: Compare signal quality between participants or activity classes
plt.figure(figsize=(10, 6))
sns.boxplot(x='Participant', y='Fuzzy_SQI', data=df)
plt.title('Signal Quality Distribution by Participant')
plt.xlabel('Participant')
plt.ylabel('Fuzzy SQI')
boxplot_participant_path = os.path.join(output_dir, "boxplot_signal_quality_by_participant.png")
plt.savefig(boxplot_participant_path)
plt.close()

plt.figure(figsize=(10, 6))
sns.boxplot(x='Activity_Class', y='Fuzzy_SQI', data=df)
plt.title('Signal Quality Distribution by Activity Class')
plt.xlabel('Activity Class')
plt.ylabel('Fuzzy SQI')
boxplot_activity_path = os.path.join(output_dir, "boxplot_signal_quality_by_activity.png")
plt.savefig(boxplot_activity_path)
plt.close()

# 4. Bar Charts: Compare average signal quality or percentage of "Excellent" time windows per activity class
excellent_percentage = df[df['Signal_Quality'] == 'Excellent'].groupby('Activity_Class').size() / df.groupby('Activity_Class').size() * 100
plt.figure(figsize=(10, 6))
excellent_percentage.plot(kind='bar', color='purple')
plt.title('Percentage of Excellent Time Windows by Activity Class')
plt.xlabel('Activity Class')
plt.ylabel('Percentage')
bar_chart_activity_path = os.path.join(output_dir, "bar_chart_excellent_quality_by_activity.png")
plt.savefig(bar_chart_activity_path)
plt.close()

# Average signal quality by activity class
avg_signal_quality = df.groupby('Activity_Class')['Fuzzy_SQI'].mean()
plt.figure(figsize=(10, 6))
avg_signal_quality.plot(kind='bar', color='cyan')
plt.title('Average Signal Quality by Activity Class')
plt.xlabel('Activity Class')
plt.ylabel('Average Fuzzy SQI')
bar_chart_avg_quality_path = os.path.join(output_dir, "bar_chart_avg_signal_quality_by_activity.png")
plt.savefig(bar_chart_avg_quality_path)
plt.close()

