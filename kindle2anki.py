#!/usr/local/bin/python3

# imports
from sys import exit, argv
from os import path, access, R_OK
import argparse
from cs50 import SQL
from simple_term_menu import TerminalMenu
import requests
import logging
from urllib.error import HTTPError
from requests.adapters import HTTPAdapter
from requests.exceptions import RetryError
from pyrae import dle
import regex as re
import k2a_response_parsers as p
import hashlib
from datetime import datetime
import genanki

def main(): # main program
    # check command line args and deternine db and deck file
    args = checkargs(argv)
    vdb = args['vdb']
    deckname = args['deck']
    num_log_level = args['num_log_level']
    string_log_level = args['string_log_level']

    # get database handle
    db = SQL(f"sqlite:///{vdb}")

    # select book for deck
    book = select_book(db)

    # get list of dictionaries dictionaries with source language 
    # matching the language of the chosen book
    dicts = get_dictionaries(book['lang'])
    if not dicts:
        exit(f"no dictionary as yet configured for language '{book['lang']}'")

    # select one of the dicitonaries available for the source language
    dict = select_dictionary(dicts)
    if dict['url'] == 'https://dle.rae.es/':
        rae = True
    else:
        rae = False

    
    # select a card type (A or B) for the cards in the deck to be created
    card_type = select_card_type()

    # get a dictionary mapping 'usages' (i.e. the text passages where the looked up words occured)
    # as values to the words as keys 
    usage = get_usage(db, book)

    # for conveniece get the words (keys of usage) as a list
    words = list(usage.keys())

    # establish a connection to the dictionary URL of the chosen dictionary
    if rae == False:
        session = connect(dict['url'], dict['referer'], num_log_level)

        # retrieve dictinary definitions for the words in our book that were looked up in kindle
        definitions = get_definitions(session, dict, words)

        # close the https session
        session.close()
    else:
        # connection will be handled by pyrae module
        definitions = get_definitions_rae(words, string_log_level)
    
    # create the anki card deck
    deck = create_deck(deckname)

    # add cards to the card deck (of the chosen card type, one per word)
    create_cards(deck, dict, card_type, words, usage, definitions)

    # write out card deck to a apkg file
    genanki.Package(deck).write_to_file(deckname)

def checkargs(argv): # check and evaluate command line input
    """
    :param argv:    array of command line arguments to be parsed and interpreted  
    :return dict:   anonymous dictionary containing 'vdb' (the path to the kindle vocabluary database)
                    and 'deck' (the name of the Anki card deck to be created)
    """
    parser = argparse.ArgumentParser(description="Create Anki card decks from Kindle vocabluary database")
    parser.add_argument("-k", default="default", help="Path to directory where kindle vocab.db resides, default='.'", type=str)
    parser.add_argument("-d", default="default", help="Name of Anki card deck, default='default.apkg'", type=str)
    parser.add_argument("-l", default="WARNING", help="log level for http(s) sessions, default='WARNING'", type=str)
    args = parser.parse_args()
    
    # determine kindle vocab.db
    if args.k == "default":
        dir = path.split(path.realpath(argv[0]))[0]
    else:
        dir = args.k
        if not (path.exists(dir) and path.isdir(dir)):
            exit(f"{dir} does not exist")

    # vocab db assumed to be in the same directory as our script
    vdb = path.join(dir, "vocab.db")
    if not (path.exists(vdb) and path.isfile(vdb)):
        exit(f"no vocab.db found at {dir}")
    if not access(vdb, R_OK):
        exit(f"vocab.db not readable")
    
    # determine deck file
    if args.d == 'default' or args.d == 'default.apkg':
        deckname = "default.apkg"
    else:
        if re.match(r'.+\.apkg', args.d):
            deckname = args.d
        else:
            deckname = args.d + ".apkg"

    # determine log level
    levels =  re.compile(r'DEBUG|INFO|WARNING|ERROR', flags=re.IGNORECASE)
    if levels.fullmatch(args.l):            # ensure the entire string matches
        string_log_level = args.l.upper()   # Convert to uppercase for consistency
    else:
        exit("Invalid log level. Valid args are: DEBUG, INFO, WARNING, ERROR")
    
    # Use getattr to convert the string to the actual log level constant
    num_log_level = getattr(logging, string_log_level, None)

    if num_log_level is None:
        exit(f'Invalid log level: {string_log_level}')

    return {'vdb': vdb, 'deck': deckname, 'num_log_level': num_log_level, 'string_log_level': string_log_level}

def select_book(db): # select a Kindle book for which a vocab card deck is to be created
    """
    :param db:      database handle to kindle sqlite vocab database 
    :return book:   Kindle e-book (db record) selected by user for vocab queries
    """
    # get keys of books for which we have looked up vocab
    key_dict = db.execute("SELECT DISTINCT(book_key) FROM LOOKUPS")
    book_keys = [key['book_key'] for key in key_dict]
    book_info = db.execute("SELECT id, lang, title, authors FROM BOOK_INFO WHERE id IN (?)", book_keys)
    
    options = [] # for building menu opions
    book_id = {} # for looking up book_key for selected menu option

    for book in book_info:
        id = book['id']
        num_words = list(db.execute("SELECT COUNT(DISTINCT(word_key)) FROM LOOKUPS WHERE book_key = ?", id)[0].values())[0]
        book['num_words'] = num_words
        option_keys = ['lang', 'title', 'authors', 'num_words']
        option = '::'.join(str(book[key]) for key in option_keys)
        options.append(option)
        book_id[option] = id
    options = sorted(options)

    while True:
        input("""
Please select a book from which to create a deck
Options for Selection will be presented in format:

<language>::<Book Title>::<Authors>::<count of looked up words to be included in deck>
            
Press any key to continue ...
""")
        terminal_menu = TerminalMenu(options, title='Books')
        menu_entry_index = terminal_menu.show()
        
        # catch error if user presses escape instead of "y" or "n"
        try:
            match is_happy(options[menu_entry_index]):
                case True:
                    break
                case _:
                    continue
        except TypeError:
            continue

    # return the book dict for the selection
    return next((book for book in book_info if book['id'] == book_id[options[menu_entry_index]]), None)

def select_card_type(): # select card type 'A' (definitions on the back) or 'B' (definitions on the front)
   """
   :param :             this function takes no params
   :return card type:   i.e. 'A' or 'B' (see 'options' below)  
   """
   options = [
        'A - Front: word and usage example from book / Back: definitions',
        'B - Front: definitions / Back: word and usage example from book'
   ]
   while True:
        input("""
Please select card type for your card deck:
Press any key to continue ...
""")

        terminal_menu = TerminalMenu(options, title='Card Type')
        menu_entry_index = terminal_menu.show() 

        # catch error when user presses escape instead of "y" or "n"
        try:
            match is_happy(options[menu_entry_index]):
                case True:
                    return options[menu_entry_index][0]
                case _:
                    continue
        except TypeError:
            continue 

def get_usage(db, book): # retrieve text passages with looked-up words from kindle db
    """
    :param db :     the sqllite database-handle to the kindle database
    :param book:    the book selected 
    :return usage:  a dictionary with the looked-up words as keys and 'usages' (i.e. the text passages 
                    in the e-book) where the looked-up word occured as values
    """
    usage = {}
    worddicts = db.execute("SELECT word_key, usage FROM LOOKUPS WHERE book_key = ?", book['id'])
    for worddict in worddicts:
        word = worddict['word_key'].split(':')[1]
        if not word in usage:
            usage[word] = worddict['usage'].replace(word, f"<b>{word}</b>")
    return usage

def get_dictionaries(lang): # get available dictionaries for language of chosen book
    """
    :param lang:                source language of dictionaries to be presented for selection (e.g. "en" for English) 
    :return dictionaries[lang]: a list of dictionaries (data type) for the selected language, each bundling information (e.g. URL, Description) on a specific dictionary  
    """
   # template for dict entry
        #'src_lang': '',     #'source language' = language of lookup word
        #'dictionaries': {   # available dictionaries of that language
        #    'id': 1,        # id for that dictionary
        #    'src_lang': '', # language of word to be looked up 
        #    'dst_lang': '', # language of definitions retreived 
        #    'name': '',     # name of dictionary
        #    'desc': '',     # description of dictionary
        #    'url': ''       # URL including "http[s]://" stump  
        #    'referer'       # referer URL to be used in request headers
        #}
        # dictionaries for which no parser has as yet been written, are commmented out 
    dictionaries = {
        # english dictionaries
        'en': [
            {   
                'id': 1,
                'src_lang': 'en',
                'dst_lang': 'en',
                'name': 'Meriam Webster',
                'desc': 'mono-lingual ',
                'url': 'https://www.merriam-webster.com/dictionary/',
                'referer': 'https://www.merriam-webster.com',
            },
            { 
                'id': 2,
                'src_lang': 'en',
                'dst_lang': 'de',
                'name': 'Larousse',
                'desc': 'bi-lingual EN->DE',
                'url': 'https://www.larousse.com/en/dictionaries/english-german/',
                'referer': 'https://www.larousse.com'
            },
            {   
                'id': 3,       
                'src_lang': 'en',
                'dst_lang': 'fr',
                'name': 'Larousse',
                'desc': 'bi-lingual EN->FR',
                'url': 'https://www.larousse.fr/dictionnaires/anglais-francais/',
                'referer': 'https://www.larousse.fr/'
            },
            {   
                'id': 4,       
                'src_lang': 'en',
                'dst_lang': 'es',
                'name': 'Larousse',
                'desc': 'bi-lingual EN->ES',
                'url': 'https://www.larousse.com/en/dictionaries/english-spanish/',
                'referer': 'https://www.larousse.com'
            },
        ],
        # french dictionaries
        'fr': [
            {   
                'id': 1,       
                'src_lang': 'fr',
                'dst_lang': 'fr',
                'name': 'Larousse',
                'desc': 'mono-lingual FR->FR',
                'url': 'https://www.larousse.fr/dictionnaires/francais/',
                'referer': 'https://www.larousse.fr'
            },
            # {   
            #     'id': 2,       
            #     'src_lang': 'fr',
            #     'dst_lang': 'en',
            #     'name': 'Larousse',
            #     'desc': 'bi-lingual FR->EN',
            #     'url': 'https://www.larousse.fr/dictionnaires/francais-anglais'
            # },
            # {   
            #     'id': 3,       
            #     'src_lang': 'fr',
            #     'dst_lang': 'de',
            #     'name': 'Larousse',
            #     'desc': 'bi-lingual FR->DE',
            #     'url': 'https://www.larousse.fr/dictionnaires/francais-allemand'
            # },
            # {   
            #     'id': 4,       
            #     'src_lang': 'fr',
            #     'dst_lang': 'es',
            #     'name': 'Larousse',
            #     'desc': 'bi-lingual FR->ES',
            #     'url': 'https://www.larousse.com/en/dictionaries/francais-espagnol'
            # },
        ],
        # spanish dictionaries
        'es': [
            {   
                'id': 1,       
                'src_lang': 'es',
                'dst_lang': 'es',
                'name': 'Dicionario de la lengua española',
                'desc': 'mono-lingual Spanish dictionary by the "Real Academia Española"',
                'url': 'https://dle.rae.es/',
                'referer': 'https://dle.rae.es'
            },
            # {   
            #     'id': 2,       
            #     'src_lang': 'es',
            #     'dst_lang': 'en',
            #     'name': 'Collins',
            #     'desc': 'bi-lingual ES->EN',
            #     'url': 'https://www.collinsdictionary.com/dictionary/spanish-english/'
            # },

        ],
        # portuguese dictionaries
        'pt': [
            {   
                'id': 1,       
                'src_lang': 'pt',
                'dst_lang': 'pt',
                'name': 'Michaelis',
                'desc': 'mono-lingual PT->PT (Brazilian)',
                'url': 'https://michaelis.uol.com.br/moderno-portugues/busca/portugues-brasileiro/',
                'referer': 'https://michaelis.uol.com.br'
            },
            # {   
            #     'id': 2,       
            #     'src_lang': 'pt',
            #     'dst_lang': 'en',
            #     'name': 'Collins',
            #     'desc': 'bi-lingual PT->EN',
            #     'url': 'https://www.collinsdictionary.com/dictionary/portuguese-english/'
            # },
        ],
        # german dictionaries
        'de': [
            # {   
            #     'id': 1,       
            #     'src_lang': 'de',
            #     'dst_lang': 'de',
            #     'name': 'Digitales Wörterbuch der deutschen Sprache',
            #     'desc': 'mono-lingual DE->DE',
            #     'url': 'https://www.dwds.de/wb/'
            # },
            # {   
            #     'id': 2,       
            #     'src_lang': 'de',
            #     'dst_lang': 'en',
            #     'name': 'Collins',
            #     'desc': 'bi-lingual DE->EN',
            #     'url': 'https://www.collinsdictionary.com/dictionary/german-english/'
            # },
        ]
    }
    if lang in list(dictionaries.keys()):
        return dictionaries[lang]
    else:
        raise ValueError("Invalid Language")

def select_dictionary(dicts): # select a dictionary for the lookups
    """
    :param dicts: a list of dictionaries to chose from (those matching the language of the chosen book)
    :return dict: a dictionary (data type) bundling information about the chosen language dictionary
    """
    options = [] # for building menu opions
    dict_id = {} # for looking up book_key for selected menu option

    for dict in dicts:
        option_keys = ['id', 'name', 'desc']
        option = '::'.join(str(dict[key]) for key in option_keys)
        options.append(option)
        dict_id[option] = dict['id']

    while True:
        input("""
Please select a dictionary from which to query definitions.
Options for selection will be presented in format:

<id>::<dictionary name>::<dicionary description>
            
Press any key to continue ...
""")
        terminal_menu = TerminalMenu(options, title='Dictionaries')
        menu_entry_index = terminal_menu.show()

        try:
            match is_happy(options[menu_entry_index]):
                case True:
                    break
                case _:
                    continue
        except TypeError:
            continue

    return next((dict for dict in dicts if dict['id'] == dict_id[options[menu_entry_index]]), None)

def get_definitions(session, dict, words):  # retrieve dictionary definitions for the looked-up words from the chosen Kindle book
    """
    :param session:     the request session object to be used for get requests
    :param dict:        a dictionary (data type) containing information about the 
                        (online language) dictionary to be used for lookups
    :param words:       the list of words to be looked up    
    :return definitions: a dictionary of definitions with looked up words as keys
    """
    definitions = {}
    baseurl = dict['url']
    parser = 'parse_' + dict['src_lang'] + "_" + str(dict['id'])
    parse = getattr(p, parser)

    print(f'Looking up words at {baseurl}...', end="")
    for word in words:
        # determine lookup url for word
        url =  baseurl + word.lower()
        print(f"looking up {word} ...", end="")
        try:
            r = session.get(url, timeout=5)
        except Exception as err:
            print(f"an error occured trying to retrieve {url}")
            definitions[word] = 'None'
        else:
            r.encoding = 'utf-8'  # Explicitly set the encoding to utf-8
            definitions[word] = parse(r.text, word) # word is not used in all parser functions but we submit it for good measure
        if definitions[word] == 'None':
            print('not found')
        else:
            print('success') 
    return definitions

def get_definitions_rae(words, log_level):  # custom get_definitions function for "rae" since our standard connect method did not work
    """
    :param dict:        a dictionary (data type) containing information about the 
                        (online language) dictionary to be used for lookups
    :param words:       the list of words to be looked up    
    :return definitions: a dictionary of definitions with looked up words as keys
    """
    dle.set_log_level(log_level)
    definitions = {}
    parser = 'parse_es_1'
    parse = getattr(p, parser)

    for word in words:
        # base url is encoded in dle module
        print(f'looking up {word} ...', end="")
        try:
            r = dle.search_by_word(word = f'{word}')
        except Exception as err:
            print(f"an error occured trying to retrieve dle dictionary entry for {word}")
            definitions[word] = 'None'
        else:
            r.encoding = 'utf-8'  # Explicitly set the encoding to utf-8
            definitions[word] = parse(r._html)
            if definitions[word] == 'None':
                print('not found')
            else:
                print('success')
    return definitions

def highlight(definition, word, card_type, lang): # highlight occurences of the word in bold-face
    """
    :param definition:     text response from the original lookup query to the mapped french language online dictionary 
    :param word:           the word looked up in dictionary
    :param card_type:      the selected card type determines replacemnt patterns
    :param lang:           the language of the looked-up word (determines suffixes to be considered in pattern matching for highlighting)
    :return definition:    the text with occurrences of word (including gramatically modified forms) hightlighted in bold-face
    """
    # we want to catch not only the looked up word verbatim but also grammatical variations 
    # (e.g. as per number, gender or conjugation) that are frequent in many languages
    # the following dictionary of suffix lists (one list per language), is unfotunately a 
    # config item (though eventually a static one) hard coded in this function
    patterns = [word]
    s = {
        'en': ['s', 'ed', 'er', 'ing', 'ly'],
        'fr': ['s', 'e', 'es', 'eur', 'euse', 'aux', 'il', 'ille', 'eux', 'x','t', 'ent' , 'is' ,'it', 'ons', 'ont','ment'],
        'es': ['s','o','a','os','as','ir','er','ar','í','ó','é','aron','se','ieron','amos','imos','emos','eis','ais','mente','aba'],
        'pt': ['s','ir','er','ar','a','o','al','este','amos','emos','imos','ou','ei','i','ão','ões','aste','aram','eram','mente','ava'],
        'de': ['e','st','er','s','t','d','en','ig','lich','ung','keit'],
    }
    suffixes = s[lang]
    has_suffix = False
    for s1 in suffixes:
        # add patterns with suffix removed from word
        if word.endswith(s1):
            has_suffix = True
            root = word[:-len(s1)]
            patterns.append(root)
            for s2 in suffixes:
                if s2 == s1:
                    continue
                else:
                    patterns.append(root + s2)
    if has_suffix == False:
        for s in suffixes:
            patterns.append(word + s)    

    # this is a special for the Portuguese Michaelis Dicitionary
    # they include sillable separated spelling (like 'sel·va·gem')
    # which would give away the word (would not be caught by the regex
    # a few lines down (replacing the word by (...) unless we remove it 
    if card_type == 'B':
        definition = re.sub(r'(\b\w+·){1,}\w+\b',r'', definition)

    # hightlight patterns, for card type 'B' replace the word by (...)
    for pattern in patterns:
        p = rf'(^|\s)({pattern})(\s|\.|\,|:|\?|$)'
        if card_type == 'A':
            r = r'\1<b>\2</b>\3'
        else:
            r = r'\1<b>(...)</b>\3'
        definition = re.sub(p, r, definition, flags=re.IGNORECASE)

    return definition

def is_happy(selection): # make sure user is happy with a menu selection 
    """
    :param selection:   a user's selection from a drop-down menu in the calling function 
    :return boolean:    'True': user confirms choice, 'False' user will be prompted to chose again 
    """
    yesno = False
    r = re.compile('^(y(es)?$|^no?$)', flags=re.IGNORECASE)
    while yesno  == False:  
        print(f"You have selected:>>>{selection}<<<\n")
        answer = input (f"Are you happy with your selection (y/n)? ")
        if r.match(answer):
            yesno = True
    match answer:
        case 'y'|'Y'|'yes'|'Yes':
            return True
        case 'n'|'N'|'no'|'NO':
            return False

def connect(url, referer, log_level): # initiate https connection to online dictionary
    """
    :param url:         dicionary URL 
    :log_level:         log level for session logging
    :return session:    request session object
    """
    logging.getLogger("requests").setLevel(log_level)
    logging.getLogger("urllib3").setLevel(log_level)
    adapter = HTTPAdapter(max_retries=5)
    session = requests.Session()
    session.mount(url, adapter)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': referer,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive'
    }

    try:
        r = session.get(
            url,
            timeout = (3, 5),
            headers = headers,
            allow_redirects=True
        )
        r.raise_for_status()
    except RetryError as err:
        print(f"Error: {err}")
    except HTTPError as http_err:
        print(f"a https error occured: {http_err}")
    except Exception as err:
        print(f"some error occured: {err}")
    else:
        print(f"Successfully connected to {url}")

    return session

def create_deck(deckname): # create a card deck
    """
    :param deckname:    name of the card deck to be created
    :return deck:       card deck object
    """
    # Generate a unique deck ID using deck name and timestamp
    unique_string = 'k2a' + str(datetime.now())  # Combine deck name with the current timestamp
    deck_id = int(hashlib.md5(unique_string.encode('utf-8')).hexdigest(), 16) >> 96

    deck = genanki.Deck(
        deck_id,
        deckname
    )
    print(f'Creating card deck {deckname}')
    return deck

def create_cards(deck, dict, card_type, words, usage, definitions): # write cards to card deck 
    """
    :param deck:        the card deck object that accomodates the cards to be created
    :param dict:        the dictionary object used
    :param card_type:   the card type selected (A or B) 
    :param words:       array of words for which cards are to be created
    :param usage:       a dictionary object containing the text passages from which words had been looked up in Kindle 
    :param definitions: the dictionary definintions looked up for each word        
    :return:            this functinon does not have a return value
    """
    # Define the basic card model (Front/Back flashcard)
    basic_model = genanki.Model(
        1149758716, # was generated with random.randrange(1 << 30, 1 << 31)
        'Simple Model',
        fields = [
            {'name': 'Question'},
            {'name': 'Answer'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Question}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ],
        css="""
        .card {
            font-family: arial;
            font-size: 20px;
            color: black;
            background-color: white;
        }
        """  # Custom CSS controlling font size and other styles
    )
    # iterate over words to to create cards and add the to the deck ...
    for word in words:
        if definitions[word] == 'None':
            print(f"no definition found for {word} - skipping ...")
            continue
        else:
            print(f"Adding card for {word} ...")
            #htmlify '\n' in definitions and highlight word occurences in bold-face
            definition = highlight(definitions[word].replace('\n','<br>'), word, card_type, dict['src_lang'])


        # htmlify '\n' in text passage
        passage = usage[word].replace('\n','<br>')

        # define front and back depending on card type and highlight occurrences of word
        # Kindle passage and dictionary definitions
        if card_type == 'A':
            # make looked word stand out bold in text passage
            front = f"<b>{word}</b><br><br>{passage}"
            back = definition
        else: # card type must be 'B'
            front = definition
            back = f"<b>{word}</b><br><br>{passage}" 
        
        # create card for word
        card = genanki.Note(
            model = basic_model,
            fields=[front, back])
        # add card to deck
        deck.add_note(card)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # If Ctrl+C is pressed outside the main logic or for other reasons
        print("\nKeyboard interrupt received - exiting...")
        exit(0)