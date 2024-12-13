import requests
import concurrent.futures
import re
import os
from typing import List, Tuple

def normalize_company_name(name: str) -> str:
    """
    Normalize company name to create a potential website URL.
    
    Args:
        name (str): Company name to normalize
    
    Returns:
        str: Normalized website URL
    """
    # Remove quotes, special characters
    name = name.strip('"')
    
    # Convert to lowercase
    name = name.lower()
    
    # Remove 'inc', 'corp', 'incorporated', etc.
    name = re.sub(r'\s+(inc\.?|corp\.?|incorporated|corporation)$', '', name)
    
    # Replace spaces and special characters
    name = re.sub(r'[^a-z0-9]+', '', name)
    
    return f"https://www.{name}.com"

def check_website_status(company_name: str) -> Tuple[str, int]:
    """
    Check the status code of a company's website.
    
    Args:
        company_name (str): Name of the company
    
    Returns:
        Tuple of (company_name, status_code)
    """
    try:
        # Generate potential website URL
        url = normalize_company_name(company_name)
        
        # Send GET request with a timeout
        response = requests.get(url, timeout=5)
        
        return (company_name, response.status_code)
    
    except requests.RequestException as e:
        # Handle various request exceptions
        return (company_name, 0)

def check_websites_sequential(companies_file: str) -> List[Tuple[str, int]]:
    """
    Check website status sequentially for companies in a text file.
    
    Args:
        companies_file (str): Path to the text file with company names
    
    Returns:
        List of tuples with (company_name, status_code)
    """
    results = []
    
    # Read companies from file
    with open(companies_file, 'r', encoding='utf-8-sig') as f:
        companies = f.read().splitlines()
    
    # Check each website sequentially
    for company in companies:
        results.append(check_website_status(company))
    
    return results

def check_websites_parallel(companies_file: str, max_workers: int = 10) -> List[Tuple[str, int]]:
    """
    Check website status in parallel for companies in a text file.
    
    Args:
        companies_file (str): Path to the text file with company names
        max_workers (int, optional): Maximum number of concurrent checks. Defaults to 10.
    
    Returns:
        List of tuples with (company_name, status_code)
    """
    # Read companies from file
    with open(companies_file, 'r', encoding='utf-8-sig') as f:
        companies = f.read().splitlines()
    
    # Use ThreadPoolExecutor for I/O bound tasks like web requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Map the check_website_status function to all companies
        results = list(executor.map(check_website_status, companies))
    
    return results

def main():
    # Example usage
    companies_file = 'companies.txt'
    
    print("Sequential Website Status Check:")
    sequential_results = check_websites_sequential(companies_file)
    for company, status in sequential_results:
        print(f"{company}: Status Code {status}")
    
    print("\nParallel Website Status Check:")
    parallel_results = check_websites_parallel(companies_file)
    for company, status in parallel_results:
        print(f"{company}: Status Code {status}")

if __name__ == "__main__":
    main()

##########################################################################################
import requests
import concurrent.futures
import re
import os
import time
from typing import List, Tuple, Dict

def clean_company_name(name: str) -> str:
    """
    Clean company name by removing:
    - Quotes
    - Unnecessary suffixes
    - Special characters
    
    Args:
        name (str): Raw company name
    
    Returns:
        str: Cleaned company name
    """
    # Remove UTF-8 BOM if present
    name = name.strip('\ufeff')
    
    # Remove quotes
    name = name.strip('"\'')
    
    # Remove common suffixes
    suffixes_to_remove = [
        r'\s+Inc\.?$', 
        r'\s+Corp\.?$', 
        r'\s+Incorporated$', 
        r'\s+Corporation$', 
        r'\s+Limited$', 
        r'\s+Ltd\.?$'
    ]
    
    for suffix in suffixes_to_remove:
        name = re.sub(suffix, '', name, flags=re.IGNORECASE)
    
    # Remove special characters, keep letters, numbers, spaces
    name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    
    # Remove extra whitespaces
    name = ' '.join(name.split())
    
    return name

def normalize_company_name(name: str) -> str:
    """
    Generate a potential website URL from a cleaned company name.
    
    Args:
        name (str): Cleaned company name
    
    Returns:
        str: Normalized website URL
    """
    # Convert to lowercase and remove spaces
    url_name = clean_company_name(name).lower().replace(' ', '')
    
    # Try multiple URL variations
    url_variations = [
        f"https://www.{url_name}.com",
        f"https://{url_name}.com",
        f"http://www.{url_name}.com",
        f"http://{url_name}.com"
    ]
    
    return url_variations

def check_website_status(company_name: str) -> Dict[str, str|int|float]:
    """
    Check the status code of a company's website.
    
    Args:
        company_name (str): Name of the company
    
    Returns:
        Dict with company details and status
    """
    start_time = time.time()
    
    # Clean the company name
    cleaned_name = clean_company_name(company_name)
    
    # Try multiple URL variations
    url_variations = normalize_company_name(cleaned_name)
    
    for url in url_variations:
        try:
            # Send GET request with a timeout
            response = requests.get(url, timeout=5)
            
            # Calculate total time taken
            total_time = time.time() - start_time
            
            return {
                'original_name': company_name,
                'cleaned_name': cleaned_name,
                'url': url,
                'status_code': response.status_code,
                'time_taken': total_time
            }
        
        except requests.RequestException:
            continue
    
    # If no URL works
    total_time = time.time() - start_time
    return {
        'original_name': company_name,
        'cleaned_name': cleaned_name,
        'url': 'N/A',
        'status_code': 0,
        'time_taken': total_time
    }

def check_websites_sequential(companies_file: str) -> List[Dict[str, str|int|float]]:
    """
    Check website status sequentially for companies in a text file.
    
    Args:
        companies_file (str): Path to the text file with company names
    
    Returns:
        List of dicts with company and status details
    """
    start_total_time = time.time()
    results = []
    
    # Read companies from file
    with open(companies_file, 'r', encoding='utf-8') as f:
        companies = f.read().splitlines()
    
    # Check each website sequentially
    for company in companies:
        results.append(check_website_status(company))
    
    total_execution_time = time.time() - start_total_time
    
    print(f"\nSequential Execution Total Time: {total_execution_time:.2f} seconds")
    return results

def check_websites_parallel(companies_file: str, max_workers: int = 10) -> List[Dict[str, str|int|float]]:
    """
    Check website status in parallel for companies in a text file.
    
    Args:
        companies_file (str): Path to the text file with company names
        max_workers (int, optional): Maximum number of concurrent checks. Defaults to 10.
    
    Returns:
        List of dicts with company and status details
    """
    start_total_time = time.time()
    
    # Read companies from file
    with open(companies_file, 'r', encoding='utf-8') as f:
        companies = f.read().splitlines()
    
    # Use ThreadPoolExecutor for I/O bound tasks like web requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Map the check_website_status function to all companies
        results = list(executor.map(check_website_status, companies))
    
    total_execution_time = time.time() - start_total_time
    
    print(f"\nParallel Execution Total Time: {total_execution_time:.2f} seconds")
    return results

def main():
    # Example usage
    companies_file = 'companies.txt'
    
    print("Sequential Website Status Check:")
    sequential_results = check_websites_sequential(companies_file)
    for result in sequential_results:
        print(f"Original: {result['original_name']}")
        print(f"Cleaned: {result['cleaned_name']}")
        print(f"URL: {result['url']}")
        print(f"Status Code: {result['status_code']}")
        print(f"Time Taken: {result['time_taken']:.4f} seconds\n")
    
    print("\nParallel Website Status Check:")
    parallel_results = check_websites_parallel(companies_file)
    for result in parallel_results:
        print(f"Original: {result['original_name']}")
        print(f"Cleaned: {result['cleaned_name']}")
        print(f"URL: {result['url']}")
        print(f"Status Code: {result['status_code']}")
        print(f"Time Taken: {result['time_taken']:.4f} seconds\n")

if __name__ == "__main__":
    main()
