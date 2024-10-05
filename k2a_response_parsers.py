from bs4 import BeautifulSoup as bs
import unicodedata
import regex as re
# each parser function defined maps to a specific online dictionary
# the mapping is via the parser function naming as 'parse_' + {lang} + {dictionary ID}
# e.g. functino 'parse_en_1' maps to the first (id '1') English (lang 'en') dictionary defined.
# The available dictionaries are defined within the kindle2anki.getDictioaries() function 

def parse_en_1 (response, word=None):    # EN: Merriam-Websters mono-lingual
    """
    :param response:    text response from the original lookup query to the mapped online dictionary 
    :param word:        looked-up word, not needed in most parsers, but included to allow for uniform call across functions
    :return parsed:     text string containing the dictionary definitions parsed from the response 
    """
    soup = bs(response, 'html.parser')
    parsed = ""
    # Definitions are contained in the section with class 'entry-attr'
    definitions_section = soup.find('div', class_='vg')
    
    if not definitions_section: 
        return "None"
    
    # Find all the numbered (top-level) definitions
    entry_items = definitions_section.find_all('div', class_=['vg-sseq-entry-item'])
    for i, item in enumerate(entry_items, 1):
        pattern = re.compile(r'sb-\d sb-entry')
        definitions = item.find_all('div', class_=pattern)
        for definition in definitions:
            cleaned = definition.get_text(separator=" ", strip=True)
            cleaned = unicodedata.normalize("NFC", cleaned)
            cleaned = re.sub(r'^\:\s', r'', cleaned)
            cleaned = re.sub(r'^([a-z]) \:', r'\1:', cleaned)
            cleaned = re.sub(r'([a-z])\s(\(1\))\s\:', r'\1: \2', cleaned)
            cleaned = re.sub(r'(\([2-9]\)\s)\:', r'\n      \1', cleaned)
            if len(entry_items) == 1:
                parsed += cleaned
            else:
                if definition == definitions[0]:
                    parsed += f"{i}. {cleaned}\n\n"
                else:
                    parsed += f"   {cleaned}\n\n"
            
    return parsed

def parse_en_2 (response, word=None):    # EN: Larousse EN->DE
    """
    :param response:    text response from the original lookup query to the mapped online dictionary 
    :param word:        looked-up word, not needed in most parsers, but included to allow for uniform call across functions
    :return parsed:     text string containing the dictionary definitions parsed from the response 
    """
    parsed = ""
    soup = bs(response, 'html.parser')
    definitions = soup.find_all(class_='content en-de')

    if not definitions:
        return "None"
    
    for definition in definitions:
        cleaned = definition.get_text(separator=" ", strip=True)
        # Normalize to handle accent variations (NFC)
        cleaned = unicodedata.normalize("NFC", cleaned)

        cleaned = re.sub(r'\r?\n', ' ', cleaned)
        cleaned = re.sub(r'(\d\.)' ,r'\n\n\1',cleaned)
        parsed += f"{cleaned}\n"
    
    return parsed

def parse_en_3 (response, word=None):    # EN: Larousse EN->FR
    """
    :param response:    text response from the original lookup query to the mapped online dictionary 
    :param word:        looked-up word, not needed in most parsers, but included to allow for uniform call across functions
    :return parsed:     text string containing the dictionary definitions parsed from the response 
    """
    parsed = ""
    soup = bs(response, 'html.parser')
    
    definition_section = soup.find(id='BlocArticle')

    if not definition_section:
        return "None"
    
    # more than one definition
    definitions = definition_section.find_all(class_='itemZONESEM')
    if not definitions:
        # only one definition
        definitions = [ definition_section.find(class_='ZoneTexte') ]

    for count, definition in enumerate(definitions, 1):
        cleaned = definition.get_text(separator=" ", strip=True)
        cleaned = unicodedata.normalize("NFC", cleaned)
        
        if len(definitions) == 1:
            parsed += cleaned
        else:
            parsed += f"{count}. {cleaned}\n\n"
    
    return parsed

def parse_en_4 (response, word=None):    # EN: Larousse EN->SP
    """
    :param response:    text response from the original lookup query to the mapped online dictionary 
    :param word:        looked-up word, not needed in most parsers, but included to allow for uniform call across functions
    :return parsed:     text string containing the dictionary definitions parsed from the response 
    """
    soup = bs(response, 'html.parser')
    
    definition_section = soup.find(class_='content en-es')
    if not definition_section:
        return 'None'
    
    for a in definition_section.find_all("a"):
         a.replace_with(a.text)
    
    cleaned = definition_section.get_text(separator=" ", strip=True)
    cleaned = unicodedata.normalize("NFC", cleaned)
    cleaned = re.sub(r'(\r\n|\n|\r)', ' ', cleaned)
    cleaned = re.sub(r'Conjugation ','', cleaned)
    cleaned = re.sub(r'(\d\.)' ,r'\n\1',cleaned)

    return cleaned

def parse_fr_1 (response, word=None):    # FR: Larousse mono-lingual
    """
    :param response:    text response from the original lookup query to the mapped online dictionary 
    :param word:        looked-up word, not needed in most parsers, but included to allow for uniform call across functions
    :return parsed:     text string containing the dictionary definitions parsed from the response 
    """
    parsed = ""
    soup = bs(response, 'html.parser')
    definitions = soup.find_all(class_='DivisionDefinition')

    if not definitions:
        return "None"
    
    for definition in definitions:
        cleaned = definition.get_text(separator=" ", strip=True)
        # Normalize to handle accent variations (NFC)
        cleaned = unicodedata.normalize("NFC", cleaned)
        cleaned = cleaned.replace(' :', ': ')
        cleaned = cleaned.replace(' - ', ' / ')
        cleaned = re.sub(r'([^\d]\.)', r'\1 ', cleaned)
        cleaned = re.sub(r'(Litt.raire)\.', r'(\1):', cleaned)
        cleaned = re.sub(r'(Synonymes?:)', r'\n\n\1', cleaned)
        cleaned = re.sub(r'(Contraires?:)', r'\n\n\1', cleaned)
                
        #parsed_array.append(cleaned)
        parsed += f"{cleaned}\n\n" 
    
    return parsed

def parse_es_1 (response, word=None):    # ES: Real Académia Española mono-lingual
    """
    :param response:    text response from the original lookup query to the mapped online dictionary 
    :param word:        looked-up word, not needed in most parsers, but included to allow for uniform call across functions
    :return parsed:     text string containing the dictionary definitions parsed from the response 
    """
    parsed = ""
    soup = bs(response, 'html.parser')
   # Find the article containing the definitions
    definitions_section = soup.find('div', id='resultados')

    # Extract the definitions from the <p> tags with class "j"
    if definitions_section:
        definitions = definitions_section.find_all('p', class_='j')
        if len(definitions) == 0:
            return 'None'
        for definition in definitions:
            cleaned = definition.get_text(separator=" ", strip=True)
            cleaned = unicodedata.normalize("NFC", cleaned)
            cleaned = cleaned.replace(' . ', '. ')  # get red of superfluous spaces before "."
            cleaned = cleaned.replace(' , ', ', ')  # get red of superfluous spaces before "."
            cleaned = cleaned.replace('f. ', '')    # get rid of the gender indicator
            cleaned = cleaned.replace('m. ', '')    # get rid of the gender indicator
            cleaned = re.sub(r'(Sin\.:)', r'\n   \1 ', cleaned) # list synonymes in new line
            cleaned = re.sub(r'(Ant\.:)', r'\n   \1 ', cleaned) # list antonoymes in new line
            cleaned = re.sub(r' \.$', r'', cleaned)           # get rid of trailing " ."
            cleaned = re.sub(r' \d$', r'', cleaned)           # get rid of trailing nummber (from annotations)
            #cleaned = re.sub(r'\d\.+$', r'', cleaned)
            
            #parsed_array.append(cleaned)
            parsed += f"{cleaned}\n\n"
        return parsed
    else:
        return 'None'

def parse_pt_1 (response, word=None):    # PT: Priberam  mono-lingual
    """
    :param response:    text response from the original lookup query to the mapped online dictionary 
    :param word:        word that was looked up (is used in some regex below) 
    :return cleaned:    text string containing the dictionary definitions parsed from the response 
    """
    soup = bs(response, 'html.parser')

    # identify main content section
    definition_section = soup.find(id='main-container')
    if not definition_section:
        return 'None'
    else:
        cleaned = definition_section.get_text(separator=" ", strip=True)
        pattern = f'^O verbete não foi encontrado'
        if re.match(pattern, cleaned):
            return 'None'
        pattern = r'\bacepç(ão|ões)\b\s+(\d+)((\s+a\s+)(\d+))?'                         # pattern to mask numbers that are rerferences to previous definitions
        cleaned = re.sub(pattern, r'acepç\1 _\2_\4_\5_', cleaned, flags=re.IGNORECASE)  # used here ....
        cleaned = re.sub(r'(\b\d\d?) ', r'\n\n\1. ', cleaned, flags=re.IGNORECASE)      # add new line and a '.' to each new numbered definition
        cleaned = re.sub(r'_(\d\d?)_', r'\1', cleaned, flags=re.IGNORECASE)             # clean up the masking from before
        cleaned = re.sub(r'__', r'', cleaned)                                           # dto.
        cleaned = re.sub(rf'({word[:-1]}..?s s(f|m) pl)', r'\n\n\1:', cleaned, flags=re.IGNORECASE) # catch the plurals section and have start with a new line
        cleaned = re.sub(r'(\p{Lu}{5,})', r'\n\n\1\n', cleaned)             # separate additional sections that are identified by capitalized headersgex as re
    return cleaned 