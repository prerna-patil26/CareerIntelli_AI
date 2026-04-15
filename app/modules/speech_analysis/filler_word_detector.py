import pandas as pd
import os


class FillerWordDetector:
    def __init__(self):
        try:
            # Project root
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

            # Dataset path
            dataset_path = os.path.join(base_dir, "datasets", "filler_words_dataset.csv")

            print("FINAL PATH:", dataset_path)

            df = pd.read_csv(dataset_path)

            self.filler_words = df['filler_word'].dropna().str.lower().tolist()

        except Exception as e:
            print("Error loading filler words dataset:", e)

            self.filler_words = ["um", "uh", "like", "you know"]
            