"""
Core analysis functions for LEMO Vocabulate
"""
from pathlib import Path
from typing import Optional, Union
import pandas as pd
from tqdm import tqdm

from .tokenizer import TwitterAwareTokenizer, tokenize_whitespace
from .stopwords import StopWordRemover, load_stopwords_from_file
from .dictionary import DictionaryData, LoadDictionary, match_dictionary

def run_vocabulate_analysis(
    dict_file: str = None,
    input_data=None,
    text_column: str = None,
    stopwords_text: str = None,
    stopwords_file: str = None,
    raw_counts: bool = True,
    encoding: str = "utf-8",
    csv_delimiter: str = ",",
    csv_quote: str = '"',
    output_csv: str = None,
    whitespace_method: str = 'new'  # <- new optional parameter
) -> pd.DataFrame:
    """Analyze text(s) using a dictionary file, with input validation and error handling."""

    if not dict_file:
        raise ValueError("Error: dict_file must be specified.")
    dict_path = Path(dict_file)
    if not dict_path.is_file():
        raise FileNotFoundError(f"Dictionary file not found: {dict_file}.")

    if not stopwords_file and not stopwords_text:
        raise ValueError("Error: Either stopwords_file or stopwords_text must be provided.")

    tokenizer = TwitterAwareTokenizer()
    stop_remover = StopWordRemover()

    if stopwords_file:
        stopwords_text = load_stopwords_from_file(stopwords_file, encoding)
    if stopwords_text:
        stop_remover.build_stoplist(stopwords_text)

    dict_data = DictionaryData()
    loader = LoadDictionary()
    try:
        dict_data = loader.load_dictionary_file(dict_data, dict_file, encoding, csv_delimiter, csv_quote)
    except Exception as e:
        raise RuntimeError(f"Failed to load dictionary: {e}")

    dict_data.raw_word_counts = raw_counts

    # ---------- Determine Input ----------
    texts_to_process = []
    filenames = []

    if isinstance(input_data, pd.DataFrame):
        if text_column is None:
            raise ValueError("text_column must be specified for DataFrame input.")
        if text_column not in input_data.columns:
            raise ValueError(f"Column '{text_column}' not found in input_data DataFrame.")
        texts_to_process = input_data[text_column].fillna("").astype(str).tolist()
        filenames = input_data.index.astype(str).tolist()

    elif isinstance(input_data, (str, Path)):
        path = Path(input_data)
        if path.is_file():
            texts_to_process = [path.read_text(encoding=encoding)]
            filenames = [path.name]
        elif path.is_dir():
            files = list(path.glob("*.txt"))
            if not files:
                raise ValueError(f"No .txt files found in directory: {input_data}")
            for f in files:
                texts_to_process.append(f.read_text(encoding=encoding))
                filenames.append(f.name)
        else:
            raise ValueError(f"Invalid input path: {input_data}")
    else:
        raise ValueError("input_data must be a DataFrame, file path, or folder path.")

    if not texts_to_process:
        raise ValueError("No texts to process.")

    # ------------- Process Texts -------------
    results = []
    print(f"🔍 Analyzing {len(texts_to_process)} text(s)...")

    for idx, text in enumerate(tqdm(texts_to_process, desc="Processing texts", unit="text")):
        wc = len(tokenize_whitespace(text, method=whitespace_method))
        words_raw = tokenizer.tokenize(text)
        tc_raw = len(words_raw)
        ttr_raw = (len(set(words_raw)) / tc_raw * 100) if tc_raw else 0

        words_clean = stop_remover.clear_stopwords(words_raw)
        words_clean = [w for w in words_clean if w]
        tc_clean = len(words_clean)
        ttr_clean = (len(set(words_clean)) / tc_clean * 100) if tc_clean else 0

        concept_counts, num_matched_tokens, captured_text, nonmatched = match_dictionary(dict_data, words_clean)
        tc_nondict = len(nonmatched)
        ttr_nondict = (len(set(nonmatched)) / tc_nondict * 100) if tc_nondict else 0
        dict_percent = (num_matched_tokens / tc_raw * 100) if tc_raw else 0

        # Category-level counts
        category_results = {cat: [0, 0] for cat in dict_data.cat_names}  # [unique_count, total_count]
        for concept, count in concept_counts.items():
            if concept in dict_data.concept_map:
                for category in dict_data.concept_map[concept]:
                    category_results[category][0] += 1
                    category_results[category][1] += count

        row = {
            "Filename": filenames[idx],
            "text": text,
            "WC": wc,
            "TC_Raw": tc_raw,
            "TTR_Raw": round(ttr_raw, 5),
            "TC_Clean": tc_clean,
            "TTR_Clean": round(ttr_clean, 5),
            "TC_NonDict": tc_nondict,
            "TTR_NonDict": round(ttr_nondict, 5),
            "DictPercent": round(dict_percent, 5),
            "CapturedText": captured_text
        }

        for cat in dict_data.cat_names:
            unique_count, total_count = category_results[cat]
            row[f"{cat}_CWR"] = round(unique_count / wc * 100, 5) if wc else 0
            row[f"{cat}_CCR"] = round(unique_count / total_count * 100, 5) if total_count else 0
            if raw_counts:
                row[f"{cat}_Count"] = total_count
                row[f"{cat}_Unique"] = unique_count

        results.append(row)

    df_results = pd.DataFrame(results)

    if output_csv:
        df_results.to_csv(output_csv, index=False, sep=csv_delimiter, quotechar=csv_quote)
        print(f"✅ Results saved to {output_csv}")

    print("✅ Analysis complete.")
    return df_results
