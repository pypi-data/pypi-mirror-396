"""
Weather Report Data Scraping Module

Scrapes textual weather forecast reports from SPC (Storm Prediction Center)
and extracts summary discussions for pairing with weather data.
"""

import os
from pathlib import Path
from typing import Optional
import pandas as pd
import requests
from bs4 import BeautifulSoup

from wxcbench.forecast_report_generation.config import (
    SPC_BASE_URL,
    SPC_DATE_RANGE_URL_TEMPLATE,
    DEFAULT_CAPTION_OUTPUT_DIR
)


def scrape_weather_reports(
    start_date: str,
    end_date: str,
    output_dir: Optional[str] = None
) -> pd.DataFrame:
    """
    Scrape weather forecast reports from SPC and save them as CSV files.
    
    This function fetches weather reports within a specified date range from the
    Storm Prediction Center (SPC) and extracts summary discussions from the reports.
    The extracted data is saved as CSV files for pairing with HRRR weather data.
    
    Parameters
    ----------
    start_date : str
        Start date of the time range in YYYY-MM-DD format
        Example: "2021-06-27"
    end_date : str
        End date of the time range in YYYY-MM-DD format
        Example: "2021-06-27"
    output_dir : str, optional
        Directory to save the output CSV files.
        If None, uses default from config (default: None)
        
    Returns
    -------
    pd.DataFrame
        DataFrame containing scraped weather report data with columns:
        date, time, url, discussion
        
    Examples
    --------
    >>> import wxcbench.forecast_report_generation as frg
    >>> df = frg.scrape_weather_reports(
    ...     start_date="2021-06-27",
    ...     end_date="2021-06-27"
    ... )
    """
    if output_dir is None:
        output_dir = DEFAULT_CAPTION_OUTPUT_DIR
    
    # Construct the SPC URL for the specified date range
    url = f"{SPC_DATE_RANGE_URL_TEMPLATE}?date0={start_date}&date1={end_date}"
    print(f"Base URL: {url}")
    
    # Fetch the page content
    try:
        page = requests.get(url, timeout=30)
        page.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f"Error fetching URL {url}: {e}")
    
    try:
        soup = BeautifulSoup(page.content, "html.parser")
    except Exception as e:
        raise Exception(f"Error parsing HTML content: {e}")
    
    # Extract report links from the page
    links = soup.find_all('a', href=True)
    report_links = [
        f"{SPC_BASE_URL}{a['href']}"
        for a in links
        if "otlk" in a.get("href", "") and ".html" in a.get("href", "")
    ]
    
    print(f"Found {len(report_links)} URLs to scrape")
    
    # Initialize a dictionary to store the scraped data
    outlook_data = {
        "date": [],
        "time": [],
        "url": [],
        "discussion": [],
    }
    
    # Scrape each report
    for report_url in report_links:
        try:
            # Extract date and time from URL
            url_parts = report_url.split(".")
            if len(url_parts) >= 2:
                date_time_part = url_parts[-2]  # Part before .html
                date_time_split = date_time_part.split("_")
                if len(date_time_split) >= 2:
                    date = date_time_split[-2]
                    time = date_time_split[-1]
                else:
                    continue
            else:
                continue
            
            # Fetch the report page
            report_page = requests.get(report_url, timeout=30)
            report_page.raise_for_status()
            soup = BeautifulSoup(report_page.content, "html.parser")
            
            # Extract summary from pre tags
            pre_tags = soup.find_all('pre')
            for pre_tag in pre_tags:
                text_report = pre_tag.text
                
                # Extract the "summary" section from the report
                if "...SUMMARY..." in text_report:
                    summary = text_report.split("...SUMMARY...")[-1].split("...")[0]
                else:
                    # If no SUMMARY marker, take the full text
                    summary = text_report
                
                outlook_data["date"].append(date)
                outlook_data["time"].append(time)
                outlook_data["url"].append(report_url)
                outlook_data["discussion"].append(summary.strip())
                
        except Exception as e:
            print(f"Error processing URL {report_url}: {e}")
            continue
    
    # Save the scraped data as CSV files
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if outlook_data["date"]:
        # Group by date and save separate CSV files for each date
        df = pd.DataFrame(outlook_data)
        
        # Save combined data
        for date in df["date"].unique():
            date_df = df[df["date"] == date]
            output_file = output_path / f"{date}.csv"
            date_df.to_csv(output_file, index=False)
            print(f"Data saved to: {output_file}")
        
        print(f"Scraping complete. Total reports: {len(df)}")
        return df
    else:
        print("Warning: No data was scraped.")
        return pd.DataFrame(outlook_data)

