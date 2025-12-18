import requests,socket,tiktoken,re,shutil,time,os,mimetypes,logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from wordsegment import load, segment
logging.basicConfig(level=logging.INFO)

