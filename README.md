# Python Final Project — Web Scraping & Dashboard

## Project Overview

This project is an end-to-end data pipeline that involves:

- Scraping historical baseball data using **Selenium**
- Saving the raw data as **CSV files**
- Importing data into a **SQLite** database
- Querying the database via the **command line**
- Building an interactive dashboard using **Streamlit or Dash**

## Project Structure

python_final_project/
├── scraper/ # Web scraping logic
│ ├── scraper.py
│ ├── config.py
│ └── utils.py
├── data/ # Raw scraped CSV files (gitignored)
├── database/ # SQLite import & query scripts
├── dashboard/ # Streamlit or Dash app
├── requirements.txt # List of dependencies
├── README.md # This file
└── .gitignore



## How to Run the Project

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the scraper:

```bash
python scraper/scraper.py
```

### 3. Import data into SQLite:

```bash
python database/import.py
```

### 4. Launch the dashboard:

```bash
streamlit run dashboard/app.py
```

## Technologies Used

 - Python
 - Selenium – for web scraping
 - Pandas – for data cleaning and transformation
 - SQLite – as the database engine
 - Streamlit or Dash – for dashboard visualization

## Data Source
Data is scraped from the Major League Baseball History website, which includes player stats, historical events, and yearly achievements.

## Screenshots
Coming soon
## Author
Created by [Alena Danilchenko](https://github.com/anelka777).
This project is part of the CTD Python course — Lesson 14 Final Project.