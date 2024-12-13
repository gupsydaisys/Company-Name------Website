"""1. Sequential Website Checking Method
The first method (check_websites_sequential) uses a straightforward, synchronous approach to checking website statuses
"""
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
"""2. Parallel Website Checking Method
The second method (check_websites_parallel) improves on the first by introducing concurrent checking:
"""
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

###################################################################################################
"""3. Asynchronous Website Checking Method
The third method (WebsiteChecker class) uses an advanced asynchronous approach
"""
import asyncio
import aiohttp
import re
import time
from typing import List, Dict
from functools import lru_cache

class WebsiteChecker:
    def __init__(self, timeout=3, max_concurrent=100):
        """
        Initialize WebsiteChecker with configurable timeout and concurrency.
        
        Args:
            timeout (int): Request timeout in seconds
            max_concurrent (int): Maximum concurrent connections
        """
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

    @staticmethod
    @lru_cache(maxsize=1000)
    def clean_company_name(name: str) -> str:
        """
        Optimized company name cleaning with caching.
        
        Uses regex compilation and caching to improve performance.
        """
        name = name.strip('\ufeff"\'')
        
        # Pre-compile regex for efficiency
        suffixes = [
            re.compile(r'\s+Inc\.?$', re.IGNORECASE),
            re.compile(r'\s+Corp\.?$', re.IGNORECASE),
            re.compile(r'\s+Incorporated$', re.IGNORECASE),
            re.compile(r'\s+Corporation$', re.IGNORECASE),
            re.compile(r'\s+Limited$', re.IGNORECASE),
            re.compile(r'\s+Ltd\.?$', re.IGNORECASE)
        ]
        
        for suffix in suffixes:
            name = suffix.sub('', name)
        
        # Use translation for faster special character removal
        name = name.translate(str.maketrans('', '', '!@#$%^&*()_+-=[]{}|;:,.<>?'))
        
        return ' '.join(name.split())

    def generate_website_urls(self, name: str) -> List[str]:
        """
        Generate multiple URL variations with more intelligent guessing.
        """
        cleaned_name = self.clean_company_name(name).lower().replace(' ', '')
        
        url_variations = [
            f"https://www.{cleaned_name}.com",
            f"https://{cleaned_name}.com",
            f"http://www.{cleaned_name}.com",
            f"http://{cleaned_name}.com",
            # Additional variations
            f"https://{cleaned_name}.net",
            f"https://www.{cleaned_name}.org"
        ]
        
        return url_variations

    async def check_website(self, session: aiohttp.ClientSession, company_name: str) -> Dict:
        """
        Asynchronous website status check with more robust error handling.
        """
        start_time = time.time()
        cleaned_name = self.clean_company_name(company_name)
        
        async with self.semaphore:
            for url in self.generate_website_urls(company_name):
                try:
                    async with session.get(url, timeout=self.timeout) as response:
                        total_time = time.time() - start_time
                        return {
                            'original_name': company_name,
                            'cleaned_name': cleaned_name,
                            'url': url,
                            'status_code': response.status,
                            'time_taken': total_time
                        }
                except (aiohttp.ClientError, asyncio.TimeoutError):
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

    async def check_websites_async(self, companies: List[str]) -> List[Dict]:
        """
        Asynchronously check websites with improved concurrency management.
        """
        async with aiohttp.ClientSession() as session:
            tasks = [self.check_website(session, company) for company in companies]
            return await asyncio.gather(*tasks)

    def run(self, companies: List[str]) -> List[Dict]:
        """
        Main method to run async website checks.
        """
        start_time = time.time()
        results = asyncio.run(self.check_websites_async(companies))
        total_execution_time = time.time() - start_time
        
        print(f"\nAsync Execution Total Time: {total_execution_time:.2f} seconds")
        return results

def main():
    # Read companies from file
    with open('companies.txt', 'r', encoding='utf-8') as f:
        companies = f.read().splitlines()
    
    checker = WebsiteChecker(timeout=3, max_concurrent=50)
    results = checker.run(companies)
    
    # Print results
    for result in results:
        print(f"Original: {result['original_name']}")
        print(f"Cleaned: {result['cleaned_name']}")
        print(f"URL: {result['url']}")
        print(f"Status Code: {result['status_code']}")
        print(f"Time Taken: {result['time_taken']:.4f} seconds\n")

if __name__ == "__main__":
    main()
