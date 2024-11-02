from bs4 import BeautifulSoup as bs
import unicodedata
import regex as re
# each parser function defined maps to a specific online dictionary
# the mapping is via the parser function naming as 'parse_' + {lang} + {dictionary ID}
# e.g. function 'parse_en_1' maps to the first (id '1') English (lang 'en') dictionary defined.
# The available dictionaries are defined within the kindle2anki.getDictioaries() function
# 
def clean(soup_object):
    cleaned = soup_object.get_text(separator=" ",strip=True)
    cleaned = unicodedata.normalize('NFC', cleaned)
    return cleaned

def parse_larousse_generic (response, word=None):    # generic parser for Larousse bi-lingual dictionaries
    """
    :param response:    text response from the original lookup query to the mapped online dictionary 
    :param word:        looked-up word, not needed in most parsers, but included to allow for uniform call across functions
    :return parsed:     text string containing the dictionary definitions parsed from the response 
    """
    # identify main content section
    soup = bs(response, 'html.parser')
    parsed = ""
    definition_section = soup.find(id='BlocArticle')

    if not definition_section:
        return "None"
    
    ze = definition_section.find_all(class_='ZoneEntree')
    zt = definition_section.find_all(class_='ZoneTexte')

    l_ze = len(ze)
    l_zt = len(zt)

    if l_ze == l_zt:
        l = l_ze
        diff = 0
    elif l_ze > l_zt:
        l = l_ze
        diff = l_ze - l_zt
    else:
        l = l_zt
        diff = l_zt - l_ze

    ZE = {}
    ZT = {}

    for i in range(l):
        if i < l_ze:
            header = ze[i]  # header section
            # extract header info (e.g. is adjective, or noun etc.)
            cleaned = clean(header)
            cleaned = re.sub(r'Conjugaison\s?', '', cleaned)
            entry = f'\n{cleaned}\n\n'
            
            if l_ze >= l_zt:
                ZE[i] = entry
            else:
                if i + diff <= l:
                    ZE[i + diff] = entry
                if i not in ZE.keys():
                    ZE[i] = ""
        else:
            ZE[i] = ""

        # get definitions for associated with header info
        if i < l_zt:
            text = zt[i]
            items = text.find_all(class_='itemZONESEM')
            entry = ""
            if not items:
                cleaned = clean(text)
                cleaned = re.sub(r'Conjugaison\s?', '', cleaned)
                entry = f'{cleaned}\n'
            else:
                for idx, item in enumerate(items, 1):
                    cleaned = clean(item)
                    cleaned = re.sub(r'Conjugaison\s?', '', cleaned)
                    cleaned = re.sub(r'(\[)(\w+)(\s-\s)', r'\2\n[',cleaned)
                    cleaned = re.sub(r'\s\[\s-\s', r'\n[',cleaned)
                    if idx == 1:
                        entry += f'{idx}. {cleaned}\n'
                    else:
                        entry += f'\n{idx}. {cleaned}\n'
            
            if l_ze > l_zt:
                if i + diff <= l:
                    ZT[i + diff] = entry
                if i not in ZT.keys():
                    ZT[i] = ""
            else:
                ZT[i] = entry
        else:
            if not ZT[i]:
                ZT[i] = ""

    for i in range(l):
        parsed += ZE[i]
        parsed += ZT[i]

    return parsed

# the following aliases support a uniform calling of the parser functions as 'parse_<lang>_<id>'
parse_en_3 = parse_larousse_generic      # EN: Larousse EN->FR (aliased to parse_larousse_generic) 
parse_fr_2 = parse_larousse_generic      # FR: Larousse FR->EN (aliased to parse_larousse_generic) 
parse_fr_3 = parse_larousse_generic      # FR: Larousse FR->DE (aliased to parse_larousse_generic) 
parse_fr_4 = parse_larousse_generic      # FR: Larousse FR->ES (aliased to parse_larousse_generic) 
parse_es_2 = parse_larousse_generic      # ES: Larousse ES->FR (aliased to parse_larousse_generic) 
parse_de_2 = parse_larousse_generic      # DE: Larousse DE->FR (aliased to parse_larousse_generic)

def parse_linguee_generic(response, word=None):     # generic parser for Linguee bi-lingual dictionaries
    soup = bs(response, 'html.parser')
    parsed = ""
    # get main section containing definitions and examples
    main_section = soup.find(class_='isMainTerm')
    if not main_section:
        return "None"

    # get definitions
    definitions_section = main_section.find(class_='exact')
    if definitions_section:
        main_definitions = definitions_section.find_all(class_='translation sortablemg featured')
        ld = len(main_definitions)

        # main definitions with desccription and examples 
        for xd, definition in enumerate(main_definitions, 1):
            # extract actual definition and add to output
            d_desc = definition.find(class_='translation_desc')
            if ld == 1:
                parsed += f'{clean(d_desc)}\n'
            else:
                if xd == 1:
                    parsed += f'{xd}. {clean(d_desc)}\n'
                else:
                    parsed += f'\n{xd}. {clean(d_desc)}\n'
            # extract examples for definition and add to output
            d_examples = definition.find(class_='example_lines')
            if d_examples:
                examples = d_examples.find_all(class_='example line')
                le = len(examples)   
                for xe, example in enumerate(examples,1):
                    s_text = clean(example.find(class_='tag_s')) # example text in source language
                    t_text = clean(example.find(class_='tag_t')) # example text in target language
                    if xe == le and xd < ld:                     # last example for this definition and more definitions to come
                        parsed += f'   {s_text} => {t_text}\n'   # add a new line before next definition
                    else:
                        parsed += f'   {s_text} => {t_text}'

        # extract alternative (less common) definitions
        alt = definitions_section.find(class_='translation_group')
        if alt:
            alt = re.sub(r'(less common:)', r'\n\n\1', clean(alt))
            parsed += f'{alt}\n'

        # extract further examples (max 5)
        example_section = main_section.find(class_='example_lines inexact')
        if example_section:
            parsed += '\nExamples:\n'
            examples = example_section.find_all(class_='lemma singleline')
            for idx, example in enumerate(examples, 1):
                if idx > 5:       # no more than 5 examples
                    break
                example = clean(example)
                example = example.replace('-','=>')
                parsed += f'{example}\n'

    return parsed
    
parse_en_5 = parse_linguee_generic      # EN: Linguee EN-FR (aliased to parse_linguee_generic) 
parse_en_6 = parse_linguee_generic      # EN: Linguee EN-ES (aliased to parse_linguee_generic) 
parse_en_7 = parse_linguee_generic      # EN: Linguee EN-PT (aliased to parse_linguee_generic) 
parse_en_8 = parse_linguee_generic      # EN: Linguee EN-DE (aliased to parse_linguee_generic) 

parse_fr_5 = parse_linguee_generic      # FR: Linguee FR-EN (aliased to parse_linguee_generic) 
parse_fr_6 = parse_linguee_generic      # FR: Linguee FR-ES (aliased to parse_linguee_generic) 
parse_fr_7 = parse_linguee_generic      # FR: Linguee FR-PT (aliased to parse_linguee_generic) 
parse_fr_8 = parse_linguee_generic      # FR: Linguee FR-DE (aliased to parse_linguee_generic) 

parse_es_3 = parse_linguee_generic      # ES: Linguee ES-EN (aliased to parse_linguee_generic) 
parse_es_4 = parse_linguee_generic      # ES: Linguee ES-FR (aliased to parse_linguee_generic) 
parse_es_5 = parse_linguee_generic      # ES: Linguee ES-PT (aliased to parse_linguee_generic) 
parse_es_6 = parse_linguee_generic      # ES: Linguee ES-DE (aliased to parse_linguee_generic) 

parse_pt_2 = parse_linguee_generic      # PT: Linguee PT-EN (aliased to parse_linguee_generic) 
parse_pt_3 = parse_linguee_generic      # PT: Linguee PT-FR (aliased to parse_linguee_generic) 
parse_pt_4 = parse_linguee_generic      # PT: Linguee PT-ES (aliased to parse_linguee_generic) 
parse_pt_5 = parse_linguee_generic      # PT: Linguee PT-DE (aliased to parse_linguee_generic) 

parse_de_3 = parse_linguee_generic      # DE: Linguee DE-EN (aliased to parse_linguee_generic) 
parse_de_4 = parse_linguee_generic      # DE: Linguee DE-FR (aliased to parse_linguee_generic) 
parse_de_5 = parse_linguee_generic      # DE: Linguee DE-ES (aliased to parse_linguee_generic) 
parse_de_6 = parse_linguee_generic      # DE: Linguee DE-PT (aliased to parse_linguee_generic) 

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
            cleaned = re.sub(r'(Sin\.:)', r'\n\n   \1 ', cleaned) # list synonymes in new line
            cleaned = re.sub(r'(Ant\.:)', r'\n\n   \1 ', cleaned) # list antonoymes in new line
            cleaned = re.sub(r' \.$', r'', cleaned)           # get rid of trailing " ."
            cleaned = re.sub(r' \d$', r'', cleaned)           # get rid of trailing nummber (from annotations)
            
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

    """
    :param response:    text response from the original lookup query to the mapped online dictionary 
    :param word:        looked-up word, not needed in most parsers, but included to allow for uniform call across functions
    :return parsed:     text string containing the dictionary definitions parsed from the response 
    """
    # identify main content section
    soup = bs(response, 'html.parser')
    parsed = ""
    definition_section = soup.find(id='BlocArticle')

    if not definition_section:
        return "None"
    
    ze = definition_section.find_all(class_='ZoneEntree')
    zt = definition_section.find_all(class_='ZoneTexte')
    #print(f'ZE: {len(ze)}, ZT: {len(zt)}')
    for i in range(len(ze)):
        header = ze[i]  # header section
        text = zt[i]    # definition section
        # extract header info (e.g. is adjective, or noun etc.)
        cleaned = header.get_text(separator=" ",strip=True)
        cleaned = unicodedata.normalize('NFC', cleaned)
        l = len(cleaned)
        if i == 0:
            parsed += f'{cleaned}\n'
        else:
            parsed += f'\n{cleaned}\n'

        parsed += l * '-' + '\n'

        # get definitions for associated with header info
        items = text.find_all(class_='itemZONESEM')
        if not items:
            cleaned = text.get_text(separator=" ",strip=True)
            cleaned = unicodedata.normalize('NFC', cleaned)
            parsed += f'{cleaned}\n'
        else:
            for idx, item in enumerate(items, 1):
                cleaned = item.get_text(separator=" ",strip=True)
                cleaned = unicodedata.normalize('NFC', cleaned)
                cleaned = re.sub(r'(\[)(\w+)(\s-\s)', r'\2\n[',cleaned)
                cleaned = re.sub(r'\s\[\s-\s', r'\n[',cleaned)
                if idx == 1:
                    parsed += f'{idx}. {cleaned}\n'
                else:
                    parsed += f'\n{idx}. {cleaned}\n'
    return parsed 
