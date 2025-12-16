"""
Web Health Checker - A Python package for website health monitoring.

This module provides functions to check website status, SSL certificates,
DNS resolution, and HTTP redirects.
"""

__all__ = [
    'check_website',
    'check_multiple',
    'save_to_csv',
    'check_ssl',
    'check_redirects',
    'check_dns',
    'WebHealthChecker'
]


class WebHealthChecker:
    """
    A simple class to perform website health checks.
    
    Attributes:
        urls (list): List of URLs to check.
        full_scan (bool): Whether to perform full scan (SSL, DNS, redirects).
    
    Example:
        >>> checker = WebHealthChecker(['https://google.com', 'https://github.com'])
        >>> results = checker.check()
        >>> for result in results:
        ...     print(result['url'], result['status'])
    """
    
    def __init__(self, urls, full_scan=False):
        """
        Initialize WebHealthChecker.
        
        Args:
            urls (list): URLs to check.
            full_scan (bool): Enable full scan. Default is False.
        """
        self.urls = urls if isinstance(urls, list) else [urls]
        self.full_scan = full_scan
    
    def check(self):
        """
        Perform health checks on all URLs.
        
        Returns:
            list: List of result dictionaries with keys: url, status, 
                  response_time, status_code, ssl_status, dns_status, redirects.
        """
        results = []
        for url in self.urls:
            result = check_website(url)
            
            if self.full_scan:
                if 'ONLINE' in result['status']:
                    result.update(check_ssl(url))
                    result.update(check_dns(url))
                
                redirect_info = check_redirects(url)
                result.update(redirect_info)
            
            results.append(result)
        
        return results
    
    def export_csv(self, filename):
        """
        Export results to CSV file.
        
        Args:
            filename (str): Output CSV filename.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        results = self.check()
        return save_to_csv(results, filename)

from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
import urllib.request
import time
import csv
import ssl
import json
import socket

DEFAULT_TIMEOUT = 10
MAX_REDIRECTS = 5
USER_AGENT = 'Mozilla/5.0 (Web Health Checker Pro)'

def check_website(url):
    """Vérifie si un site est en ligne avec gestion améliorée des statuts"""
    try:
        start_time = time.time()
        req = Request(url, headers={'User-Agent': USER_AGENT})
        
        with urlopen(req, timeout=DEFAULT_TIMEOUT) as response:
            status_code = response.status
            if 200 <= status_code < 400:
                status = 'ONLINE'
            else:
                status = f'HTTP {status_code}'
            
            return {
                'url': url,
                'status': status,
                'status_code': status_code,
                'response_time': round(time.time() - start_time, 3),
                'error': None
            }
            
    except HTTPError as e:
        return {
            'url': url,
            'status': f'HTTP ERROR: {e.code}',
            'status_code': e.code,
            'response_time': None,
            'error': str(e)
        }
    except URLError as e:
        return {
            'url': url,
            'status': 'CONNECTION ERROR',
            'status_code': None,
            'response_time': None,
            'error': str(e)
        }
    except Exception as e:
        return {
            'url': url,
            'status': 'UNKNOWN ERROR',
            'status_code': None,
            'response_time': None,
            'error': str(e)
        }

def check_multiple(urls, max_workers=5):
    """Vérifie plusieurs sites en parallèle"""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(check_website, urls))

def check_ssl(url):
    """Vérifie la validité du certificat SSL"""
    hostname = urlparse(url).hostname
    if not hostname:
        return {"ssl_status": "INVALID URL", "ssl_valid": False}
    
    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, 443), timeout=DEFAULT_TIMEOUT) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                return {
                    "ssl_status": "VALID SSL",
                    "ssl_valid": True,
                    "ssl_issuer": dict(x[0] for x in cert['issuer']),
                    "ssl_expires": cert['notAfter']
                }
    except Exception as e:
        return {"ssl_status": "SSL ERROR", "ssl_valid": False, "ssl_error": str(e)}

def check_redirects(url):
    """Détecte les redirections HTTP"""
    class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, hdrs, newurl):
            return None
    
    opener = urllib.request.build_opener(NoRedirectHandler)
    try:
        resp = opener.open(url, timeout=DEFAULT_TIMEOUT)
        return {"redirects": False}
    except HTTPError as e:
        if e.code in (301, 302, 303, 307, 308):
            return {
                "redirects": True,
                "redirect_url": e.headers['Location'],
                "redirect_code": e.code
            }
        return {"redirects": False}

def check_dns(url):
    """Vérifie la résolution DNS"""
    hostname = urlparse(url).hostname
    if not hostname:
        return {"dns_status": "INVALID HOSTNAME"}
    
    try:
        start = time.perf_counter()
        ip = socket.gethostbyname(hostname)
        return {
            "dns_status": "RESOLVED",
            "dns_ip": ip,
            "dns_time": round(time.perf_counter() - start, 3)
        }
    except Exception as e:
        return {"dns_status": f"DNS ERROR: {str(e)}"}

def save_to_csv(results, csv_filename="status_report.csv"):
    """Exporte les résultats en CSV avec gestion des champs optionnels"""
    if not results:
        return False

    # Collecte de tous les champs possibles
    all_fields = set()
    for result in results:
        all_fields.update(result.keys())
    
    fieldnames = sorted(all_fields)
    
    try:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                # Nettoyage des données pour CSV
                cleaned = {k: str(v).replace('\n', ' ') if v is not None else '' 
                          for k, v in result.items()}
                writer.writerow(cleaned)
        
        return True
    except Exception as e:
        print(f"Erreur lors de l'export CSV : {str(e)}")
        return False