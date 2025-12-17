#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import os
from pathlib import Path
import time
import random
import logging
import sys
import traceback
import base64
import re
from urllib.parse import urlparse, urljoin, urlunparse
from typing import Optional, Dict, Tuple, Union, List, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("url_fetcher")

# Define possible rendering methods
RENDER_METHOD_REQUESTS = "requests"  # Simple request, no JS execution
RENDER_METHOD_PLAYWRIGHT = "playwright"  # Full browser rendering with Playwright
RENDER_METHOD_SELENIUM = "selenium"  # Full browser rendering with Selenium

# Check if Playwright is installed
has_playwright = False
try:
    from playwright.sync_api import sync_playwright
    has_playwright = True
    logger.info("Playwright loaded successfully, full browser rendering supported")
except ImportError:
    logger.warning("Playwright not detected, full browser rendering unavailable. To use it, run: pip install playwright && playwright install chromium")

# Check if Selenium is installed
has_selenium = False
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    has_selenium = True
    logger.info("Selenium loaded successfully, full browser rendering supported")
except ImportError:
    logger.warning("Selenium not detected, browser rendering with this method unavailable. To use it, run: pip install selenium")

class UrlFetcher:
    """
    URL fetching and parsing utility class, responsible for retrieving HTML content from web URLs
    Supports multiple fetching methods: raw requests, Playwright, Selenium
    Can handle internal links and output static HTML files
    """
    
    def __init__(self, headers: Optional[Dict[str, str]] = None, timeout: int = 30, 
                 render_method: str = RENDER_METHOD_PLAYWRIGHT, wait_time: int = 5,
                 inline_resources: bool = True, max_resource_size: int = 5*1024*1024,
                 remove_scripts: bool = False, remove_images: bool = False):
        """
        Initialize the UrlFetcher class
        
        Args:
            headers: Request header dictionary, defaults to simulating a regular browser
            timeout: Request timeout in seconds, default 30 seconds
            render_method: Rendering method, possible values: "requests"(HTML only), "playwright"(default), "selenium"
            wait_time: Browser rendering wait time in seconds
            inline_resources: Whether to inline resources (CSS, JS, images, etc.)
            max_resource_size: Maximum inline resource size, default 5MB
            remove_scripts: Whether to remove all script tags, default False
            remove_images: Whether to remove all image tags, default False
        """
        self.timeout = timeout
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        }
        self.render_method = render_method
        self.wait_time = wait_time
        self.inline_resources = inline_resources
        self.max_resource_size = max_resource_size
        self.resource_cache = {}  # Cache for downloaded resources
        self.remove_scripts = remove_scripts
        self.remove_images = remove_images
        
        # Verify if the rendering method is available
        if self.render_method == RENDER_METHOD_PLAYWRIGHT and not has_playwright:
            logger.warning("Playwright not installed, falling back to requests method")
            self.render_method = RENDER_METHOD_SELENIUM if has_selenium else RENDER_METHOD_REQUESTS
            
        if self.render_method == RENDER_METHOD_SELENIUM and not has_selenium:
            logger.warning("Selenium not installed, falling back to requests method")
            self.render_method = RENDER_METHOD_REQUESTS
    
    def _fetch_with_requests(self, url: str) -> Tuple[Union[bytes, None], int]:
        """Fetch URL content using requests library (doesn't execute JavaScript)"""
        try:
            logger.info(f"Fetching URL with requests: {url}")
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            status_code = response.status_code
            
            if status_code == 200:
                # Use raw binary content to avoid encoding issues
                html_content = response.content
                return html_content, status_code
            else:
                logger.warning(f"Failed to fetch URL with requests: {url}, status code: {status_code}")
                return None, status_code
        except requests.RequestException as e:
            logger.error(f"Requests exception: {url}, error: {str(e)}")
            return None, 0
        except Exception as e:
            logger.error(f"Requests parsing exception: {url}, error: {str(e)}")
            return None, 0
    
    def _fetch_with_playwright(self, url: str) -> Tuple[Union[str, None], Union[str, None], int]:
        """Fetch URL content using Playwright (full browser rendering, executes JavaScript)"""
        if not has_playwright:
            logger.error("Playwright not installed, cannot use this method")
            return None, None, 0
        
        try:
            logger.info(f"Fetching URL with Playwright: {url}")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent=self.headers.get("User-Agent")
                )
                
                page = context.new_page()
                
                # Add additional request headers
                page.set_extra_http_headers(self.headers)
                
                # Visit page and wait for loading
                response = page.goto(url, timeout=self.timeout * 1000, wait_until="networkidle")
                status_code = response.status if response else 0
                
                if not response or status_code != 200:
                    browser.close()
                    logger.warning(f"Playwright failed to fetch URL: {url}, status code: {status_code}")
                    return None, None, status_code
                
                # Wait for page rendering to complete
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(self.wait_time * 1000)  # Additional wait to ensure JS execution
                
                # Get page title
                title = page.title()
                
                # Get rendered HTML content
                html_content = page.content()
                
                # Extract rendered text content
                text_content = page.evaluate("""() => {
                    return document.body.innerText;
                }""")
                
                # Clean up resources
                browser.close()
                
                return html_content, text_content, status_code
        except Exception as e:
            logger.error(f"Playwright fetch exception: {url}, error: {str(e)}")
            traceback.print_exc()
            return None, None, 0
    
    def _fetch_with_selenium(self, url: str) -> Tuple[Union[str, None], Union[str, None], int]:
        """Fetch URL content using Selenium (full browser rendering, executes JavaScript)"""
        if not has_selenium:
            logger.error("Selenium not installed, cannot use this method")
            return None, None, 0
        
        driver = None
        try:
            logger.info(f"Fetching URL with Selenium: {url}")
            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"user-agent={self.headers.get('User-Agent')}")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Start browser
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(self.timeout)
            
            # Visit page
            driver.get(url)
            
            # Wait for page to load
            time.sleep(self.wait_time)  # Wait for JavaScript execution
            
            # Get page title
            title = driver.title
            
            # Get rendered HTML
            html_content = driver.page_source
            
            # Get text content
            text_content = driver.find_element(By.TAG_NAME, "body").text
            
            # Assume successful fetch (Selenium doesn't provide status code)
            return html_content, text_content, 200
        except TimeoutException:
            logger.error(f"Selenium load timeout: {url}")
            return None, None, 408  # Request timeout
        except WebDriverException as e:
            logger.error(f"Selenium browser exception: {url}, error: {str(e)}")
            return None, None, 0
        except Exception as e:
            logger.error(f"Selenium fetch exception: {url}, error: {str(e)}")
            traceback.print_exc()
            return None, None, 0
        finally:
            # Clean up resources
            if driver:
                driver.quit()

    def _get_resource(self, resource_url: str, base_url: str) -> Tuple[Union[str, None], str, str]:
        """
        Fetch resource content and convert it to Data URL or relative path
        
        Args:
            resource_url: Resource URL
            base_url: Base URL for resolving relative URLs
            
        Returns:
            tuple: (resource content, content type, Data URL or original URL)
        """
        # Check cache
        if resource_url in self.resource_cache:
            return self.resource_cache[resource_url]
            
        try:
            # Parse resource URL
            parsed_resource_url = urlparse(resource_url)
            
            # Convert to absolute URL if it's a relative URL
            if not parsed_resource_url.netloc:
                absolute_url = urljoin(base_url, resource_url)
                parsed_resource_url = urlparse(absolute_url)
            else:
                absolute_url = resource_url
            
            # Skip data URLs, javascript URLs and anchors
            if (parsed_resource_url.scheme in ['data', 'javascript'] or 
                not parsed_resource_url.netloc or
                resource_url.startswith('#')):
                return None, "", resource_url
            
            # Fetch resource content
            try:
                response = requests.get(
                    absolute_url, 
                    headers=self.headers, 
                    timeout=self.timeout,
                    stream=True  # Use streaming to avoid loading large files at once
                )
                
                # Ensure UTF-8 encoding for text resources
                response.encoding = 'utf-8'
                
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch resource: {absolute_url}, status code: {response.status_code}")
                    return None, "", resource_url
                
                # Get content type
                content_type = response.headers.get('content-type', '').split(';')[0]
                if not content_type:
                    # Guess content type based on URL suffix
                    extension = os.path.splitext(parsed_resource_url.path)[1].lower()
                    content_type = {
                        '.css': 'text/css',
                        '.js': 'application/javascript',
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg',
                        '.png': 'image/png',
                        '.gif': 'image/gif',
                        '.svg': 'image/svg+xml',
                        '.webp': 'image/webp',
                        '.ttf': 'font/ttf',
                        '.woff': 'font/woff',
                        '.woff2': 'font/woff2',
                        '.eot': 'font/eot',
                    }.get(extension, 'application/octet-stream')
                
                # Check resource size
                content_length = int(response.headers.get('content-length', 0))
                if content_length and content_length > self.max_resource_size:
                    logger.warning(f"Resource too large: {absolute_url}, size: {content_length} bytes")
                    return None, content_type, resource_url
                
                # Get resource content
                content = response.content
                
                # Check size again (in case content-length is inaccurate)
                if len(content) > self.max_resource_size:
                    logger.warning(f"Resource too large: {absolute_url}, size: {len(content)} bytes")
                    return None, content_type, resource_url
                
                # Create Base64 encoded Data URL
                data_url = f"data:{content_type};base64,{base64.b64encode(content).decode('utf-8')}"
                
                # Cache result
                result = (content, content_type, data_url)
                self.resource_cache[resource_url] = result
                return result
            
            except requests.RequestException as e:
                logger.error(f"Error requesting resource: {absolute_url}, error: {str(e)}")
                return None, "", resource_url
                
        except Exception as e:
            logger.error(f"Error processing resource URL: {resource_url}, error: {str(e)}")
            return None, "", resource_url
    
    def _staticize_html(self, html_content: str, base_url: str) -> str:
        """
        Inline external resources in HTML to convert to fully static HTML
        Can remove all scripts and images based on configuration
        
        Args:
            html_content: HTML content
            base_url: Base URL for resolving relative URLs
            
        Returns:
            Processed HTML content
        """
        logger.info(f"Starting HTML staticization process, base URL: {base_url}")
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            processed_urls = set()  # Track processed URLs to avoid duplicates
            
            # 1. Remove all script tags based on configuration
            if self.remove_scripts:
                logger.info("Removing all script tags...")
                # Remove all script tags
                scripts_removed = 0
                for script in soup.find_all('script'):
                    script.extract()  # Remove element from DOM
                    scripts_removed += 1
                
                # Remove element attributes that may contain javascript
                js_attrs = ['onclick', 'onload', 'onunload', 'onchange', 'onsubmit', 
                           'onreset', 'onselect', 'onblur', 'onfocus', 'onkeydown', 
                           'onkeypress', 'onkeyup', 'onmouseover', 'onmouseout', 
                           'onmousedown', 'onmouseup', 'onmousemove', 'ondblclick']
                
                attrs_removed = 0
                for attr in js_attrs:
                    for tag in soup.find_all(attrs={attr: True}):
                        del tag[attr]
                        attrs_removed += 1
                
                # Remove href attributes with javascript:
                js_hrefs_removed = 0
                for a in soup.find_all('a', href=True):
                    if a['href'].startswith('javascript:'):
                        a['href'] = '#'
                        js_hrefs_removed += 1
                
                logger.info(f"Removed {scripts_removed} script tags, {attrs_removed} event attributes, {js_hrefs_removed} javascript links")
            
            # 2. Remove all image tags based on configuration
            if self.remove_images:
                logger.info("Removing all images and media tags...")
                # Remove all image tags
                images_removed = 0
                for img in soup.find_all('img'):
                    img.extract()
                    images_removed += 1
                
                # Remove background image styles
                style_attrs_updated = 0
                for tag in soup.find_all(style=True):
                    if 'background' in tag['style'] and ('url(' in tag['style'] or 'image' in tag['style']):
                        # Remove background image but keep other styles
                        style = tag['style']
                        style = re.sub(r'background-image\s*:[^;]+;?', '', style)
                        style = re.sub(r'background\s*:[^;]*url\([^)]+\)[^;]*;?', '', style)
                        tag['style'] = style
                        style_attrs_updated += 1
                
                # Remove other media elements
                media_removed = 0
                for media in soup.find_all(['video', 'audio', 'picture', 'svg', 'canvas', 'iframe']):
                    media.extract()
                    media_removed += 1
                
                logger.info(f"Removed {images_removed} images, {style_attrs_updated} background image styles, {media_removed} other media elements")
            
            # 3. Inline resource processing (if enabled)
            if self.inline_resources:
                # Process CSS links
                for link in soup.find_all('link', rel='stylesheet'):
                    href = link.get('href')
                    if href and href not in processed_urls:
                        processed_urls.add(href)
                        content, content_type, data_url = self._get_resource(href, base_url)
                        if content:
                            # Replace with inline style
                            style_tag = soup.new_tag('style')
                            style_tag['type'] = 'text/css'
                            style_tag.string = content.decode('utf-8', errors='ignore')
                            link.replace_with(style_tag)
                        elif data_url and data_url.startswith('data:'):
                            # Replace with Data URL
                            link['href'] = data_url
                
                # Process URLs in inline styles
                for style in soup.find_all('style'):
                    if style.string:
                        # Process url() references in CSS
                        style.string = re.sub(
                            r'url\(["\']?([^"\'()]+)["\']?\)',
                            lambda m: self._process_css_url(m, base_url, processed_urls),
                            style.string
                        )
                
                # Process URLs in element inline styles
                for tag in soup.find_all(style=True):
                    style_attr = tag['style']
                    if 'url(' in style_attr:
                        tag['style'] = re.sub(
                            r'url\(["\']?([^"\'()]+)["\']?\)',
                            lambda m: self._process_css_url(m, base_url, processed_urls),
                            style_attr
                        )
                
                # Process JavaScript (only if not configured to remove all scripts)
                if not self.remove_scripts:
                    for script in soup.find_all('script', src=True):
                        src = script.get('src')
                        if src and src not in processed_urls:
                            processed_urls.add(src)
                            content, content_type, data_url = self._get_resource(src, base_url)
                            if content:
                                # Replace with inline script
                                script_content = content.decode('utf-8', errors='ignore')
                                del script['src']
                                script.string = script_content
                            elif data_url and data_url.startswith('data:'):
                                # Replace with Data URL
                                script['src'] = data_url
                
                # Process images (only if not configured to remove all images)
                if not self.remove_images:
                    for img in soup.find_all('img', src=True):
                        src = img.get('src')
                        if src and src not in processed_urls:
                            processed_urls.add(src)
                            content, content_type, data_url = self._get_resource(src, base_url)
                            if data_url and data_url.startswith('data:'):
                                img['src'] = data_url
                
                # Process video and audio sources (if media is allowed to remain)
                if not self.remove_images:
                    for media in soup.find_all(['video', 'audio']):
                        for source in media.find_all('source', src=True):
                            src = source.get('src')
                            if src and src not in processed_urls:
                                processed_urls.add(src)
                                content, content_type, data_url = self._get_resource(src, base_url)
                                if data_url and data_url.startswith('data:'):
                                    source['src'] = data_url
            
            # Process links to make all links absolute URLs
            for a in soup.find_all('a', href=True):
                href = a.get('href')
                if href and not href.startswith(('javascript:', '#', 'data:', 'mailto:', 'tel:')):
                    # Convert relative URL to absolute URL
                    a['href'] = urljoin(base_url, href)
            
            # Process form actions
            for form in soup.find_all('form', action=True):
                action = form.get('action')
                if action and not action.startswith(('javascript:', '#', 'data:')):
                    form['action'] = urljoin(base_url, action)
            
            # Add base tag to ensure all relative URLs are based on the correct base URL
            head = soup.head or soup.html.insert(0, soup.new_tag('head'))
            existing_base = soup.find('base')
            if existing_base:
                existing_base['href'] = base_url
            else:
                base_tag = soup.new_tag('base')
                base_tag['href'] = base_url
                head.insert(0, base_tag)
            
            # Add meta tag indicating this is a statically processed page
            meta_tag = soup.new_tag('meta')
            meta_tag['name'] = 'static-page-generator'
            meta_tag['content'] = 'UrlFetcher'
            head.append(meta_tag)
            
            logger.info(f"HTML staticization completed, processed {len(processed_urls)} resources")
            return str(soup)
            
        except Exception as e:
            logger.error(f"Error staticizing HTML: {str(e)}")
            traceback.print_exc()
            # Return original HTML on error
            return html_content
    
    def _process_css_url(self, match, base_url: str, processed_urls: Set[str]) -> str:
        """Process url() references in CSS"""
        url = match.group(1)
        if url in processed_urls or url.startswith(('data:', 'javascript:', '#')):
            return f'url("{url}")'
        
        processed_urls.add(url)
        content, content_type, data_url = self._get_resource(url, base_url)
        if data_url and data_url.startswith('data:'):
            return f'url("{data_url}")'
        return f'url("{url}")'
    
    def fetch_url(self, url: str) -> Tuple[Union[bytes, None], Union[str, None], Union[str, None], int]:
        """
        Fetch HTML content and rendered text from URL, and process internal links to make fully static
        
        Args:
            url: URL to fetch
            
        Returns:
            tuple: (static HTML content (binary), text content, page title, status code)
                If fetch fails, HTML content is None
        """
        try:
            logger.info(f"Fetching URL: {url}, using rendering method: {self.render_method}")
            
            # Select different fetching methods based on rendering method
            if self.render_method == RENDER_METHOD_PLAYWRIGHT:
                html_content, text_content, status_code = self._fetch_with_playwright(url)
                
                # Extract title using BeautifulSoup
                if html_content:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    title_tag = soup.find('title')
                    title = title_tag.text if title_tag else url
                else:
                    title = url
                    
            elif self.render_method == RENDER_METHOD_SELENIUM:
                html_content, text_content, status_code = self._fetch_with_selenium(url)
                
                # Extract title using BeautifulSoup
                if html_content:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    title_tag = soup.find('title')
                    title = title_tag.text if title_tag else url
                else:
                    title = url
                    
            else:  # Use requests by default
                html_content, status_code = self._fetch_with_requests(url)
                
                # Extract title and text using BeautifulSoup
                if html_content:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    title_tag = soup.find('title')
                    title = title_tag.text if title_tag else url
                    # Extract text content
                    text_content = soup.get_text(separator='\n', strip=True)
                else:
                    title = url
                    text_content = None
            
            # If fetch failed
            if html_content is None:
                logger.warning(f"Failed to fetch URL: {url}, status code: {status_code}")
                return None, None, url, status_code
            
            # For binary content, return directly without static conversion
            # Check if it's binary data
            if isinstance(html_content, bytes):
                try:
                    # Try to detect encoding
                    import chardet
                    detected = chardet.detect(html_content)
                    logger.info(f"Detected content encoding: {detected}")
                    
                    # If it looks like a binary file rather than text, return binary content directly
                    if detected['encoding'] is None or detected['confidence'] < 0.5:
                        logger.info(f"Detected possible binary file, returning binary content directly")
                        return html_content, text_content, title, status_code
                    
                    # Try to decode to text for static processing
                    text_html = html_content.decode(detected['encoding'], errors='replace')
                    static_html = self._staticize_html(text_html, url)
                    # Convert back to binary
                    return static_html.encode(detected['encoding'], errors='replace'), text_content, title, status_code
                except Exception as e:
                    logger.warning(f"Encoding processing failed, returning original binary data: {str(e)}")
                    return html_content, text_content, title, status_code
            else:
                # Process text content
                static_html = self._staticize_html(html_content, url)
                logger.info(f"Successfully fetched URL: {url}, title: {title}")
                return static_html, text_content, title, status_code
            
        except Exception as e:
            logger.error(f"Error fetching URL: {url}, error: {str(e)}")
            traceback.print_exc()
            return None, None, url, 0
    
    def save_html_to_file(self, html_content: Union[str, bytes], output_path: Union[str, Path]) -> Path:
        """
        Save HTML content to file
        
        Args:
            html_content: HTML content (string or bytes)
            output_path: Path to save the file
            
        Returns:
            Saved file path
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Choose correct saving method based on content type
        if isinstance(html_content, bytes):
            # Binary content
            with open(output_path, 'wb') as f:
                f.write(html_content)
        else:
            # Text content
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            except UnicodeEncodeError:
                # If encoding fails, try writing in binary mode
                with open(output_path, 'wb') as f:
                    f.write(html_content.encode('utf-8', errors='replace'))
        
        logger.info(f"Content saved to: {output_path}")
        return output_path
        
    def save_text_to_file(self, text_content: Union[str, bytes, None], output_path: Union[str, Path]) -> Path:
        """
        Save text content to file
        
        Args:
            text_content: Text content (string, bytes, or None)
            output_path: Path to save the file
            
        Returns:
            Saved file path
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # If content is empty
        if text_content is None:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("Unable to extract text content")
            return output_path
            
        # Handle different types of content
        if isinstance(text_content, bytes):
            try:
                # Try to detect encoding
                import chardet
                detected = chardet.detect(text_content)
                if detected['encoding'] is None:
                    # Binary file, save directly
                    with open(output_path, 'wb') as f:
                        f.write(text_content)
                else:
                    # Try to decode text
                    with open(output_path, 'w', encoding=detected['encoding'], errors='replace') as f:
                        f.write(text_content.decode(detected['encoding'], errors='replace'))
            except Exception:
                # If decoding fails, save directly in binary mode
                with open(output_path, 'wb') as f:
                    f.write(text_content)
        else:
            # Text content
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
        
        logger.info(f"Text content saved to: {output_path}")
        return output_path

def fetch_and_save_url(url: str, output_dir: Union[str, Path], 
                       filename: Optional[str] = None, 
                       render_method: str = RENDER_METHOD_PLAYWRIGHT,
                       wait_time: int = 5,
                       inline_resources: bool = True) -> Tuple[Union[Dict, None], str, int]:
    """
    Fetch URL content and save as static HTML and text files
    
    Args:
        url: URL to fetch
        output_dir: Output directory
        filename: Filename to save, auto-generated from URL if not provided
        render_method: Rendering method, possible values: "requests", "playwright", "selenium"
        wait_time: Browser rendering wait time in seconds
        inline_resources: Whether to inline resources (CSS, JS, images, etc.)
        
    Returns:
        tuple: (Saved file information dictionary, page title, status code)
            Returns (None, title, status code) if fetch fails
    """
    # Select appropriate rendering method
    if render_method == RENDER_METHOD_PLAYWRIGHT and not has_playwright:
        logger.warning("Playwright not installed, falling back to Selenium")
        render_method = RENDER_METHOD_SELENIUM if has_selenium else RENDER_METHOD_REQUESTS
    
    if render_method == RENDER_METHOD_SELENIUM and not has_selenium:
        logger.warning("Selenium not installed, falling back to requests")
        render_method = RENDER_METHOD_REQUESTS
    
    # Create URL fetcher
    fetcher = UrlFetcher(render_method=render_method, wait_time=wait_time, inline_resources=inline_resources)
    
    # Fetch URL content
    html_content, text_content, title, status_code = fetcher.fetch_url(url)
    
    if html_content is None:
        return None, title or url, status_code
    
    # Generate filename from URL if not provided
    if filename is None:
        # Extract domain from URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Generate filename: domain-timestamp.html
        timestamp = int(time.time())
        random_id = random.randint(1000, 9999)
        filename = f"{domain}-{timestamp}-{random_id}"
    
    # Ensure output directory exists
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save HTML content
    html_filename = f"{filename}.html"
    html_path = output_dir / html_filename
    saved_html_path = fetcher.save_html_to_file(html_content, html_path)
    
    # No longer saving text content
    # text_filename = f"{filename}.txt"
    # text_path = output_dir / text_filename
    # saved_text_path = fetcher.save_text_to_file(text_content, text_path)
    
    return {
        "html_path": str(saved_html_path),
        # "text_path": str(saved_text_path),  # Remove text path
        "title": title,
        "url": url,
        "render_method": render_method
    }, title, status_code

def install_dependencies():
    """Install dependency libraries"""
    try:
        import subprocess
        
        # Install basic dependencies
        subprocess.run([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4", "lxml"], check=True)
        
        # Install browser automation dependencies
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
            subprocess.run(["playwright", "install", "chromium"], check=True)
            print("Playwright installed successfully!")
        except Exception as e:
            print(f"Failed to install Playwright: {str(e)}")
            
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "selenium"], check=True)
            print("Selenium installed successfully!")
        except Exception as e:
            print(f"Failed to install Selenium: {str(e)}")
            
        print("All dependencies installed!")
        return True
    except Exception as e:
        print(f"Error installing dependencies: {str(e)}")
        return False

if __name__ == "__main__":
    # Simple test
    url = "https://www.example.com"
    output_dir = "./test_output"
    
    # Install dependencies if necessary
    if not has_playwright and not has_selenium:
        print("No browser rendering libraries detected, attempting installation...")
        install_dependencies()
    
    # Test different rendering methods
    render_methods = [m for m in [RENDER_METHOD_PLAYWRIGHT if has_playwright else None,
                                 RENDER_METHOD_SELENIUM if has_selenium else None,
                                 RENDER_METHOD_REQUESTS] if m]
    
    for method in render_methods:
        print(f"\nTesting {method} rendering method:")
        result, title, status = fetch_and_save_url(url, output_dir, render_method=method)
        
        if result:
            print(f"Title: {title}")
            print(f"HTML file: {result['html_path']}")
            # No longer output text file path since we're not saving text files anymore
        else:
            print(f"Fetch failed: {status}")