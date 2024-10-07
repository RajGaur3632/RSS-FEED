# -*- coding: utf-8 -*-
"""RSS FEED.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1mXuQo62GsJudRBf0VjrYzpVKvrhINNIR
"""

!pip install feedparser sqlalchemy celery redis Flask pyngrok spacy
!python -m spacy download en_core_web_sm

# Create the app.py file
with open("app.py", "w") as f:
    f.write('''import feedparser
import logging
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from celery import Celery
import spacy
from flask import Flask, render_template
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

# List of RSS feeds
rss_feeds = [
    "http://rss.cnn.com/rss/cnn_topstories.rss",
    "http://qz.com/feed",
    "http://feeds.foxnews.com/foxnews/politics",
    "http://feeds.reuters.com/reuters/businessNews",
    "http://feeds.feedburner.com/NewshourWorld",
    "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml",
]

# Database setup
DATABASE_URI = 'sqlite:///news.db'  # Use SQLite for local testing
engine = create_engine(DATABASE_URI)
Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    published = Column(DateTime)
    link = Column(String)
    category = Column(String)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Function to parse feeds
def parse_feeds():
    articles = []
    for feed_url in rss_feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            article = {
                'title': entry.title,
                'content': entry.get('summary', ''),
                'published': datetime.now(),  # Use current time as published time
                'link': entry.get('link', '')
            }
            if not article['content']:  # Log if no content is found
                logging.warning(f"No content found for article titled: {article['title']}")
            articles.append(article)
    return articles

# Function to store articles in the database
def store_articles(articles):
    for article in articles:
        if not session.query(Article).filter_by(title=article['title']).first():
            new_article = Article(**article)
            session.add(new_article)
    session.commit()

# Setting up Celery
app = Celery('tasks', broker='redis://localhost:6379/0')  # Make sure Redis is running

@app.task
def classify_and_store(article):
    nlp = spacy.load("en_core_web_sm")

    # Define categories
    categories = {
        "Terrorism / protest / political unrest / riot": ["protest", "unrest", "riot", "terrorism"],
        "Positive/Uplifting": ["positive", "uplifting", "happy"],
        "Natural Disasters": ["earthquake", "flood", "disaster", "hurricane"],
        "Others": []
    }

    # Categorize based on keywords
    category_assigned = "Others"

    # Process the article's content
    doc = nlp(article['content'])

    # Categorize based on keywords
    for category, keywords in categories.items():
        if any(keyword in article['content'].lower() for keyword in keywords):
            category_assigned = category
            break

    # Update the article with the category
    article['category'] = category_assigned
    new_article = Article(**article)
    session.add(new_article)
    session.commit()

# Main function to parse, store, and classify articles
def parse_and_store():
    try:
        articles = parse_feeds()
        store_articles(articles)
        for article in articles:
            classify_and_store.delay(article)  # Asynchronous task
    except Exception as e:
        logging.error(f"Error occurred: {e}")

# Flask web app setup
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    # Fetch articles from the database
    articles = session.query(Article).all()
    return render_template('index.html', articles=articles)

# Run the application
if __name__ == "__main__":
    parse_and_store()  # Populate the database with articles
    flask_app.run(host='0.0.0.0', port=5000)  # Run Flask app
''')

import os

# Create templates and static directories
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Create the index.html file
with open("templates/index.html", "w") as f:
    f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RSS Feed Articles</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
</head>
<body>
    <div class="container">
        <h1>RSS Feed Articles</h1>
        {% for article in articles %}
        <div class="article">
            <h2><a href="{{ article.link }}">{{ article.title }}</a></h2>
            <p><strong>Published:</strong> {{ article.published }}</p>
            <p><strong>Category:</strong> {{ article.category }}</p>
            <p>{{ article.content }}</p>
        </div>
        {% endfor %}
    </div>
</body>
</html>
''')

# Create the styles.css file
with open("static/styles.css", "w") as f:
    f.write('''body {
    font-family: Arial, sans-serif;
    margin: 20px;
    background-color: #f8f8f8;
}

.container {
    max-width: 800px;
    margin: auto;
}

h1 {
    text-align: center;
}

.article {
    border: 1px solid #ddd;
    background: white;
    padding: 10px;
    margin: 10px 0;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.article h2 {
    margin: 0 0 10px;
}

.article a {
    text-decoration: none;
    color: #007BFF;
}

.article a:hover {
    text-decoration: underline;
}
''')

from pyngrok import ngrok

# Set your ngrok authentication token
ngrok.set_auth_token("2n7MhIJyncCEegvSBNtJ4CEMAxv_7fng5suJgwnaoSYPRcDet")

# Set up a tunnel to the Flask app
public_url = ngrok.connect(5000)
print(f" * ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:5000\"")

!python app.py

