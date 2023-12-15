import os
import re

DATASETS_ROOT = '/content/datasets'
TRANSCRIPT_PATH = os.path.join(DATASETS_ROOT, 'transcript.txt')
# VCTK
VCTK_ROOT = os.path.join(DATASETS_ROOT, 'VCTK-Corpus')
VCTK_WAVS = os.path.join(VCTK_ROOT, 'wav48')
VCTK_TXT = os.path.join(VCTK_ROOT, 'txt')

# BAKER
BAKER_ROOT = os.path.join(DATASETS_ROOT, "BZNSYP")
BAKER_WAVS = os.path.join(BAKER_ROOT, "Wave")
BAKER_TXT = os.path.join(BAKER_ROOT, "ProsodyLabeling/000001-010000.txt")

# AISHELL-3
AISHELL_ROOT = os.path.join(DATASETS_ROOT, "data_aishell3")
AISHELL_TRAIN_PATH = os.path.join(AISHELL_ROOT, "train")
AISHELL_TEST_PATH = os.path.join(AISHELL_ROOT, "test")


def write_transcript(tf, wav_file_path, speaker, lang, txt):
    tf.write(f"{wav_file_path}|{speaker}|{lang}|{txt}\n")


def flush_vctk(tf):
    for _, dirs, _ in os.walk(VCTK_TXT):
        for spk_dir in dirs:
            wav_root_path = os.path.join(VCTK_WAVS, spk_dir)
            txt_root_path = os.path.join(VCTK_TXT, spk_dir)
            for txt_root, _, txt_files in os.walk(txt_root_path):
                for txt_file in txt_files:
                    with open(os.path.join(txt_root, txt_file), mode="r", encoding="utf-8") as f:
                        txt = f.read().strip()
                    wav_file = txt_file.replace(".txt", ".wav")
                    speaker = spk_dir
                    wav_file_path = os.path.join(wav_root_path, wav_file)
                    write_transcript(tf, wav_file_path, speaker, "EN", txt)
        break


def flush_baker(tf):
    pattern = re.compile("#\d+")
    speaker_name = "baker"
    with open(BAKER_TXT, "r", encoding="utf-8") as ttf:
        for line in ttf:
            # read line and skip next line
            wav_name, text = line.rstrip("\n").split("\t")
            text = pattern.sub("", text)
            wav_path = os.path.join(BAKER_WAVS, wav_name + ".wav")
            write_transcript(tf, wav_path, speaker_name, "ZH", text)
            _ = next(ttf)
    pass


def flush_aishell(tf):
    def flush(fo, path):
        content_path = os.path.join(path, "content.txt")
        with open(content_path) as f:
            for line in f:
                wav_filename, text = line.rstrip("\n").split("\t")
                spk_id = wav_filename[:7]
                wav_path = os.path.join(path, "wav", spk_id, wav_filename)
                temp = text.split(" ")
                text = "".join(temp[::2])
                write_transcript(fo, wav_path, spk_id, "ZH", text)

    flush(tf, AISHELL_TRAIN_PATH)
    flush(tf, AISHELL_TEST_PATH)
    pass


def main():
    with open(TRANSCRIPT_PATH, mode="w", encoding="utf-8") as f:
        flush_baker(f)
        flush_vctk(f)
        flush_aishell(f)


if __name__ == '__main__':
    main()