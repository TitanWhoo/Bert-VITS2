import os
import argparse
import librosa
import glob
from multiprocessing import Pool, cpu_count

import soundfile
from tqdm import tqdm

from config import config


def process(item):
    file_path, args = item  # Unpack the tuple
    if os.path.exists(file_path) and file_path.lower().endswith(".wav"):
        wav, sr = librosa.load(file_path, sr=args.sr)
        soundfile.write(file_path, wav, sr)  # Write back to the original location


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sr",
        type=int,
        default=config.resample_config.sampling_rate,
        help="sampling rate",
    )
    parser.add_argument(
        "--in_dir",
        type=str,
        default=config.resample_config.in_dir,
        help="path to source dir",
    )
    parser.add_argument(
        "--processes",
        type=int,
        default=0,
        help="cpu_processes",
    )
    args, _ = parser.parse_known_args()

    if args.processes == 0:
        processes = cpu_count() - 2 if cpu_count() > 4 else 1
    else:
        processes = args.processes
    pool = Pool(processes=processes)

    # Use glob to find all .wav files
    wav_files = glob.glob(os.path.join(args.in_dir, '**', '*.wav'), recursive=True)

    tasks = [(file_path, args) for file_path in wav_files]

    for _ in tqdm(pool.imap_unordered(process, tasks), total=len(tasks)):
        pass

    pool.close()
    pool.join()

    print("音频重采样完毕!")
