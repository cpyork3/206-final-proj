import unittest
import sqlite3
import json
import os
import urllib.request

def load_nhljson(url, file_path):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                data = response.read().decode('UTF-8')

                with open(file_path, "w") as file:
                    file.write(data)

                print("Data written to file successfully.")
            else:
                print(f"HTTP Error {response.status}: {response.reason}")
                print(response.read().decode('UTF-8'))
    except Exception as e:
        print(f"Error: {e}")

# Example usage
url = 'https://records.nhl.com/site/api/draft'
file_path = 'nhlapi.json'
load_nhljson(url, file_path)