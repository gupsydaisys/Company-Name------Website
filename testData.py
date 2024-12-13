import csv
import random
from typing import Dict, Tuple, List

DATASET_PATH = "dataset1.csv"
COMPANIES_FILE_PATH = "companies.txt"
TOTAL_COMPANIES = 947  # Max number of companies in the file

def getData() -> Tuple[Dict[str, str], Dict[str, str]]:
    compToWebTrain = {}
    compToWebTest = {}

    with open(DATASET_PATH, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        arr = next(reader)  # Assuming single line in dataset
        arr = [item.strip() for item in arr if item]

    for i in range(len(arr)):
        if i % 4 == 0:
            compToWebTrain[arr[i]] = arr[i+1].strip()
        elif i % 4 == 2:
            compToWebTest[arr[i]] = arr[i+1].strip()

    return compToWebTrain, compToWebTest

def getNCompanies(n: int = 20) -> List[str]:
    n = max(1, min(n, TOTAL_COMPANIES))  # Clamping n to [1, TOTAL_COMPANIES]
    
    with open(COMPANIES_FILE_PATH, encoding='utf-8') as f:
        lines = [line.strip().strip('\x00').strip('"') for line in f if line.strip()]

    if len(lines) < TOTAL_COMPANIES:
        raise ValueError(f"Expected at least {TOTAL_COMPANIES} lines, found {len(lines)}.")
    
    selected_indices = random.sample(range(len(lines)), n)
    return [lines[i] for i in selected_indices]

# Load dictionaries from CSV
companyToWebsiteTrainingDictionary, companyToWebsiteTestingDictionary = getData()
