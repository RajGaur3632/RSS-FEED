# RSS Feed Article Collector

## Project Overview

This project collects news articles from various RSS feeds, categorizes them into predefined categories, and displays them on a web page. The application is built using Flask for the web framework, SQLAlchemy for database interactions, Celery for task management, and spaCy for natural language processing.

## Features

- Fetches articles from multiple RSS feeds.
- Categorizes articles into predefined categories:
  - Terrorism / protest / political unrest / riot
  - Positive / Uplifting
  - Natural Disasters
  - Others
- Stores articles in a SQLite database.
- Displays articles in a user-friendly web interface.

## Requirements

- Python 3.x
- Flask
- SQLAlchemy
- Feedparser
- Celery
- Redis (for task queue)
- spaCy
- pyngrok (for exposing local server)

## Installation

1. Clone the repository or download the files.
2. Install the required packages:

   ```bash
   pip install -r requirements.txt
