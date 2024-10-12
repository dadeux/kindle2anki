# separate file containing the dictionary definitions to avoid the mail program getting to clunky
# contains one function that returns an array of dicts for dictionaries per language .
#  
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
            {   
                'id': 5,       
                'src_lang': 'en',
                'dst_lang': 'fr',
                'name': 'Linguee',
                'desc': 'bi-lingual EN->FR',
                'url': 'https://www.linguee.com/english-french/translation/',
                'referer': 'https://www.linguee.com'
            },
            {   
                'id': 6,       
                'src_lang': 'en',
                'dst_lang': 'es',
                'name': 'Linguee',
                'desc': 'bi-lingual EN->ES',
                'url': 'https://www.linguee.com/english-spanish/translation/',
                'referer': 'https://www.linguee.com'
            },
            {   
                'id': 7,       
                'src_lang': 'en',
                'dst_lang': 'pt',
                'name': 'Linguee',
                'desc': 'bi-lingual EN->PT',
                'url': 'https://www.linguee.com/english-portuguese/translation/',
                'referer': 'https://www.linguee.com'
            },
            {   
                'id': 8,       
                'src_lang': 'en',
                'dst_lang': 'de',
                'name': 'Linguee',
                'desc': 'bi-lingual EN->DE',
                'url': 'https://www.linguee.com/english-german/translation/',
                'referer': 'https://www.linguee.com'
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
            {   
                'id': 2,       
                'src_lang': 'fr',
                'dst_lang': 'en',
                'name': 'Larousse',
                'desc': 'bi-lingual FR->EN',
                'url': 'https://www.larousse.fr/dictionnaires/francais-anglais/',
                'referer': 'https://www.larousse.fr'
            },
            {   
                'id': 3,       
                'src_lang': 'fr',
                'dst_lang': 'de',
                'name': 'Larousse',
                'desc': 'bi-lingual FR->DE',
                'url': 'https://www.larousse.fr/dictionnaires/francais-allemand/',
                'referer': 'https://www.larousse.fr'
            },
            {   
                'id': 4,       
                'src_lang': 'fr',
                'dst_lang': 'es',
                'name': 'Larousse',
                'desc': 'bi-lingual FR->ES',
                'url': 'https://www.larousse.fr/dictionnaires/francais-espagnol/',
                'referer': 'https://www.larousse.fr'
            },
            {   
                'id': 5,       
                'src_lang': 'fr',
                'dst_lang': 'en',
                'name': 'Linguee',
                'desc': 'bi-lingual FR->EN',
                'url': 'https://www.linguee.com/french-english/translation/',
                'referer': 'https://www.linguee.com'
            },
            {   
                'id': 6,       
                'src_lang': 'fr',
                'dst_lang': 'es',
                'name': 'Linguee',
                'desc': 'bi-lingual FR->ES',
                'url': 'https://www.linguee.com/french-spanish/translation/',
                'referer': 'https://www.linguee.com'
            },
            {   
                'id': 7,       
                'src_lang': 'fr',
                'dst_lang': 'pt',
                'name': 'Linguee',
                'desc': 'bi-lingual FR->PT',
                'url': 'https://www.linguee.com/french-portuguese/translation/',
                'referer': 'https://www.linguee.com'
            },
            {   
                'id': 8,       
                'src_lang': 'fr',
                'dst_lang': 'de',
                'name': 'Linguee',
                'desc': 'bi-lingual FR->DE',
                'url': 'https://www.linguee.com/french-german/translation/',
                'referer': 'https://www.linguee.com'
            },
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
            {   
                'id': 2,       
                'src_lang': 'es',
                'dst_lang': 'fr',
                'name': 'Larousse',
                'desc': 'bi-lingual ES->FR',
                'url': 'https://www.larousse.fr/dictionnaires/espagnol-francais/',
                'referer': 'https://www.larousse.fr'
            },
            {   
                'id': 3,       
                'src_lang': 'es',
                'dst_lang': 'en',
                'name': 'Linguee',
                'desc': 'bi-lingual ES->EN',
                'url': 'https://www.linguee.com/spanish-english/translation/',
                'referer': 'https://www.linguee.com'
            },
            {   
                'id': 4,       
                'src_lang': 'es',
                'dst_lang': 'fr',
                'name': 'Linguee',
                'desc': 'bi-lingual ES->FR',
                'url': 'https://www.linguee.com/spanish-french/translation/',
                'referer': 'https://www.linguee.com'
            },
            {   
                'id': 5,       
                'src_lang': 'es',
                'dst_lang': 'pt',
                'name': 'Linguee',
                'desc': 'bi-lingual ES->PT',
                'url': 'https://www.linguee.com/spanish-portuguese/translation/',
                'referer': 'https://www.linguee.com'
            },
            {   
                'id': 6,       
                'src_lang': 'es',
                'dst_lang': 'de',
                'name': 'Linguee',
                'desc': 'bi-lingual ES->DE',
                'url': 'https://www.linguee.com/spanish-german/translation/',
                'referer': 'https://www.linguee.com'
            },
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
            {   
                'id': 2,       
                'src_lang': 'pt',
                'dst_lang': 'en',
                'name': 'Linguee',
                'desc': 'bi-lingual PT->EN',
                'url': 'https://www.linguee.com/portuguese-english/translation/',
                'referer': 'https://www.linguee.com'
            },
            {   
                'id': 3,       
                'src_lang': 'pt',
                'dst_lang': 'fr',
                'name': 'Linguee',
                'desc': 'bi-lingual PT->FR',
                'url': 'https://www.linguee.com/portuguese-french/translation/',
                'referer': 'https://www.linguee.com'
            },
            {   
                'id': 4,       
                'src_lang': 'pt',
                'dst_lang': 'es',
                'name': 'Linguee',
                'desc': 'bi-lingual PT->ES',
                'url': 'https://www.linguee.com/portuguese-spanish/translation/',
                'referer': 'https://www.linguee.com'
            },
            {   
                'id': 5,       
                'src_lang': 'pt',
                'dst_lang': 'de',
                'name': 'Linguee',
                'desc': 'bi-lingual PT->DE',
                'url': 'https://www.linguee.com/portuguese-german/translation/',
                'referer': 'https://www.linguee.com'
            },
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
            {
                'id': 2,       
                'src_lang': 'de',
                'dst_lang': 'fr',
                'name': 'Larousse',
                'desc': 'bi-lingual DE->FR',
                'url': 'https://www.larousse.fr/dictionnaires/allemand-francais/',
                'referer': 'https://www.larousse.fr'
            },
            {   
                'id': 3,       
                'src_lang': 'de',
                'dst_lang': 'en',
                'name': 'Linguee',
                'desc': 'bi-lingual DE->EN',
                'url': 'https://www.linguee.com/german-english/translation/',
                'referer': 'https://www.linguee.com'
            },
            {   
                'id': 4,       
                'src_lang': 'de',
                'dst_lang': 'fr',
                'name': 'Linguee',
                'desc': 'bi-lingual DE->FR',
                'url': 'https://www.linguee.com/german-french/translation/',
                'referer': 'https://www.linguee.com'
            },
            {   
                'id': 5,       
                'src_lang': 'de',
                'dst_lang': 'es',
                'name': 'Linguee',
                'desc': 'bi-lingual DE->ES',
                'url': 'https://www.linguee.com/german-spanish/translation/',
                'referer': 'https://www.linguee.com'
            },
            {   
                'id': 6,       
                'src_lang': 'de',
                'dst_lang': 'pt',
                'name': 'Linguee',
                'desc': 'bi-lingual DE->PT',
                'url': 'https://www.linguee.com/german-english/translation/',
                'referer': 'https://www.linguee.com'
            },
        ]
    }
    if lang in list(dictionaries.keys()):
        return dictionaries[lang]
    else:
        raise ValueError("Invalid Language")