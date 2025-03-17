# Twitter Archive Processor

## Overview

This tool processes a Twitter archive zip file to extract tweet data. It handles the unzipping of the archive, extraction of tweets and likes data, and saves the processed information to a CSV file matching the format of the provided example.

## Features

- Extract Twitter data directly from archive zip file
- Process tweets and likes into a structured CSV
- Comprehensive data extraction including:
  - Tweet text and timestamps
  - Reply information
  - URL expansion
  - Like and retweet counts
  - Media URLs
- Command-line interface for easy use

## Prerequisites

### Required Packages

- Python 3.6 or higher
- pandas
- requests

## Installation

1. Clone this repository or download the `twitter_archive_processor.py` script

2. Install the required packages:

```bash
pip install pandas requests
```

## Project Structure

The recommended project structure is:

```
tweeter_archive_processor/
├── archive/
│   └── twitter-archive.zip    # Your Twitter archive goes here
├── results/
│   └── tweets_data.csv        # Output will be saved here
├── .gitignore
├── README.md
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
python twitter_archive_processor.py [--archive ARCHIVE_PATH] [--output-dir OUTPUT_DIR]
```

Parameters:
- `--archive`: Path to the Twitter archive zip file (default: twitter-archive.zip)
- `--output-dir`: Directory to store output files (default: results)

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

## Output Files

The script generates `tweets_data.csv` in the output directory, containing all the extracted tweet data.

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

## Troubleshooting

### Common Issues

1. **"Error: twitter-archive.zip is not a valid zip file"**
   - Ensure your archive file is a valid zip file
   - Check that the path to the archive is correct

2. **"Required data files not found in the archive"**
   - Ensure you're using a valid Twitter archive
   - The archive should contain `tweet.js` (or `tweets.js`) and `like.js` files

## Getting Your Twitter Archive

1. Log into your Twitter account
2. Go to Settings > Your Account > Download an archive of your data
3. Follow Twitter's instructions to request and download your archive
4. Place the downloaded zip file in the archive directory


---

*Last updated: March 17, 2025*