# Twitter Archive Processor

## Overview

This tool processes a Twitter archive zip file to extract tweet data. It handles the unzipping of the archive, extraction of tweets and likes data, and saves the processed information to a CSV file matching the format of the provided example.

## Features

- Extract Twitter data directly from archive zip file
- Process tweets and likes into a structured CSV
- Optional image analysis using the CLIP model
- Comprehensive data extraction including:
  - Tweet text and timestamps
  - Reply information
  - URL expansion
  - Like and retweet counts
  - Media URLs
- Command-line interface for easy use

## Prerequisites

### Required Packages

- Python 3.9 recommended
- NumPy < 2.0 (important for compatibility)
- pandas
- requests
- Pillow
- Optional: transformers and torch (for image analysis)

## Installation

1. Clone this repository or download the `twitter_archive_processor.py` script

   ```bash
   git clone https://github.com/yourusername/tweeter_archive_processor.git
   cd tweeter_archive_processor
   ```

2. Set up the environment using conda with environment.yml (recommended):

   ```bash
   # Create and set up environment using environment.yml
   conda env create -f environment.yml
   conda activate twitter_env
   ```

   The environment.yml file contains all the necessary dependencies with specific version requirements:
   
   ```yaml
   name: twitter_env
   channels:
     - conda-forge
     - defaults
   dependencies:
     - python=3.9
     - numpy=1.24.0
     - pandas=1.5.3
     - pillow=9.4.0
     - requests=2.28.2
     - pip=22.3.1
     - pip:
       - transformers==4.26.0
       - torch==1.13.1
   ```
   
   This approach ensures that all dependencies are installed with the exact versions needed to avoid compatibility issues. The YML file specifies that packages should be installed from conda-forge and defaults channels, with specific packages from pip where necessary.

   Alternatively, you can install packages manually:

   ```bash
   # Create conda environment
   conda create -n twitter_env python=3.9
   conda activate twitter_env
   
   # Install core dependencies
   conda install -c conda-forge numpy=1.24.0 pandas=1.5.3 pillow=9.4.0 requests=2.28.2
   
   # Optional: Install for image analysis
   pip install transformers==4.26.0 torch==1.13.1
   ```

3. Or install using pip with the requirements.txt file:

   ```bash
   pip install -r requirements.txt
   ```

### Important Note on NumPy Compatibility

This project requires NumPy version less than 2.0 due to compatibility issues with pandas and other dependencies. Using NumPy 2.x may result in errors like:

```
A module that was compiled using NumPy 1.x cannot be run in NumPy 2.x
```

## Project Structure

The recommended project structure is:

```
tweeter_archive_processor/
├── archive/
│   └── twitter-archive.zip    # Your Twitter archive goes here
├── output/
│   └── tweets_data.csv        # Output will be saved here
├── .gitignore
├── README.md
├── environment.yml            # Conda environment configuration
├── requirements.txt           # Pip requirements file
└── twitter_archive_processor.py
```

## Usage

### Basic Usage

The simplest way to run the script is:

```bash
python twitter_archive_processor.py
```

This will look for `twitter-archive.zip` in the archive directory and create a CSV file with all your tweet data in the results directory.

### Archive File Naming

By default, the script expects the archive file to be named `twitter-archive.zip`. You can specify a different filename with the `--archive` parameter.

### Command-line Options

```
python twitter_archive_processor.py [--archive ARCHIVE_PATH] [--output-dir OUTPUT_DIR] [--analyze-images]
```

Parameters:
- `--archive`: Path to the Twitter archive zip file (default: twitter-archive.zip)
- `--output-dir`: Directory to store output files (default: results)
- `--analyze-images`: Enable image analysis using CLIP model (requires transformers and torch)

### Example Commands

Process archive with default name:
```bash
python twitter_archive_processor.py
```

Process archive with custom name:
```bash
python twitter_archive_processor.py --archive archive/my_twitter_data.zip
```

Specify output directory:
```bash
python twitter_archive_processor.py --output-dir my_results
```

Enable image analysis:
```bash
python twitter_archive_processor.py --analyze-images
```

## Output Files

The script generates:
- `tweets_data.csv` in the output directory, containing all the extracted tweet data
- `tweets_data_with_image_analysis.csv` (if image analysis is enabled)

## CSV Format

The output CSV includes the following columns:

- `tweet_id`: Unique identifier for the tweet
- `in_reply_to_status_id`: ID of the tweet this is a reply to (if applicable)
- `in_reply_to_user_id`: ID of the user this tweet replies to (if applicable)
- `in_reply_to_status_username`: Username this tweet replies to (if applicable)
- `timestamp`: Timestamp of the tweet in YYYY-MM-DD HH:MM:SS format
- `source`: Application used to post the tweet
- `text`: Content of the tweet
- `expanded_urls`: URLs included in the tweet, expanded from shortened forms
- `tweet_url`: Direct URL to the tweet
- `retweet_count`: Number of retweets
- `favorite_count`: Number of favorites
- `like_count`: Number of likes

With image analysis enabled, additional columns:
- `Image Category`: Categorization of the image (meme, infographic, etc.)
- `Probability`: Confidence score of the classification

## Troubleshooting

### Common Issues

1. **"Error: twitter-archive.zip is not a valid zip file"**
   - Ensure your archive file is a valid zip file
   - Check that the path to the archive is correct

2. **"Required data files not found in the archive"**
   - Ensure you're using a valid Twitter archive
   - The archive should contain `tweet.js` (or `tweets.js`) and `like.js` files

3. **NumPy version errors**
   - If you see NumPy compatibility errors, ensure you're using NumPy version less than 2.0
   - Use the provided environment.yml or requirements.txt to set up your environment

4. **Recursion errors with transformers**
   - If you encounter recursion errors when using the image analysis feature, try:
     - Increasing Python's recursion limit
     - Using the specific versions of transformers and torch in environment.yml

## Getting Your Twitter Archive

1. Log into your Twitter account
2. Go to Settings > Your Account > Download an archive of your data
3. Follow Twitter's instructions to request and download your archive
4. Place the downloaded zip file in the archive directory

---

*Last updated: March 21, 2025. We recommend using the conda environment with environment.yml file for setup as it's the most reliable method to ensure compatibility across all dependencies.*