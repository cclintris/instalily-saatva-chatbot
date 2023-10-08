import configparser
import requests
import re
import urllib.request
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urlparse
import os
import openai

################################################################################
######################## Settings and Configurations ###########################
################################################################################

# Regex pattern to match a URL
HTTP_URL_PATTERN = r'^https://www\.saatva\.com/(mattresses|furniture|bedding)/$ # only match the three categories'

# Load API key from key.ini
config = configparser.ConfigParser()
try:
    config.read('../key.ini')
except Exception as e:
    print("An error occurred:", e)

openai.api_key = config['openai']['api_key']
os.environ["OPENAI_API_KEY"] = config['openai']['api_key']

# Define root domain to crawl
domain = "saatva.com"
full_url = "https://www.saatva.com"


################################################################################
######################## Setting up a web crawler ##############################
################################################################################

# Create a class to parse the HTML and get the hyperlinks
class HyperlinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        # Create a list to store the hyperlinks
        self.hyperlinks = []

    # Override the HTMLParser's handle_starttag method to get the hyperlinks
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        # If the tag is an anchor tag and it has an href attribute, add the href attribute to the list of hyperlinks
        if tag == "a" and "href" in attrs:
            self.hyperlinks.append(attrs["href"])
            


# Function to get the hyperlinks from a URL
def get_hyperlinks(url):
    
    # Try to open the URL and read the HTML
    try:
        # Open the URL and read the HTML
        with urllib.request.urlopen(url) as response:

            # If the response is not HTML, return an empty list
            if not response.info().get('Content-Type').startswith("text/html"):
                return []
            
            # Decode the HTML
            html = response.read().decode('utf-8')
    except Exception as e:
        print(e)
        return []

    # Create the HTML Parser and then Parse the HTML to get hyperlinks
    parser = HyperlinkParser()
    parser.feed(html)

    return parser.hyperlinks



# Function to get the hyperlinks from a URL that are within the same domain
def get_domain_hyperlinks(local_domain, url):
    clean_links = []
    for link in set(get_hyperlinks(url)):
        clean_link = None

        # Skip the main domain
        if link == "https://" + local_domain or link == "https://" + local_domain + "/":
            continue

        # If the link is a URL, check if it is within the same domain
        if re.match(HTTP_URL_PATTERN, link):
            # Parse the URL and check if the domain is the same
            url_obj = urlparse(link)
            if url_obj.netloc == local_domain:
                clean_link = link

        # If the link is not a URL, check if it is a relative link
        else:
            if link.startswith("/"):
                clean_link = "https://" + local_domain + link

        if clean_link is not None:
            if clean_link.endswith("/"):
                clean_link = clean_link[:-1]
            clean_links.append(clean_link)

    return list(set(clean_links))



def crawl(url):
    # Parse the URL and get the domain
    local_domain = urlparse(url).netloc

    # Create a queue to store the URLs to crawl
    queue = deque([url])

    # Create a set to store the URLs that have already been seen (no duplicates)
    seen = set([url])

    # Create a directory to store the text files
    if not os.path.exists("text/"):
            os.mkdir("text/")

    if not os.path.exists("text/"+local_domain+"/"):
            os.mkdir("text/" + local_domain + "/")

    # While the queue is not empty, continue crawling
    while queue:

        # Get the next URL from the queue
        url = queue.pop()
        print(url) # for debugging and to see the progress
        
        # Try extracting the text from the link, if failed proceed with the next item in the queue
        try:
            # Save text from the url to a <url>.txt file
            with open('text/'+local_domain+'/'+url[8:].replace("/", "_") + ".txt", "w", encoding="UTF-8") as f:
                response = requests.get(url)
                response_as_string = str(response.content)  # Convert the entire Response object's content to a string
                clean_html_content = re.sub(r'<.*?>|function|var|return|for|while|if|else|document|window|class|style|[^\w\s.,!?;]', ' ', response_as_string)
                clean_html = re.sub(r'<.*?>', ' ', clean_html_content)
                js_keywords = r'\b(function|var|let|const|return|for|while|do|switch|case|break|continue|if|else|true|false|null|undefined)\b'
                clean_js = re.sub(js_keywords, ' ', clean_html)
                css_keywords = r'\b(style|color|background|border|margin|padding|font)\b'
                clean_css = re.sub(css_keywords, ' ', clean_js)
                clean_special_chars = re.sub(r'[^\w\s.,!?;]', ' ', clean_css)

                # Get the text but remove the tags
                text = str("WEBPAGE: "+ str(url)+ "\n")
                text = text + clean_special_chars

                # If the crawler gets to a page that requires JavaScript, it will stop the crawl
                if ("You need to enable JavaScript to run this app." in text):
                    print("Unable to parse page " + url + " due to JavaScript being required")
            
                # Otherwise, write the text to the file in the text directory
                f.write(text)
        except Exception as e:
            print("Unable to parse page " + url)
            print(e)

        # Get the hyperlinks from the URL and add them to the queue
        for link in get_domain_hyperlinks(local_domain, url):
            if link not in seen:
                queue.append(link)
                seen.add(link)          

crawl(full_url)
