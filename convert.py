
from urllib.parse import urlparse
import enchant
from typing import List, Dict, Tuple, Set, Union
from googleapiclient.discovery import build


# Constants for weight calculation
URL_COUNT_WEIGHT = 0.25
URL_ORDER_WEIGHT = -0.25
URL_LEN_WEIGHT = -0.1

# Initialize English dictionary
ENGLISH_DICT = enchant.Dict("en_US")
TRIVIAL_WORDS = {
    "company", "inc", "group", "corporation", "co", "corp", "university",
    "college", "&", "llc", "the", "of", "a", "an"
}

def getURLForQuery(query, query2URLS, api_key="CUSTOM_SEARCH_API", cx="CUSTOM_SEARCH_ENGINE_ID"):
    service = build("customsearch", "v1", developerKey=api_key)
    result = service.cse().list(q=query, cx=cx).execute()
    
    # Store URLs in the dictionary
    query2URLS[query] = [item['link'] for item in result.get('items', [])]

def simplifyURL(url: str) -> str:
    """Simplify URL to its domain."""
    return urlparse(url).netloc

def arrangeWordsByImportance(company: str) -> Tuple[List[str], List[str]]:
    """Arrange company words by importance based on length and dictionary checks."""
    words = sorted(company.lower().split(), key=len, reverse=True)
    nonwords, others = [], []
    
    for word in words:
        if word in TRIVIAL_WORDS:
            continue
        if not ENGLISH_DICT.check(word):
            nonwords.append(word)
        else:
            others.append(word)
    
    return nonwords, others

def getRankedURLSLst(urls: List[str]) -> List[Tuple[str, float]]:
    """Rank URLs using weighted linear combination of features."""
    rankedURLSDict = {}
    min_rank, max_rank = float('inf'), float('-inf')

    for i, url in enumerate(urls):
        simpleURL = simplifyURL(url)
        domain_parts = simpleURL.split(".")
        domain_length = len(domain_parts[1]) if len(domain_parts) == 3 else len(domain_parts[0])

        rank = URL_COUNT_WEIGHT + URL_ORDER_WEIGHT * (i + 1) + URL_LEN_WEIGHT * domain_length
        rankedURLSDict[simpleURL] = rankedURLSDict.get(simpleURL, 0) + rank

        min_rank = min(min_rank, rankedURLSDict[simpleURL])
        max_rank = max(max_rank, rankedURLSDict[simpleURL])

    divisor = max(max_rank - min_rank, 1)  # Prevent division by zero
    return sorted(
        [(url, (rank - min_rank) / divisor) for url, rank in rankedURLSDict.items()],
        key=lambda x: x[1],
        reverse=True
    )

def getCompanyAcronyms(company: str) -> Set[str]:
    """Generate acronyms from company name."""
    all_words = ''.join(word[0] for word in company.split()).lower()
    important = ''.join(word[0] for word in company.split() if word.lower() not in TRIVIAL_WORDS).lower()
    return {all_words, important}

def getBestURL(company: str, urls: List[str]) -> Union[Tuple[str, float, str], str]:
    """Identify the best matching URL for a company."""
    company = ''.join(c for c in company if c not in '.,')
    ranked_urls = getRankedURLSLst(urls)
    nonwords, others = arrangeWordsByImportance(company)
    company_acronyms = getCompanyAcronyms(company)
    simplified_name = company.replace(" ", "").lower()

    for domain, rank in ranked_urls:
        domain_parts = domain.split(".")
        normalized_domain = domain_parts[1] if len(domain_parts) >= 3 else domain_parts[0]

        if normalized_domain in simplified_name or simplified_name in normalized_domain:
            return domain, rank, "domain in companyName or vice versa"

        if normalized_domain in company_acronyms:
            return domain, rank, "domain in company acronyms"

        if any(nonword in normalized_domain for nonword in nonwords):
            return domain, rank * 0.5, "nonword match"

        reduced_domain = normalized_domain
        for word in others:
            reduced_domain = reduced_domain.replace(word, '')

        if len(normalized_domain) <= 4 and len(reduced_domain) <= 1:
            return domain, rank * 0.4, "small domain match"
        elif len(reduced_domain) <= 4:
            return domain, rank * 0.4, "partial domain match"

    return ""

def getQuery2URLS(company_names: List[str]) -> Dict[str, List[str]]:
    """Generate query-to-URL mappings."""
    query2URLS = {}
    for name in company_names:
        getURLForQuery(name, query2URLS)
    return query2URLS

def getBestURLForName(query2URLS: Dict[str, List[str]]) -> Tuple[Dict[str, Tuple[str, float, str]], List[str]]:
    """Find the best URL for each company name."""
    not_found, results = [], {}
    for company, urls in query2URLS.items():
        best_url = getBestURL(company, urls)
        if best_url:
            results[company] = best_url
        else:
            not_found.append(company)
    return results, not_found
