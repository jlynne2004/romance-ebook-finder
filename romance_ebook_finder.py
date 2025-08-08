# romance_ebook_finder.py

"""Romance Ebook Finder
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

class RomanceEbookFinder:
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
            'Best Friend’s Sibling': ['best friend’s sibling', 'brother of best friend', 'sister of best friend', 'friend’s sibling', 'sibling of best friend'],
            'Sibling’s Best Friend': ['sibling’s best friend', 'brother’s best friend', 'sister’s best friend'],
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

        def detect_subgenres(self, title, description="", tags=""):
            """Detect subgenres based on keywords in the text."""
            text = f"{title} {description} {tags}".lower()

            detected_subgenres = set()
            for subgenre, keywords in self.subgenre_keywords.items():
                if any(keyword in text for keyword in keywords):
                    detected_subgenres.add(subgenre)

            # Return the most specific or first detected subgenre
            if detected_subgenres:
                priority_order = [
                    'Amish Romance', 'Regency Romance', 'Pirate Romance', 'MC Romance', 'Cowboy Romance',
                    'Rock Star Romance', 'Sports Romance', 'Medical Romance', 'Military Romance', 'Royal Romance',
                    'Billionaire Romance', 'Interracial Romance', 'LGBTQ+ Romance', 'Disability Romance', 'Celebrity Romance',
                    'Small Town Romance', 'Urban Fantasy Romance', 'Urban Romance', 'Dystopian Romance', 'Mythological Romance',
                    'Fantasy Romance', 'Paranormal Romance', 'Sci-Fi Romance', 'Time Travel Romance', 'Adventure Romance',
                    'Romantic Suspense', 'Romantic Comedy', 'Second Chance Romance', 'Survival Romance',
                    'Inspirational Romance', 'Young Adult Romance', 'Sweet Romance', 'Clean Romance', 'Holiday Romance',
                    'Historical Romance', 'Bully Romance', 'Taboo Romance', 'Erotic Romance'
                ]
                for priority_subgenre in priority_order:
                    if priority_subgenre in detected_subgenres:
                        return [priority_subgenre]
                return [detected_subgenres[0]]
            return ["Contemporary Romance"] # Default if none detected

        def detect_tropes(self, title, description="", tags=""):
            """Detect tropes based on keywords in the text."""
            text = f"{title} {description} {tags}".lower()

            detected_tropes = set()
            for trope, keywords in self.trope_keywords.items():
                if any(keyword in text for keyword in keywords):
                    detected_tropes.add(trope)

            return list(detected_tropes)
        
        def detect_content_warnings(self, title, description="", tags=""):
            """Detect content warnings based on keywords in the text."""
            text = f"{title} {description} {tags}".lower()

            detected_warnings = set()
            for warning, keywords in self.content_warning_keywords.items():
                if any(keyword in text for keyword in keywords):
                    detected_warnings.add(warning)

            return list(detected_warnings)
        
        def search_bookbub(self, max_results=100):
            """Search BookBub for free romance ebooks."""
            url = "https://www.bookbub.com/ebook-deals/free-romance-ebooks"
            logger.info(f"Searching BookBub for free romance ebooks: {url}")
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                ebooks = soup.find_all("div", class_="book-card")
                for ebook in ebooks:
                    title = ebook.find("h3").text.strip()
                    author = ebook.find("p", class_="author").text.strip()
                    description = ebook.find("p", class_="description").text.strip()
                    tags = ebook.find("p", class_="tags").text.strip()
                    subgenres = self.detect_subgenres(title, description, tags)
                    tropes = self.detect_tropes(title, description, tags)
                    content_warnings = self.detect_content_warnings(title, description, tags)
                    retailer_links = ebook.find_all("a", class_="retailer-link")
                    if retailer_links:
                        # Assuming the first link is the main retailer link
                        main_retailer_link = urljoin(url, retailer_links[0]['href'])
                    else:
                        main_retailer_link = None
                    self.books.append({
                        "title": title,
                        "author": author,
                        "description": description,
                        "tags": tags,
                        "subgenres": subgenres,
                        "tropes": tropes,
                        "content_warnings": content_warnings,
                        "retailer_link": main_retailer_link,
                        "source": "BookBub",
                        "date_found": datetime.now().isoformat()
                    })
            else:
                logger.error(f"Failed to fetch BookBub page: {response.status_code}")

            return self.books
        
    def save_books_to_csv(self, filename="romance_ebooks.csv"):
        """Save the found books to a CSV file."""
        logger.info(f"Saving {len(self.books)} books to {filename}")
        with open(filename, "w", newline='', encoding='utf-8') as csvfile:
            fieldnames = ["title", "author", "description", "tags", "subgenres", "tropes", "content_warnings", "retailer_link", "source", "date_found"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for book in self.books:
                writer.writerow(book)