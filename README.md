# Hexoskin Study Data

Data recorded during the study on June 8th with 48 participants wearing a
Hexoskin Proshirts and carrying a Samsung Galaxy A52s 5G.

## Hexoskin Data

The Hexoskin data is saved in EDF files and named after the following scheme:

- If there was only one record on the Hexoskin device, the file is named like
  the device, e.g. `HX45123.edf`
- If there were multiple records on the Hexoskin device, the files are starting
  with the device name, but have an index, and the data and time of recording
  appended, e.g. `HX45123-1_110134_4503.edf`. In general, the following format
  is used: `HX45123-{index}_{HH}{MM}{ss}_{MM}{ss}.edf`. If the time was greater
  than 99 minutes and 59 seconds (1 hour and 39 minutes and 59 seconds), the
  time is written also in `{HH}{MM}{ss}` format.

Exceptions:
- Device `HX45249` is contained twice. This must be due to a transcription
  error. The real `HX45249` device is renamed to `HX45249A`.
- The device `HX4516` does not exist. It must be either `HX45136`, or `HX45163`.

# File converted into EDF to CSV 
  The data has contain 'hexoskin' folder and converted csv file has in the 'overall' folder. 

# Synchornizing data
  All csv data has synchornized and presenting the plot graph of ECG(256Hz) and Accelerometer(64Hz) data of all each converted csv file.

# Cleaning data
  Clean all the Synchornizing data with the frequencies of 0.5 Hz and 45 Hz, Data is divided into 10-second windows

# Activity Classification 
  classified each file and every file will present the magnitude(high,medium,low - intensity) with  window sencod.

# R-Peak Detection 
  Using the R-Peak for each 10-second window and Plot of ECG signals with marked R-peaks.

# Signal Quality Using Fuzzy SQI  
  