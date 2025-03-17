#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter Archive Processor

This script processes a Twitter archive zip file to extract tweet data and perform optional
image classification using the CLIP model. It handles the unzipping of the archive,
extraction of tweets and likes data, and saves the processed information to CSV files.

Usage:
    python twitter_archive_processor.py [--archive ARCHIVE_PATH] [--analyze-images]

Requirements:
    - Python 3.6+
    - pandas
    - transformers
    - torch
    - Pillow
    - requests

Author: Your Name
Version: 1.0.0
Date: March 17, 2025
"""

import argparse
import csv
import json
import os
import re
import shutil
import signal
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from PIL import Image

# Optional imports for image analysis
try:
    import torch
    from transformers import CLIPProcessor, CLIPModel

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


def setup_argument_parser():
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(description='Process Twitter archive and analyze tweet data')
    parser.add_argument('--archive', type=str, default='twitter-archive.zip',
                        help='Path to the Twitter archive zip file (default: twitter-archive.zip)')
    parser.add_argument('--analyze-images', action='store_true',
                        help='Enable image analysis using CLIP model')
    parser.add_argument('--output-dir', type=str, default='output',
                        help='Directory to store output files (default: output)')
    return parser


def load_json_file(filename, prefix):
    """
    Load and clean Twitter JSON file by removing JavaScript variable declarations.

    Args:
        filename (str): Path to the JSON file
        prefix (str): The prefix to remove from the JavaScript variable declaration

    Returns:
        list: Parsed JSON data as a list of dictionaries
    """
    with open(filename, "r", encoding="utf-8") as file:
        js_content = file.read()

    # Remove JavaScript variable declaration if present
    json_str = re.sub(fr"^window\.YTD\.{prefix}\.part0\s*=\s*", "", js_content).rstrip(";")

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in {filename}: {e}")
        return []


def extract_twitter_data(tweets_file, likes_file, output_csv):
    """
    Extract Twitter data from tweets and likes files and save to CSV.

    Args:
        tweets_file (str): Path to the tweets.js file
        likes_file (str): Path to the like.js file
        output_csv (str): Path where the output CSV should be saved

    Returns:
        None
    """
    print(f"Processing tweets from {tweets_file} and likes from {likes_file}...")

    # === Load Tweets Data ===
    tweets_data = load_json_file(tweets_file, "tweets")
    tweets = {t["tweet"].get("id_str"): t["tweet"] for t in tweets_data}
    print(f"Loaded {len(tweets)} tweets")

    # === Load Likes Data & Count Likes Per Tweet ID ===
    likes_data = load_json_file(likes_file, "like")
    like_counts = {}
    for like in likes_data:
        tweet_id = like.get("like", {}).get("tweetId")
        if tweet_id:
            like_counts[tweet_id] = like_counts.get(tweet_id, 0) + 1
    print(f"Processed {len(likes_data)} likes")

    # === Write Data to CSV ===
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'tweet_id', 'in_reply_to_status_id', 'in_reply_to_user_id',
            'in_reply_to_status_username', 'timestamp', 'source', 'text',
            'expanded_urls', 'tweet_url', 'retweet_count', 'favorite_count',
            'like_count'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for tweet_id, tweet in tweets.items():
            # Convert timestamp
            timestamp = tweet.get('created_at', '')
            formatted_timestamp = ''
            if timestamp:
                try:
                    formatted_timestamp = datetime.strptime(
                        timestamp, '%a %b %d %H:%M:%S +0000 %Y'
                    ).strftime('%Y-%m-%d %H:%M:%S')
                except ValueError as e:
                    print(f"Error parsing timestamp '{timestamp}': {e}")

            # Extract tweet text
            text = tweet.get('full_text', '').replace('\n', ' ')

            # Extract URLs
            expanded_urls = ', '.join([
                url['expanded_url'] for url in tweet.get('entities', {}).get('urls', [])
                if 'expanded_url' in url
            ])

            # Create tweet URL
            user_id = tweet.get('user_id_str', '')
            tweet_url = f"https://twitter.com/{user_id}/status/{tweet_id}"

            # Extract counts
            retweet_count = tweet.get('retweet_count', 0)
            favorite_count = tweet.get('favorite_count', 0)
            like_count = like_counts.get(tweet_id, 0)

            # Extract media URLs
            media_urls = ', '.join([
                media.get('media_url', '')
                for media in tweet.get('entities', {}).get('media', [])
                if media.get('media_url')
            ])

            # Extract reply information
            in_reply_to_status_id = tweet.get('in_reply_to_status_id_str', '')
            in_reply_to_user_id = tweet.get('in_reply_to_user_id_str', '')
            in_reply_to_screen_name = tweet.get('in_reply_to_screen_name', '')

            # Extract source (the app used to post)
            source = tweet.get('source', '')
            # Clean HTML from source
            source = re.sub(r'<[^>]+>', '', source) if source else ''

            writer.writerow({
                'tweet_id': tweet_id,
                'in_reply_to_status_id': in_reply_to_status_id,
                'in_reply_to_user_id': in_reply_to_user_id,
                'in_reply_to_status_username': in_reply_to_screen_name,
                'timestamp': formatted_timestamp,
                'source': source,
                'text': text,
                'expanded_urls': expanded_urls,
                'tweet_url': tweet_url,
                'retweet_count': retweet_count,
                'favorite_count': favorite_count,
                'like_count': like_count
            })

    print(f"✅ Extracted Twitter data saved as {output_csv}")
    return output_csv


def classify_image(image_url, processor, model, categories):
    """
    Classify an image using the CLIP model.

    Args:
        image_url (str): URL of the image to classify
        processor (CLIPProcessor): CLIP processor
        model (CLIPModel): CLIP model
        categories (list): List of category names to classify against

    Returns:
        list: Probability scores for each category
    """
    try:
        # Download and process the image
        response = requests.get(image_url, stream=True, timeout=10)
        if response.status_code != 200:
            print(f"Failed to download image {image_url}: HTTP {response.status_code}")
            return [0.0] * len(categories)

        image = Image.open(response.raw)

        # Process image with CLIP
        inputs = processor(text=categories, images=image, return_tensors="pt", padding=True)
        outputs = model(**inputs)
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1).squeeze(0).tolist()

        return probs
    except Exception as e:
        print(f"Error processing image {image_url}: {e}")
        return [0.0] * len(categories)


def analyze_images(csv_file, output_csv):
    """
    Analyze images in tweets using the CLIP model.

    Args:
        csv_file (str): Path to the CSV file with tweet data
        output_csv (str): Path where the output CSV should be saved

    Returns:
        None
    """
    if not TRANSFORMERS_AVAILABLE:
        print("⚠️ Transformers library not available. Please install with: pip install transformers torch")
        return

    print("Initializing CLIP model for image analysis...")
    try:
        model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
        print("✅ CLIP model loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load CLIP model: {e}")
        return

    # Categories for classification
    categories = ["meme", "infographic", "book recommendation", "promotion"]

    # Load the CSV file
    try:
        data = pd.read_csv(csv_file)
        print(f"Loaded dataset with {len(data)} rows")
    except Exception as e:
        print(f"❌ Failed to load CSV file: {e}")
        return

    # Analyze images
    print("Analyzing images in tweets...")

    # Add columns for image analysis if they don't exist
    if 'Image Category' not in data.columns:
        data['Image Category'] = ''
    if 'Probability' not in data.columns:
        data['Probability'] = 0.0

    # Count tweets with media
    media_count = data['media_url'].notna().sum()
    print(f"Found {media_count} tweets with media URLs")

    # Process each tweet with media
    processed = 0
    for index, row in data.iterrows():
        media_urls = row.get('media_url', None)

        if pd.notna(media_urls) and isinstance(media_urls, str) and media_urls.strip():
            first_url = media_urls.split(',')[0].strip()

            if first_url:
                print(f"Processing image {processed + 1}/{media_count}: {first_url}")
                probabilities = classify_image(first_url, processor, model, categories)

                # Find the highest probability category
                max_prob = max(probabilities)
                max_category = categories[probabilities.index(max_prob)]

                # Update the dataframe
                data.at[index, 'Image Category'] = max_category
                data.at[index, 'Probability'] = max_prob

                processed += 1
                if processed % 10 == 0:
                    print(f"Progress: {processed}/{media_count} images processed")

    # Save the updated dataframe
    data.to_csv(output_csv, index=False)
    print(f"✅ Updated dataset with image analysis saved as {output_csv}")


def extract_twitter_archive(archive_path, extract_dir):
    """
    Extract Twitter archive zip file to a directory.

    Args:
        archive_path (str): Path to the Twitter archive zip file
        extract_dir (str): Directory to extract the archive to

    Returns:
        bool: True if extraction was successful, False otherwise
    """
    try:
        # Create the extraction directory if it doesn't exist
        os.makedirs(extract_dir, exist_ok=True)

        # Extract the archive
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        print(f"✅ Successfully extracted archive to {extract_dir}")
        return True
    except zipfile.BadZipFile:
        print(f"❌ Error: {archive_path} is not a valid zip file.")
        return False
    except Exception as e:
        print(f"❌ Error extracting archive: {e}")
        return False


def find_data_files(extract_dir):
    """
    Find the tweets.js and like.js files in the extracted archive.

    Args:
        extract_dir (str): Directory where the archive was extracted

    Returns:
        tuple: (tweets_file, likes_file) paths, or (None, None) if not found
    """
    # Initialize paths
    tweets_file = None
    likes_file = None

    # Define possible data directories
    data_dirs = [
        extract_dir,
        os.path.join(extract_dir, 'data'),
        os.path.join(extract_dir, 'tweet.js'),
        os.path.join(extract_dir, 'like.js')
    ]

    # Look for tweet.js and like.js files
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if file.lower() == 'tweet.js' or file.lower() == 'tweets.js':
                tweets_file = os.path.join(root, file)
            elif file.lower() == 'like.js':
                likes_file = os.path.join(root, file)

    # Report findings
    if tweets_file:
        print(f"Found tweets file: {tweets_file}")
    else:
        print("❌ Could not find tweets.js file in the archive")

    if likes_file:
        print(f"Found likes file: {likes_file}")
    else:
        print("❌ Could not find like.js file in the archive")

    return tweets_file, likes_file


def cleanup(extract_dir):
    """
    Clean up temporary files and directories.

    Args:
        extract_dir (str): Path to the temporary extraction directory

    Returns:
        None
    """
    try:
        shutil.rmtree(extract_dir)
        print(f"✅ Cleaned up temporary directory {extract_dir}")
    except Exception as e:
        print(f"⚠️ Warning: Could not clean up {extract_dir}: {e}")


def main():
    """Main function to process Twitter archive."""
    # Set up argument parser
    parser = setup_argument_parser()
    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Define paths
    temp_dir = os.path.join(args.output_dir, 'temp_extract')
    csv_output = os.path.join(args.output_dir, 'tweets_data.csv')
    csv_with_img_output = os.path.join(args.output_dir, 'tweets_data_with_image_analysis.csv')

    print(f"Processing Twitter archive: {args.archive}")

    # Extract archive
    if not extract_twitter_archive(args.archive, temp_dir):
        return

    # Find data files
    tweets_file, likes_file = find_data_files(temp_dir)
    if not tweets_file or not likes_file:
        print("❌ Required data files not found in the archive. Aborting.")
        cleanup(temp_dir)
        return

    # Process Twitter data
    extract_twitter_data(tweets_file, likes_file, csv_output)

    # Analyze images if requested
    if args.analyze_images:
        if not TRANSFORMERS_AVAILABLE:
            print("⚠️ Image analysis requested but transformers library not available.")
            print("Please install required libraries with: pip install transformers torch")
        else:
            analyze_images(csv_output, csv_with_img_output)

    # Clean up
    cleanup(temp_dir)

    print("\n===== Twitter Archive Processing Complete =====")
    print(f"Output files saved to the {args.output_dir} directory:")
    print(f"  - {csv_output} (Basic tweet data)")
    if args.analyze_images and TRANSFORMERS_AVAILABLE:
        print(f"  - {csv_with_img_output} (Tweet data with image analysis)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user. Exiting...")
        exit(1)
