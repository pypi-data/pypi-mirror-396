# Vocabulate Python Edition

**Vocabulate** is a dictionary-based text analysis tool originally developed in C# for Windows.  

This Python package allows you to tokenize, clean, and analyze texts based on custom dictionaries across **any operating system** (Windows, macOS, Linux).

**DISCLAIMER:** All credit for formulating how to compute emotion vocabularies goes to the authors of Vocabulate [Vine et al. (2020)](https://www.nature.com/articles/s41467-020-18349-0). I do not take credit for this software. I simply reconfigured this formula to run in python instead of C#. 

```bib
@article{vine2020natural,
  title={Natural emotion vocabularies as windows on distress and well-being},
  author={Vine, Vera and Boyd, Ryan L. and Pennebaker, James W.},
  journal={Nature Communications},
  volume={11},
  number={1},
  pages={4525},
  year={2020},
  doi={10.1038/s41467-020-18349-0}
}
```

## Why This Package?

While the original Vocabulate software is powerful, this Python implementation offers several alternatives:

- **Cross-platform compatibility**: Works on Windows, macOS, and Linux (original is Windows-only)
- **Flexible input formats**: Analyze text from pandas DataFrames, CSV files, single text files, or folders of text files
- **Modern Python ecosystem**: Integrates seamlessly with pandas, Jupyter notebooks, and other data science tools. 

---

## Environment Setup

**Tip:** For the best experience, we recommend running this in a [**Jupyter Notebook**](https://code.visualstudio.com/docs/datascience/jupyter-notebooks) via VSCode where you can interactively explore your results.

### New to Python or VS Code?

If you're completely new to Python, don't worry! Here's a step-by-step guide:

#### Step 1: Check if you have Python

1. **Open Terminal** 
   - **Mac**: Applications → Utilities → Terminal
   - **Windows**: Search for "Command Prompt" or "PowerShell"
   - **Linux**: Press Ctrl+Alt+T
   
2. Type this command and press Enter:
   ```bash
   python --version
   ```
   
3. **What you should see:**
   - ✅ `Python 3.8.x` or higher → You're ready! Skip to [Installation](#installing-lemo-vocabulate-library)
   - ❌ `command not found` or version lower than 3.8 → Continue to next step

#### Step 2: Install Python (if needed)

**Option A: Install Python directly**
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download Python 3.8 or higher
3. Run the installer and follow the prompts
4. ⚠️ **Important**: Check the box that says "Add Python to PATH"

**Option B: Install via Anaconda (recommended for data science)**
1. Go to [anaconda.com/download](https://www.anaconda.com/download)
2. Download and install Anaconda
3. This includes Python, conda, and many useful packages

#### Step 3: Install VS Code (optional but highly recommended)

1. Download from [code.visualstudio.com](https://code.visualstudio.com/)
2. Install the Python extension: [VS Code Python tutorial](https://code.visualstudio.com/docs/python/python-tutorial)

#### Step 4: Verify your Python Installation

Open Terminal/Command Prompt again and run:
```bash
python --version  # Should show Python 3.8 or higher
pip --version     # Should show pip is installed
```

#### Step 5: Install LEMO Vocabulate & Get Started

Now you're ready to install the package and start analyzing text! Open your VS Code terminal, your system terminal, or whatever coding interface you're using and navigate to the Installing LEMO Vocabulate Library section below.

## Installing LEMO Vocabulate Library

First, create a jupyter notebook in VS Code by opening the command palette (Ctrl+Shift+P or Cmd+Shift+P) and selecting "Jupyter: Create New Jupyter Notebook". Then navigate to the terminal in VS Code (View -> Terminal) to run the installation commands below. 

### Option 1: Install in a Conda Environment (Recommended)

For better dependency management, we'd recommend using a conda environment:

```bash
# Create and activate a new environment
conda create -n lemo python=3.8 -y  # must have at least python 3.8
conda activate lemo # run this line in terminal to activate environment
conda install pandas numpy -y # run this line in terminal to install pandas and numpy, which help with data handling
pip install lemo-vocabulate # install the package in the environment
```

### Option 2: Install from PyPI

The simplest way to install LEMO Vocabulate is via pip. In your terminal, run:

```bash
pip install lemo-vocabulate
```
That's it! The package includes the AEV dictionary and stopwords file, so you can start analyzing text immediately. These files are located in the `lemo_vocabulate/data/` directory of the installed package. Or, you can access them programmatically using the `get_data_path` function.


### Option 3: Install from Source

If you want to modify the code or contribute to this library's development:

```bash
# Clone the repository
git clone https://github.com/Bushel-of-Lemons/LEMO_Vocabulate.git
cd LEMO_Vocabulate

# Install in editable mode
pip install -e .
```
---
## Quick Start Guide

At this stage, you can use the `Example-notebook.ipynb` included in the repository for a hands-on introduction. Or, you can follow the examples below to get started quickly by copying and pasting the below code into your own Jupyter notebook cells or Python script and press execute! 

**Note** You may be prompted to install additional dependencies (like pandas or .ipynb extensions) if you don't have them already. Just follow the instructions to complete the installation.

### Basic Example

```python
import pandas as pd
from lemo_vocabulate import run_vocabulate_analysis, get_data_path

# Example using a DataFrame with included data files
df = pd.DataFrame({
    "user_id": ["user_1", "user_2"],
    "text": ["This is a sample text.", "Another example text."]
})

# Use the included dictionary and stopwords and save as an object
results = run_vocabulate_analysis(
    dict_file=get_data_path("AEV_Dict.csv"),
    input_data=df,
    text_column="text",
    stopwords_file=get_data_path("stopwords.txt"),
    raw_counts=True
)

print(results.head())
```

### Using Custom Files

You can still use your own dictionary and stopwords files, just provide the file paths:

```python
# Use custom files
results = run_vocabulate_analysis(
    dict_file="path/to/your/custom_dict.csv", # specify your own dictionary file
    input_data=df,
    text_column="text",
    stopwords_file="path/to/your/custom_stopwords.txt", # specify your own stopwords file
    raw_counts=True # save the raw counts columns (optional)
)
```
---

## Features

- **Tokenization designed for social media text**
    - Twitter-aware tokenizer that handles:
        - Usernames (@user)
        - Hashtags (#happy)
        - Emojis and emoticons
        - URLs
        - Repeated characters (soooo good)
        - Punctuation-heavy social media text

- **Stopword removal**
    - Flexible stopword handling via file or string input

- **Dictionary matching with multi-word wildcards**
    - Compatible with custom dictionaries in CSV format
    - Dictionary provided: `lemo_vocabulate/data/AEV_Dict.csv`
    
    **Dictionary breakdown:**
    ```
    Neg          94
    Pos          53
    AnxFear      20
    Anger        16
    Sadness      36
    NegUndiff    15
    Total words in dictionary: 162
    ```

- **Comprehensive text metrics**
    - Word count, type-token ratio, dictionary coverage
    - Category-level statistics (CWR, CCR, counts, unique counts)

- **Flexible output**
    - Returns Pandas DataFrame
    - Optional CSV export

---

## Usage Examples

### Analyzing a Pandas DataFrame

```python
import pandas as pd
from lemo_vocabulate import run_vocabulate_analysis

# Create sample data
df = pd.DataFrame({
    "text_id": [1, 2, 3],
    "text": [
        "I am so agitated and aggravated!",
        "He was afraid of the dark.",
        "I am so happy happy happy! And sad."
    ]
})

# Run analysis
results = run_vocabulate_analysis(
    dict_file=get_data_path("AEV_Dict.csv"),
    input_data=df,
    text_column="text",
    stopwords_file=get_data_path("stopwords.txt") ,
    raw_counts=True,
    output_csv="results.csv"
)

print(results.head())
```

### Analyzing Text Files in a Folder or Single File

```python
# Analyze a single text file
results = run_vocabulate_analysis(
     dict_file=get_data_path("AEV_Dict.csv"),
    input_data="path/to/file.txt",
    stopwords_file=get_data_path("stopwords.txt") ,
    raw_counts=True
)

# Analyze all .txt files in a folder
results = run_vocabulate_analysis(
    dict_file=get_data_path("AEV_Dict.csv"),
    input_data="path/to/folder",
    stopwords_file=get_data_path("stopwords.txt") ,
    raw_counts=False
)
```

### Merging Results with Original Data

```python
# Run analysis
df_results = run_vocabulate_analysis(
    get_data_path("AEV_Dict.csv"),
    input_data=df,
    text_column="text",
    stopwords_file=get_data_path("stopwords.txt") ,
    raw_counts=True
)

# Create text_id for merging
df_results['text_id'] = df_results.index

# Merge with original data
df_complete = df_results.drop(['text', 'Filename'], axis=1).merge(
    df,
    on='text_id',
    how='left'
)

# Reorder columns
cols = ['text_id', 'text'] + [col for col in df_complete.columns if col not in ['text_id', 'text']]
df_complete = df_complete[cols]
```
---

## Stopwords

Stopword removal allows you to exclude very common function words (e.g., `the`, `and`, `is`, `I`, `you`). In Vocabulate, stopwords are removed **after tokenization** and **before dictionary matching**, which improves the interpretability of dictionary categories.

**Note:** The stopwords file we provide includes the term "hopefully" so this word will not be counted as a positive emotion word, in line with the original Vocabulate tool and [LIWC22](https://www.liwc.app/).

**This package includes a pre-configured stopwords file** that you can use immediately, or you can create your own custom stopwords file.

### Using a Stopwords File (Recommended)

Create a `.txt` file with one word per line:

```txt
the
and
is
i
you
to
```

Use it in your analysis:

```python
from lemo_vocabulate import run_vocabulate_analysis, get_data_path
results = run_vocabulate_analysis(
    dict_file=get_data_path("AEV_Dict.csv"),
    input_data=df,
    text_column="text",
    stopwords_file=get_data_path("stopwords.txt")  # Use bundled stopwords
)
```

### Using a Stopwords String

```python
stopwords = "the\nand\nis\nbe\nnot\n"
results = run_vocabulate_analysis(
    dict_file=get_data_path("AEV_Dict.csv"),
    input_data=df,
    text_column="text",
    stopwords_text=stopwords
)
```

### How Stopwords Affect Output Metrics

**Stopword removal does NOT affect:**
- `WC` (whitespace word count)
- `TC_Raw` (raw token count)
- `TTR_Raw` (raw type-token ratio)

**Stopword removal DOES affect:**

| Column | Effect |
|--------|--------|
| `TC_Clean` | Tokens after stopword removal |
| `TTR_Clean` | Based on clean tokens |
| `TC_NonDict` | Non-dictionary tokens after cleaning |
| `DictPercent` | Higher if stopwords filtered out |
| Category metrics | Only meaningful content words remain |

---

## Understanding the Output

The `run_vocabulate_analysis` function returns a Pandas DataFrame where each row corresponds to a single input text. Below is a detailed explanation of all output columns.

### General Text Metrics

| Column Name    | Description                                                                            |
| -------------- | -------------------------------------------------------------------------------------- |
| `Filename`     | Name of the file or index of the row from the input DataFrame                          |
| `text`         | The full original text that was analyzed                                               |
| `WC`           | Word count: total number of whitespace-separated tokens in the original text           |
| `TC_Raw`       | Token count after tokenizer processing (including punctuation, emoticons, etc.)        |
| `TTR_Raw`      | Type-Token Ratio for raw tokens: `#unique tokens / TC_Raw * 100`                       |
| `TC_Clean`     | Token count after removing stopwords                                                   |
| `TTR_Clean`    | Type-Token Ratio for cleaned tokens: `#unique tokens / TC_Clean * 100`                 |
| `TC_NonDict`   | Number of tokens not matched to any dictionary concept                                 |
| `TTR_NonDict`  | Type-Token Ratio of non-dictionary tokens                                              |
| `DictPercent`  | Percent of tokens matched to dictionary concepts: `num_matched_tokens / TC_Raw * 100`  |
| `CapturedText` | Concatenated string of all dictionary-matched words from the text                      |

### Category-Specific Metrics

For each category in the loaded dictionary (e.g., `Neg`, `Pos`, `AnxFear`, `Anger`, `Sadness`, `NegUndiff`), four metrics are provided:

| Column Suffix | Description                                                                                                                                                  |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `_CWR`        | **Category Word Ratio**: percentage of unique words in the category relative to total words in text. This is the critical measure (i.e., Natural Emotion Vocabularies) used in the Original Vine et al. (2020) paper: `unique_count / WC * 100`                               |
| `_CCR`        | **Category Concept Ratio**: percentage of unique words in the category relative to all matched tokens in that category: `unique_count / total_count * 100`   |
| `_Count`      | **Raw Count**: total number of occurrences of words from this category in the text (only if `raw_counts=True`)                                              |
| `_Unique`     | **Unique Count**: number of unique words in the text that matched this category (only if `raw_counts=True`)                                                 |

#### Example: Category "Neg"

- `Neg_CWR` → % of total words in the text that were unique Neg words relative to total word count
- `Neg_CCR` → % of category words that were unique Neg words relative to the total number of words used that fall into the Neg category
- `Neg_Count` → Total Neg words matched
- `Neg_Unique` → Number of unique Neg words matched

---

## Example Output

| Filename | text | WC | TC_Raw | TTR_Raw | TC_Clean | TTR_Clean | TC_NonDict | TTR_NonDict | DictPercent | CapturedText | Neg_CWR | Neg_CCR | Neg_Count | Neg_Unique | Pos_CWR | Pos_CCR | Pos_Count | Pos_Unique | AnxFear_CWR | AnxFear_CCR | AnxFear_Count | AnxFear_Unique | Anger_CWR | Anger_CCR | Anger_Count | Anger_Unique | Sadness_CWR | Sadness_CCR | Sadness_Count | Sadness_Unique | NegUndiff_CWR | NegUndiff_CCR | NegUndiff_Count | NegUndiff_Unique |
|----------|------|-----|--------|---------|----------|-----------|------------|-------------|-------------|--------------|---------|---------|-----------|------------|---------|---------|-----------|------------|-------------|-------------|---------------|----------------|-----------|-----------|-------------|--------------|-------------|-------------|---------------|----------------|---------------|---------------|-----------------|------------------|
| 0 | I am so angry and agitated! | 6 | 7 | 100.0 | 2 | 100.0 | 0 | 0.0 | 28.57 | angry agitated | 33.33 | 100.0 | 2 | 2 | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0 | 0 | 16.67 | 100.0 | 1 | 1 | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0 | 0 |
| 1 | I'm feeling really happy. Happy but also nervous. | 8 | 10 | 80.0 | 4 | 75.0 | 1 | 100.0 | 30.0 | happy happy nervous | 12.5 | 100.0 | 1 | 1 | 12.5 | 50.0 | 2 | 1 | 12.5 | 100.0 | 1 | 1 | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0 | 0 |
| 2 | It's been an emotional rollercoaster… | 5 | 6 | 100.0 | 3 | 100.0 | 2 | 100.0 | 16.67 | emotional | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0 | 0 | 20.0 | 100.0 | 1 | 1 |
| 3 | It was like a combo of anxiety/agitation. | 7 | 10 | 100.0 | 4 | 100.0 | 2 | 100.0 | 20.0 | anxiety agitation | 28.57 | 100.0 | 2 | 2 | 0.0 | 0.0 | 0 | 0 | 14.29 | 100.0 | 1 | 1 | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0 | 0 |
| 4 | I had a good day. :) | 6 | 7 | 100.0 | 3 | 100.0 | 3 | 100.0 | 0.0 | | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0 | 0 |
| 5 | I dislike disliking people, but I can't help but dislike this person! | 12 | 14 | 78.57 | 6 | 83.33 | 3 | 100.0 | 21.43 | dislike disliking dislike | 8.33 | 33.33 | 3 | 1 | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0 | 0 |
| 6 | I felt bad about work, and I felt bad about my relationships, but I was mostly mad at myself. | 19 | 22 | 72.73 | 7 | 71.43 | 4 | 75.0 | 13.64 | bad bad mad | 5.26 | 100.0 | 1 | 1 | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0 | 0 | 5.26 | 100.0 | 1 | 1 | 0.0 | 0.0 | 0 | 0 | 5.26 | 50.0 | 2 | 1 |
---

## Function Parameters

```python
run_vocabulate_analysis(
    dict_file: str = None,           # Path to dictionary CSV file (required)
    input_data = None,               # DataFrame, file path, or folder path (required)
    text_column: str = None,         # Column name for text (required for DataFrame)
    stopwords_text: str = None,      # Stopwords as newline-separated string
    stopwords_file: str = None,      # Path to stopwords file
    raw_counts: bool = True,         # Include raw counts in output
    encoding: str = "utf-8",         # File encoding
    csv_delimiter: str = ",",        # CSV delimiter
    csv_quote: str = '"',            # CSV quote character
    output_csv: str = None,          # Optional output CSV path
    whitespace_method: str = 'new'   # 'new' (default, recommended) or 'old' (exact C# match)
)
```
**Note about `whitespace_method`**

This parameter controls how the `WC` (word count) metric is calculated and **only affects this one column**.

**`'new'` (default, recommended)**: 
Uses Python's standard `split()` method with additional handling for URLs and file paths:
- Splits text on whitespace 
- Preserves URLs and tokens with periods (e.g., `http://example.com`, `file.txt`) as single tokens
- Handles multiple consecutive spaces, leading/trailing whitespace consistently
- **Best for new analyses** and most use cases

**`'old'`**: 
Replicates the exact whitespace tokenization from the original C# Vocabulate:
- Simple split on whitespace only
- May produce different counts for text with URLs, file paths, or unusual spacing
- **Use this only if** you need to exactly replicate results from the original Windows Vocabulate software

**Important:** The choice of `whitespace_method` only affects the `WC` (word count) column. All other metrics (tokenization, dictionary matching, category ratios) are identical between both methods. We recommend using the default `new` method for all new analyses unless you have a specific reason to replicate legacy results. For example, the `new` method will count "anxiety/sadness" as 2 words while the `old` method will count it as 1 word.

---

## Citation

If you use this software in your research, please cite the original paper that develops the emotion vocabulary technique (Vine et al., 2020) and also the preprint for the current paper for which we developed this python package (Sahi et al., under review)

```bib
@article{vine2020natural,
  title={Natural emotion vocabularies as windows on distress and well-being},
  author={Vine, Vera, Boyd, Ryan L. and Pennebaker, James W.},
  journal={Nature Communications},
  volume={11},
  number={1},
  pages={4525},
  year={2020},
  doi={10.1038/s41467-020-18349-0}
}
```

```bib
@misc{sahi_large_2025,
	title = {Large natural emotion vocabularies are linked with better mental health in psychotherapeutic conversations},
	url = {https://www.researchsquare.com/article/rs-6932501/v1},
	doi = {10.21203/rs.3.rs-6932501/v1},
	urldate = {2025-12-05},
	publisher = {Research Square},
	author = {Sahi, Razia and Hull, Thomas and Vine, Vera and Nook, Erik},
	month = jun,
	year = {2025},
	note = {ISSN: 2693-5015},
	file = {Full Text PDF:files/10200/Sahi et al. - 2025 - Large natural emotion vocabularies are linked with better mental health in psychotherapeutic convers.pdf:application/pdf},
}
```