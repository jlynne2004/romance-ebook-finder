#!/usr/bin/env python3
"""
Romance Ebook Blog Generator
A script to find free romance ebooks with subgenres for weekly blog posts
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import csv
from datetime import datetime, timedelta
from urllib.parse import urljoin, quote
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RomanceBlogGenerator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.books = []
        
        # Romance subgenre keywords for classification
        self.subgenre_keywords = {
            'Historical Romance': ['historical', 'victorian', 'medieval', 'highlander', 'edwardian', 'wwii', 'star-crossed'],
            'Pirate Romance': ['pirate', 'pirates'],
            'Paranormal Romance': ['paranormal', 'vampire', 'werewolf', 'ghost', 'supernatural', 'shifter', 'demon', 'witch', 'magic', 'sorcery', 'star-crossed', 'alpha', 'beta', 'omega', 'pack'],
            'Fantasy Romance': ['fantasy', 'dragon', 'elf', 'magic', 'sorcery', 'sorcerer','kingdom', 'mythical', 'realm', 'witch', 'ghost', 'enchantress', 'galaxy', 'alien', 'star-crossed'],
            'Romantic Suspense': ['romantic suspense', 'suspense', 'thriller', 'mystery', 'crime', 'detective', 'spy', 'FBI', 'star-crossed'],
            'Erotic Romance': ['erotic', 'spicy', 'bdsm', 'dominant', 'submissive', 'high heat', 'explicit', 'taboo', 'dark desires'],
            'Young Adult Romance': ['ya romance', 'young adult', 'teen', 'high school', 'college', 'coming of age'],
            'LGBTQ+ Romance': ['lgbtq', 'gay', 'lesbian', 'bisexual', 'transgender', 'trans', 'queer', 'pansexual', 'asexual', 'non-binary', 'gender fluid', 'mm romance', 'ff romance', 'star-crossed'],
            'Small Town Romance': ['small town', 'rural', 'hometown', 'homecoming', 'countryside', 'close-knit community'],
            'Second Chance Romance': ['second chance', 'reunion', 'rekindled', 'lost love', 'old flame', 'ex-lovers'],
            'Billionaire Romance': ['billionaire', 'wealthy', 'rich', 'tycoon', 'CEO', 'heir'],
            'Cowboy Romance': ['western', 'cowboy', 'ranch', 'rodeo', 'country romance', 'frontier'],
            'Military Romance': ['military', 'soldier', 'marine', 'navy', 'air force', 'veteran', 'army', 'seal', 'special forces'],
            'MC Romance': ['motorcycle club', 'biker', 'mc', 'outlaw', 'patch', 'ride or die', 'bad boy'],
            'Sports Romance': ['sports', 'athlete', 'football', 'basketball', 'hockey', 'baseball', 'soccer', 'tennis', 'golf', 'mma', 'wrestling', 'boxing', 'coach', 'team'],
            'Rock Star Romance': ['rock star', 'musician', 'band', 'singer', 'guitarist', 'drummer', 'rock and roll', 'pop star', 'tour', 'music'],
            'Time Travel Romance': ['time travel', 'time travel romance', 'historical time travel', 'future', 'past'],
            'Sci-Fi Romance': ['sci-fi', 'science fiction', 'space', 'cyberpunk', 'alien', 'robot', 'android', 'cyborg', 'galaxy', 'starship', 'interplanetary', 'star-crossed'],
            'Royal Romance': ['royal', 'prince', 'princess', 'king', 'queen', 'duke', 'duchess', 'monarchy', 'crown', 'court', 'castle', 'heir', 'star-crossed'],
            'Inspirational Romance': ['inspirational', 'faith', 'religious', 'christian', 'spiritual', 'uplifting', 'hopeful'],
            'Sweet Romance': ['sweet', 'heartwarming', 'feel-good', 'low heat', 'hospital', 'nurse'],
            'Clean Romance': ['clean', 'wholesome', 'family-friendly', 'no explicit content'],
            'Holiday Romance': ['holiday', 'christmas', 'valentine', 'new year', 'thanksgiving', 'halloween', 'festive', 'seasonal', 'hannukah', 'easter'],
            'Medical Romance': ['medical', 'doctor', 'nurse', 'hospital', 'healthcare', 'surgeon', 'paramedic', 'first responder'],
            'Urban Fantasy Romance': ['urban fantasy', 'supernatural city', 'magical realism'],
            'Dystopian Romance': ['dystopian', 'post-apocalyptic', 'survival', 'rebellion', 'totalitarian', 'futuristic society', 'stranded'],
            'Regency Romance': ['regency', 'georgian', 'jane austen', 'ballroom', 'dukes', 'earls', 'ladies', 'gentlemen', 'highlander', 'wallflower', 'spinster'],
            'Urban Romance': ['urban', 'city life', 'metropolitan', 'cityscape'],
            'Adventure Romance': ['adventure', 'exploration', 'quest', 'journey', 'expedition', 'discovery', 'explorer'],
            'Romantic Comedy': ['romantic comedy', 'romcom', 'humor', 'funny', 'light-hearted', 'comedic', 'laugh-out-loud'],
            'Interracial Romance': ['interracial', 'multicultural', 'cross-cultural', 'diverse', 'Black romance', 'Asian romance', 'Latinx romance', 'BWWM', 'BBW', 'MM interracial', 'FF interracial'],
            'Amish Romance': ['Amish', 'mennonite', 'rumspringa'],
            'Taboo Romance': ['taboo', 'forbidden', 'illicit', 'scandalous', 'controversial', 'prohibited'],
            'Mythological Romance': ['mythological', 'gods', 'goddesses', 'myths', 'legends', 'ancient tales', 'greek mythology', 'norse mythology'],
            'Disability Romance': ['disability romance', 'disabled', 'differently-abled', 'accessible romance', 'inclusion', 'adaptive'],
            'Single Dad Romance': ['single dad romance', 'fatherhood', 'dad life', 'father figure', 'dad hero'],
            'Single Mom Romance': ['single mom romance', 'motherhood', 'mom life', 'mother figure', 'mom hero'],
            'Celebrity Romance': ['celebrity romance', 'famous', 'star-crossed', 'public figure', 'fame', 'glamour', 'rock star', 'pop star', 'actor', 'actress', 'musician'],
            'Survival Romance': ['survival', 'stranded', 'endurance', 'resilience', 'overcoming adversity'],
            'Bully Romance': ['bully romance', 'bullying', 'toxic romance', 'abusive relationship', 'power dynamics'],
        }

        self.tropes_keywords = {
            'Enemies to Lovers': ['enemies to lovers', 'hate to love', 'rivals', 'bickering', 'feuding', 'antagonistic', 'jerk'],
            'Friends to Lovers': ['friends to lovers', 'best friends', 'friends first', 'bff', 'friend zone'],
            'Forbidden Love': ['forbidden love', 'secret love', 'secret relationship', 'illicit', 'off-limits', 'secret affair', 'forbidden attraction'],
            'Fake Relationship': ['fake relationship', 'pretend boyfriend', 'pretend girlfriend', 'fake dating', 'fake couple', 'fauxmance', 'publicity stunt', 'staged romance', 'pretend romance', 'contract marriage'],
            'Marriage of Convenience': ['marriage of convenience', 'arranged marriage', 'contract marriage', 'business arrangement', 'wedding of convenience'],
            'Single Parent': ['single parent', 'widowed', 'divorced', 'co-parenting', 'blended family'],
            'Opposites Attract': ['opposites attract', 'polar opposites', 'different worlds', 'clash of personalities', 'clashing', 'unlikely pair', 'grumpy sunshine', 'grumpy hero', 'sunshine heroine', 'grumpy heroine', 'sunshine heroine'],
            'Grumpy/Sunshine': ['grumpy sunshine', 'grumpy hero', 'sunshine heroine', 'grump', 'sunshine', 'curmudgeon', 'optimist'],
            'Love Triangle': ['love triangle', 'torn between', 'caught in the middle', 'two suitors', 'competing love interests'],
            'Reunited Lovers': ['reunited lovers', 'old flames', 'rekindled romance', 'past lovers'],
            'Reverse Grumpy/Sunshine': ['grumpy heroine', 'sunshine hero'],
            'Slow Burn': ['slow burn', 'slow build', 'tension', 'builds over time', 'lingering looks'],
            'Workplace Romance': ['workplace romance', 'office romance', 'co-workers', 'boss/employee', 'forbidden office romance', 'ceo'],
            'Amnesia': ['amnesia', 'memory loss', 'forgotten past', 'lost memories', 'recovery of memory'],
            'Secret Identity': ['secret identity', 'hidden past', 'double life', 'undercover', 'hidden identity'],
            'Redemption Arc': ['redemption arc', 'forgiveness', 'healing', 'personal growth', 'overcoming past mistakes'],
            'Bodyguard Romance': ['bodyguard romance', 'bodyguard', 'guardian', 'protector'],
            'Protector Romance': ['protector romance', 'bodyguard','guardian', 'savior', 'defender', 'shield', 'safety', 'security', 'protective hero', 'protective heroine'],
            'Forced Proximity': ['forced proximity', 'stuck together', 'close quarters', 'unavoidable closeness', 'trapped together'],
            'Accidental Pregnancy': ['accidental pregnancy', 'unexpected pregnancy', 'unplanned parenthood', 'surprise pregnancy', 'unintended pregnancy', 'secret baby'],
            'Insta-Love': ['insta-love', 'love at first sight', 'instant attraction', 'immediate chemistry', 'quick connection', 'instant connection'],
            'Reverse Harem / Why Choose': ['reverse harem', 'why choose', 'multiple love interests', 'polyamorous', 'harem romance', 'shared love', 'poly romance'],
            'Age Gap': ['age gap', 'older man', 'younger woman', 'younger man', 'older woman', 'significant age difference'],
            "Best Friend's Sibling": ["best friend's sibling", "brother of best friend", "sister of best friend", "friend's sibling", "sibling of best friend"],
            "Sibling's Best Friend": ["sibling's best friend", "brother's best friend", "sister's best friend"],
            'Marriage Pact': ['marriage pact', 'promise of marriage', 'vow', 'commitment', 'binding agreement', 'marriage agreement'],
            'Unrequited Love': ['unrequited love', 'one-sided love', 'pining', 'longing', 'unreciprocated feelings'],
            'Mistaken Identity': ['mistaken identity', 'identity swap', 'case of mistaken identity', 'wrong person', 'identity confusion'],
            'Found Family': ['found family', 'chosen family', 'community', 'support system', 'bonded by circumstance', 'family of choice'],
            'Road Trip Romance': ['road trip romance', 'traveling together', 'journey', 'adventure on the road', 'car trip', 'voyage'],
            'Secret Baby': ['secret baby', 'hidden pregnancy', 'surprise baby', 'unacknowledged child', 'love child', 'surprise pregnancy'],
            'Alpha/Beta/Omega Dynamics': ['alpha', 'beta', 'omega', 'shifter dynamics', 'pack hierarchy', 'werewolf dynamics'],
            'Billionaire/CEO': ['billionaire', 'CEO', 'wealthy hero', 'rich heroine', 'business tycoon', 'corporate romance', 'boss/employee'],
            'Royalty/Aristocracy': ['royalty', 'aristocracy', 'nobility', 'prince/princess', 'duke/duchess', 'king/queen'],
            'Marriage in Trouble': ['marriage in trouble', 'relationship crisis', 'marital issues', 'couples therapy', 'struggling marriage'],
            'Alphahole Hero': ['alphahole hero', 'alphahole', 'jerk', 'jerk with a heart of gold'],
            'Bad Boy Hero': ['bad boy', 'rebel', 'troublemaker', 'anti-hero', 'delinquent', 'jerk', 'alphahole', 'dominant'],
            'Playboy': ['playboy', 'womanizer', 'player', 'flirt', 'charmer', 'commitment issues'],
            'Cheating': ['cheating', 'infidelity', 'betrayal', 'unfaithful', 'adultery', 'love affair'],
            'Strong Heroine': ['strong heroine', 'independent woman', 'resilient heroine', 'fierce heroine', 'badass heroine'],
            'Bullying': ['bullying', 'bully romance', 'enemies to lovers', 'antagonistic relationship', 'abusive relationship'],
        }

        self.content_warning_keywords = {
            'Cheating/Infidelity': ['cheating', 'infidelity', 'adultery', 'betrayal', 'unfaithful', 'affair'],
            'Abuse/Domestic Violence': ['abuse', 'domestic violence', 'abusive relationship', 'toxic relationship', 'controlling partner'],
            'Bullying/Trauma': ['bullying', 'trauma', 'verbal abuse', 'bullies', 'mean girl'],
            'Death of Loved One': ['death', 'grief', 'loss', 'bereavement', 'mourning', 'widow', 'widower', 'passed away', 'tragic loss'],
            'Mental Health Issues': ['mental health', 'depression', 'anxiety', 'bipolar', 'schizophrenia', 'mental illness', 'anxiety attacks', 'anxiety disorder', 'panic attacks', 'therapy'],
            'Substance Abuse': ['substance abuse', 'addiction', 'alcoholism', 'drug abuse', 'rehab', 'alcoholic', 'alcohol abuse', 'recovery', 'sobriety'],
            'Sexual Assault / Rape': ['sexual assault', 'rape', 'sexual violence', 'consent'],
            'Toxic Relationships': ['toxic relationship', 'manipulation', 'gaslighting', 'controlling partner', 'emotional abuse', 'narcissistic', 'toxic', 'emotional abuse'],
            'Non-Consensual Content': ['non-consensual', 'forced', 'reluctant', 'lack of consent', 'dubious consent', 'dubcon'],
            'Dark Romance': ['dark romance', 'dark themes', 'morally gray characters', 'possessive', 'obsessive', 'stalker', 'captor', 'dangerous man'],
            'Graphic Violence': ['graphic violence', 'gore', 'gory', 'bloodshed', 'graphic content', 'brutal', 'torture', 'blood'],
            'BDSM/Kink': ['bdsm', 'kink', 'bondage', 'dominant', 'submissive', 'kinky', 'fetish', 'power exchange', 'consensual non-consent'],
            'Crime/Mafia Content': ['crime', 'mafia', 'gangster', 'hitman', 'organized crime', 'criminal underworld', 'mob', 'cartel', 'gang', 'underworld'],
            'Religious/Cult Themes': ['religious', 'cult', 'religious themes', 'faith-based', 'spiritual abuse', 'religious trauma'],
            'Body Shaming/Fatphobia': ['body shaming', 'fatphobia', 'weight stigma', 'body image issues', 'fat shaming'],
            'Racism/Discrimination': ['racism', 'discrimination', 'prejudice', 'bigotry', 'racial slurs', 'xenophobia', 'homophobia', 'transphobia', 'ableism'],
            'Love Triangle': ['love triangle', 'jealousy', 'multiple suitors', 'competing love interests', 'torn between two lovers'],
            'Cliffhanger Ending': ['cliffhanger', 'unfinished story', 'not a standalone', 'to be continued', 'unresolved plot', 'series continuation'],
            'Graphic Sexual Content': ['graphic sexual content', 'explicit', 'sexual scenes', 'steamy', 'spicy', 'high heat', 'sexual situations', 'sexual encounters'],
            'Age Gap': ['age gap', 'older man', 'younger woman', 'younger man', 'older woman', 'significant age difference', 'student/teacher', 'mentor/mentee'],
            'Open Relationship / Polyamory': ['open relationship', 'polyamory', 'polyamorous', 'multiple partners', 'non-monogamous', 'throuple', 'triad'],
            'Unplanned Pregnancy': ['unplanned pregnancy', 'unexpected pregnancy', 'surprise pregnancy', 'accidental pregnancy', 'secret baby'],
            'Secret Baby': ['secret baby', 'hidden pregnancy', 'love child', 'illegitimate child', 'concealed pregnancy', 'unacknowledged child'],
            'Infertility/Pregnancy Loss': ['infertility', 'pregnancy loss', 'miscarriage', 'stillbirth', 'loss of child', 'unable to conceive', 'fertility issues'],
            'Parental Issues': ['parental issues', 'dysfunctional family', 'toxic parents', 'absent parents', 'parental neglect', 'parental abuse'],
            'Age Play': ['age play', 'age regression', 'daddy kink', 'little space', 'caregiver/little dynamic', 'age difference'],
            'Teacher/Student': ['teacher/student', 'professor', 'college student', 'instructor']
        }
    
    def detect_subgenre(self, title, description="", tags=""):
        """Detect romance subgenre based on title, description, and tags"""
        text = f"{title} {description} {tags}".lower()
        
        detected_genres = []
        for genre, keywords in self.subgenre_keywords.items():
            if any(keyword in text for keyword in keywords):
                detected_genres.append(genre)
        
        # Return the most specific or first detected genre
        if detected_genres:
            # Prioritize more specific genres
            priority_order = ['Erotic Romance', 'LGBTQ+ Romance', 'MC Romance', 'Bully Romance', 
                            'Military Romance', 'Sports Romance', 'Rock Star Romance', 'Pirate Romance',
                            'Romantic Suspense', 'Paranormal Romance', 'Fantasy Romance', 
                            'Sci-Fi Romance', 'Royal Romance', 'Regency Romance', 'Historical Romance', 
                            'Cowboy Romance', 'Time Travel Romance', 'Urban Fantasy Romance',
                            'Dystopian Romance', 'Mythological Romance', 'Celebrity Romance',
                            'Medical Romance', 'Amish Romance', 'Holiday Romance', 'Taboo Romance']
            
            for priority_genre in priority_order:
                if priority_genre in detected_genres:
                    return priority_genre
            
            return detected_genres[0]
        
        return 'Contemporary Romance'  # Default
    
    def detect_tropes(self, title, description="", tags=""):
        """Detect romance tropes based on title, description, and tags"""
        text = f"{title} {description} {tags}".lower()
        
        detected_tropes = []
        for trope, keywords in self.tropes_keywords.items():
            if any(keyword in text for keyword in keywords):
                detected_tropes.append(trope)
        
        return detected_tropes[:5]  # Limit to top 5 tropes to avoid overwhelming
    
    def detect_content_warnings(self, title, description="", tags=""):
        """Detect potential content warnings based on title, description, and tags"""
        text = f"{title} {description} {tags}".lower()
        
        detected_warnings = []
        for warning, keywords in self.content_warning_keywords.items():
            if any(keyword in text for keyword in keywords):
                detected_warnings.append(warning)
        
        return detected_warnings
    
    def search_bookbub(self):
        """Search BookBub for free romance books with enhanced subgenre detection"""
        logger.info("Searching BookBub...")
        try:
            url = "https://www.bookbub.com/ebook-deals/free-ebooks/romance"
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for book items
            book_items = soup.find_all('div', class_='book-item')
            
            for item in book_items:
                try:
                    title_elem = item.find('h3', class_='book-title')
                    author_elem = item.find('p', class_='book-author')
                    description_elem = item.find('div', class_='book-description')
                    
                    if title_elem and author_elem:
                        title = title_elem.get_text(strip=True)
                        author = author_elem.get_text(strip=True)
                        description = description_elem.get_text(strip=True) if description_elem else ""
                        
                        # Get tags/categories if available
                        tags_elem = item.find('div', class_='book-tags')
                        tags = tags_elem.get_text(strip=True) if tags_elem else ""
                        
                        subgenre = self.detect_subgenre(title, description, tags)
                        tropes = self.detect_tropes(title, description, tags)
                        content_warnings = self.detect_content_warnings(title, description, tags)
                        
                        # Look for retailer links
                        retailer_links = item.find_all('a', class_='retailer-link')
                        
                        if not retailer_links:
                            # Try alternative selector
                            retailer_links = item.find_all('a', href=True)
                        
                        for link in retailer_links:
                            retailer_name = link.get('data-retailer', 'Unknown')
                            if retailer_name == 'Unknown':
                                # Try to detect from URL
                                href = link.get('href', '').lower()
                                if 'amazon' in href:
                                    retailer_name = 'Amazon'
                                elif 'barnesandnoble' in href or 'bn.com' in href:
                                    retailer_name = 'Barnes & Noble'
                                elif 'kobo' in href:
                                    retailer_name = 'Kobo'
                                elif 'apple' in href:
                                    retailer_name = 'Apple Books'
                            
                            retailer_url = link.get('href', '')
                            
                            self.books.append({
                                'title': title,
                                'author': author,
                                'subgenre': subgenre,
                                'tropes': tropes,
                                'content_warnings': content_warnings,
                                'description': description[:200] + "..." if len(description) > 200 else description,
                                'source': f'BookBub',
                                'retailer': retailer_name,
                                'price': 'Free',
                                'link': retailer_url,
                                'aggregator_link': url,
                                'found_date': datetime.now().strftime('%Y-%m-%d'),
                                'genre': 'Romance'
                            })
                            
                except Exception as e:
                    logger.warning(f"Error parsing BookBub item: {e}")
                    
        except Exception as e:
            logger.error(f"Error searching BookBub: {e}")
    
    def search_freebooksy(self):
        """Search Freebooksy for romance deals with subgenre detection"""
        logger.info("Searching Freebooksy...")
        try:
            url = "https://freebooksy.com/free-romance-books/"
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for book cards
            book_cards = soup.find_all('div', class_='book-card')
            
            for card in book_cards:
                try:
                    title_elem = card.find('h4', class_='book-title')
                    author_elem = card.find('p', class_='book-author')
                    description_elem = card.find('div', class_='book-description')
                    category_elem = card.find('span', class_='book-category')
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        author = author_elem.get_text(strip=True) if author_elem else "Unknown"
                        description = description_elem.get_text(strip=True) if description_elem else ""
                        category = category_elem.get_text(strip=True) if category_elem else ""
                        
                        subgenre = self.detect_subgenre(title, description, category)
                        tropes = self.detect_tropes(title, description, category)
                        content_warnings = self.detect_content_warnings(title, description, category)
                        
                        # Look for "Get Book" or retailer links
                        book_link = card.find('a', class_='book-link')
                        if book_link:
                            link_url = book_link.get('href', '')
                            
                            # Detect retailer from URL
                            retailer = 'Unknown'
                            if 'amazon' in link_url.lower():
                                retailer = 'Amazon'
                            elif 'barnesandnoble' in link_url.lower():
                                retailer = 'Barnes & Noble'
                            elif 'kobo' in link_url.lower():
                                retailer = 'Kobo'
                            
                            self.books.append({
                                'title': title,
                                'author': author,
                                'subgenre': subgenre,
                                'tropes': tropes,
                                'content_warnings': content_warnings,
                                'description': description[:200] + "..." if len(description) > 200 else description,
                                'source': 'Freebooksy',
                                'retailer': retailer,
                                'price': 'Free',
                                'link': link_url,
                                'aggregator_link': url,
                                'found_date': datetime.now().strftime('%Y-%m-%d'),
                                'genre': 'Romance'
                            })
                            
                except Exception as e:
                    logger.warning(f"Error parsing Freebooksy card: {e}")
                    
        except Exception as e:
            logger.error(f"Error searching Freebooksy: {e}")
    
    def search_bargain_booksy(self):
        """Search BargainBooksy for free romance books with enhanced parsing"""
        logger.info("Searching BargainBooksy...")
        try:
            url = "https://bargainbooksy.com/free-romance-ebooks/"
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse book listings
            book_entries = soup.find_all('div', class_='book-entry')
            
            for entry in book_entries:
                try:
                    title_elem = entry.find('h3')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        
                        # Look for author and description
                        author = "Unknown"
                        description = ""
                        
                        text_content = entry.get_text()
                        
                        # Extract author
                        author_match = re.search(r'by\s+([^\n\r]+)', text_content, re.IGNORECASE)
                        if author_match:
                            author = author_match.group(1).strip()
                        
                        # Extract description/blurb
                        paragraphs = entry.find_all('p')
                        for p in paragraphs:
                            p_text = p.get_text(strip=True)
                            if len(p_text) > 50 and 'by ' not in p_text.lower():
                                description = p_text
                                break
                        
                        subgenre = self.detect_subgenre(title, description)
                        tropes = self.detect_tropes(title, description)
                        content_warnings = self.detect_content_warnings(title, description)
                        
                        # Get retailer links
                        retailer_links = entry.find_all('a', href=True)
                        for link in retailer_links:
                            href = link['href']
                            retailer = 'Unknown'
                            
                            if 'amazon.' in href:
                                retailer = 'Amazon'
                            elif 'barnesandnoble.com' in href:
                                retailer = 'Barnes & Noble'
                            elif 'kobo.com' in href:
                                retailer = 'Kobo'
                            elif 'apple.com' in href and 'books' in href:
                                retailer = 'Apple Books'
                            
                            if retailer != 'Unknown':
                                self.books.append({
                                    'title': title,
                                    'author': author,
                                    'subgenre': subgenre,
                                    'tropes': tropes,
                                    'content_warnings': content_warnings,
                                    'description': description[:200] + "..." if len(description) > 200 else description,
                                    'source': 'BargainBooksy',
                                    'retailer': retailer,
                                    'price': 'Free',
                                    'link': href,
                                    'aggregator_link': url,
                                    'found_date': datetime.now().strftime('%Y-%m-%d'),
                                    'genre': 'Romance'
                                })
                                
                except Exception as e:
                    logger.warning(f"Error parsing BargainBooksy entry: {e}")
                    
        except Exception as e:
            logger.error(f"Error searching BargainBooksy: {e}")
    
    def search_all_sources(self):
        """Search all romance ebook aggregator sources"""
        logger.info("Starting romance ebook search for blog post...")
        
        # Search each source with delays to be respectful
        self.search_bookbub()
        time.sleep(3)
        
        self.search_freebooksy()
        time.sleep(3)
        
        self.search_bargain_booksy()
        time.sleep(3)
        
        # Remove duplicates based on title and author
        unique_books = []
        seen = set()
        
        for book in self.books:
            key = (book['title'].lower().strip(), book['author'].lower().strip())
            if key not in seen:
                unique_books.append(book)
                seen.add(key)
        
        self.books = unique_books
        logger.info(f"Search complete. Found {len(self.books)} unique free romance ebooks.")
    
    def generate_blog_post(self):
        """Generate a formatted blog post with the free ebooks"""
        if not self.books:
            return "No free romance ebooks found for this week's post."
        
        # Get next Friday's date
        today = datetime.now()
        days_ahead = 4 - today.weekday()  # Friday is weekday 4
        if days_ahead <= 0:  # Target is today or in the past
            days_ahead += 7
        next_friday = today + timedelta(days_ahead)
        
        blog_post = f"""# Free Romance Ebooks - {next_friday.strftime('%B %d, %Y')}

Welcome to this week's roundup of **FREE romance ebooks**! I've scoured the web to bring you the best free romance reads available right now. Remember, these deals can change quickly, so grab them while they're hot! 🔥

*Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*

---

"""
        
        # Group books by subgenre
        by_subgenre = {}
        for book in self.books:
            subgenre = book['subgenre']
            if subgenre not in by_subgenre:
                by_subgenre[subgenre] = []
            by_subgenre[subgenre].append(book)
        
        # Sort subgenres by number of books (most popular first)
        sorted_subgenres = sorted(by_subgenre.items(), key=lambda x: len(x[1]), reverse=True)
        
        for subgenre, books in sorted_subgenres:
            blog_post += f"## {subgenre} ({len(books)} book{'s' if len(books) != 1 else ''})\n\n"
            
            for book in sorted(books, key=lambda x: x['title']):
                blog_post += f"### {book['title']}\n"
                blog_post += f"**Author:** {book['author']}  \n"
                
                if book['description']:
                    blog_post += f"**Description:** {book['description']}  \n"
                
                # Add tropes if detected
                if book.get('tropes'):
                    tropes_list = ', '.join(book['tropes'])
                    blog_post += f"**Tropes:** {tropes_list}  \n"
                
                # Add content warnings if detected
                if book.get('content_warnings'):
                    warnings_list = ', '.join(book['content_warnings'])
                    blog_post += f"**⚠️ Content Warnings:** {warnings_list}  \n"
                
                # Group retailer links
                retailer_links = []
                for b in self.books:
                    if b['title'] == book['title'] and b['author'] == book['author']:
                        if b['retailer'] not in [r[0] for r in retailer_links]:
                            retailer_links.append((b['retailer'], b['link']))
                
                blog_post += f"**Get it free:** "
                link_texts = []
                for retailer, link in retailer_links:
                    if link and retailer != 'Unknown':
                        link_texts.append(f"[{retailer}]({link})")
                
                if link_texts:
                    blog_post += " | ".join(link_texts)
                else:
                    blog_post += "Check your favorite retailer"
                
                blog_post += f"  \n*Found via: {book['source']}*\n\n"
        
        blog_post += """---

## 📚 How to Get These Books

1. **Click the retailer links** above to go directly to the book's page
2. **Verify the price** is still $0.00 (deals can change quickly!)
3. **Add to cart** or click "Buy now" 
4. **Download** to your device or reading app

## 💡 Pro Tips

- **Act fast!** Free promotions are usually limited-time offers
- **Check multiple retailers** - sometimes one store will have it free while others don't
- **Sign up for newsletters** from BookBub, Freebooksy, and other deal sites
- **Follow your favorite authors** - they often announce their own free promotions
- **Pay attention to content warnings** - they help you choose books that match your comfort level

## 🏷️ Understanding the Tags

**Tropes** are popular romance themes and plot devices (like enemies-to-lovers, fake dating, etc.)  
**Content Warnings** alert you to potentially sensitive topics so you can read what feels right for you

---

*Happy reading! Let me know in the comments which books you grabbed this week and what tropes you're loving right now! 💕*

*This post contains affiliate links. If you purchase through these links, I may earn a small commission at no extra cost to you.*
"""
        
        return blog_post
    
    def save_blog_post(self, filename=None):
        """Save the blog post to a markdown file"""
        if not filename:
            next_friday = datetime.now() + timedelta((4 - datetime.now().weekday()) % 7)
            filename = f"free_romance_ebooks_{next_friday.strftime('%Y_%m_%d')}.md"
        
        blog_content = self.generate_blog_post()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(blog_content)
        
        logger.info(f"Blog post saved to {filename}")
        return filename
    
    def save_data_files(self):
        """Save the raw data to CSV and JSON"""
        # CSV
        csv_filename = f"romance_ebooks_data_{datetime.now().strftime('%Y_%m_%d')}.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'author', 'subgenre', 'tropes', 'content_warnings', 'description', 'source', 'retailer', 'price', 'link', 'found_date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for book in self.books:
                # Convert lists to strings for CSV
                book_data = book.copy()
                book_data['tropes'] = '; '.join(book.get('tropes', []))
                book_data['content_warnings'] = '; '.join(book.get('content_warnings', []))
                writer.writerow({k: v for k, v in book_data.items() if k in fieldnames})
        
        # JSON
        json_filename = f"romance_ebooks_data_{datetime.now().strftime('%Y_%m_%d')}.json"
        with open(json_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.books, jsonfile, indent=2, ensure_ascii=False)
        
        logger.info(f"Data saved to {csv_filename} and {json_filename}")
    
    def print_summary(self):
        """Print a summary for the blog owner"""
        if not self.books:
            print("No free romance ebooks found.")
            return
            
        print(f"\n=== BLOG POST READY: {len(self.books)} FREE ROMANCE EBOOKS ===")
        
        # Group by subgenre for summary
        by_subgenre = {}
        for book in self.books:
            subgenre = book['subgenre']
            if subgenre not in by_subgenre:
                by_subgenre[subgenre] = 0
            by_subgenre[subgenre] += 1
        
        print("\nSubgenre breakdown:")
        for subgenre, count in sorted(by_subgenre.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {subgenre}: {count} book{'s' if count != 1 else ''}")
        
        # Retailer breakdown
        retailers = {}
        for book in self.books:
            retailer = book['retailer']
            if retailer not in retailers:
                retailers[retailer] = 0
            retailers[retailer] += 1
        
        print("\nRetailer coverage:")
        for retailer, count in sorted(retailers.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {retailer}: {count} book{'s' if count != 1 else ''}")

def main():
    """Main function"""
    print("Romance Ebook Blog Generator")
    print("===========================")
    print("Generating your weekly free romance ebooks blog post...")
    
    generator = RomanceBlogGenerator()
    
    try:
        # Search all sources
        generator.search_all_sources()
        
        # Show summary
        generator.print_summary()
        
        # Generate and save blog post
        blog_filename = generator.save_blog_post()
        generator.save_data_files()
        
        print(f"\n✅ Blog post ready: {blog_filename}")
        print("📊 Data files saved for reference")
        print("\n🎉 Your Friday blog post is ready to publish!")
        
    except KeyboardInterrupt:
        print("\nSearch interrupted by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()