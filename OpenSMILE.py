import opensmile
import pandas as pd
import glob
from multiprocessing import Pool, cpu_count
import time
import re

regex = r"\\(\w*)\\"

smile = opensmile.Smile(feature_set=opensmile.FeatureSet.ComParE_2016, feature_level=opensmile.FeatureLevel.Functionals,) # Select the features set
path = "Sounds"
data = []
files = glob.glob(path + '/**/*.wav', recursive= True) # Get all the wav files in the subdirectories

def process(file): # Extract the features with OpenSMILE
    try:
        df = smile.process_file(file)
        df["targetClass"] = re.findall(regex, file, re.MULTILINE)[0]
        return df
    except Exception as inst:
        print(type(inst))
        return []

if __name__ == "__main__":

    print("Starting multiprocessing\n")

    results = []
    tic = time.perf_counter() # Start timer
    with Pool(cpu_count() * 2 - 1) as pool: # Apply the function to all the files
        for result in pool.map(process, files):
            if len(result) > 0:
                results.append(result)
    toc = time.perf_counter() # Stop timer
    print(f"Finished in {toc - tic:0.4f} seconds") # Write time spent

    pd.concat(results, axis=0, ignore_index=False).to_csv('features.csv', index=False) # Write csv file
