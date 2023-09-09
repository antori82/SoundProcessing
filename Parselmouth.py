import parselmouth
import numpy as np
import glob
import re
import pandas as pd

regex = r"\\(\w*)\\"

path = "Sounds" # Where are the files?
files = glob.glob(path + '/**/*.wav', recursive= True) # List all the wav files in the subdirectories

featuresList = []

for file in files:
    matches = re.finditer(regex, file, re.MULTILINE) # Use a regex to extract the class

    for matchNum, match in enumerate(matches, start=0):
        targetClass = match.group()[1:-1]

        snd = parselmouth.Sound(file) # Read the sound file
        dur = snd.get_total_duration() # Extract the duration
        intensity = snd.to_intensity(minimum_pitch=80) # Get the intensity profile
        pitch = snd.to_pitch(time_step=0.01) # Get the pitch profile
        intensityArray = []
        for k, value in enumerate(intensity.values[0]):
            intensityArray.append((np.floor((intensity.t1 + k * intensity.time_step) * 1000), value)) # Convert to milliseconds

        intensityArray = np.asarray(intensityArray, dtype=np.float64)
        mIntensity = parselmouth.praat.call(intensity, "Get mean", 0, 0, 'energy') # Get mean intensity

        pitchArray = []
        for k, value in enumerate(pitch.selected_array):
            pitchArray.append((np.floor((pitch.t1 + k * pitch.time_step) * 1000), value[0])) # Convert to milliseconds

        pitchArray = np.asarray(pitchArray, dtype=np.float64)
        mpitch = parselmouth.praat.call(pitch, "Get mean", 0, 0, 'Hertz') # Get mean pitch
        mpitch = mpitch if not np.isnan(mpitch) else 0 # Use 0 to represent unvoiced instead of nan

        featuresList.append((mIntensity, mpitch, targetClass)) # create data row

pd.DataFrame(featuresList, columns= ['Mean Intensity', 'Mean Pitch', 'Target Class']).to_csv('parselmouthFeatures.csv', index=False) # create a csv file