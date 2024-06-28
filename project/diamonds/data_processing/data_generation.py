from pathlib import Path

import numpy as np
import pandas as pd


def save_split_csv(dirpath: Path, filename: Path, chunk_size: int = 5000, random_state: int=42):
    df = pd.read_csv(dirpath.path/filename)
    df = df.sample(frac=1, random_state=random_state).reset_index(drop=True)

    num_chunks = int(np.ceil(len(df) / chunk_size))
    for i in range(num_chunks):
        chunk = df[i * chunk_size:(i + 1) * chunk_size]
        chunk.to_csv(dirpath.path / f"diamonds_chunk_{i}.csv", index=False)
