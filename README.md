# kindle2anki

**Create _Anki_ card decks from _Kindle_ vocab.db**

This little utility has been created as the final project for my Harvard CS50 Introduction to Programming with Python Course. 
It helps language learners to create Anki Card Decks for the vocabulary they looked up from Kindle E-Books (from dictionaries installed within Kindle). Kindle stores these look-ups within an internal sqlite3 database and offers basic flash-card study functionality to review the vocabluary, however without the spaced repetition algorithm implemented in a fully-fledged flash card application like Anki, that we want to leverage.

The project contains three files:

1. **kindle2anki.py**:
   The main program: 
   - queries the kindle vocab.db for books that contain words that where looked up from within Kindle
   - has you select a book for which you want to extract the looked-up vocabluary and create a card deck
   - has you select a dictionary from a choice of configured dictionaries for the language of the chosen book
   - has you select a card type with two types available:
     - Type 'A' Front: looked up word with enclosing text passage from kindle book / Back: dictionary definitions of word
     - Type 'B' Front: dicionary definitions of word / Back: word and text enclosing text passage from kindle book
   - looks up the word definitions from chosen online dictionary
   - creates card deck with one card of the chosen type with one card for each word from the looked-up words of the chosen book
  
2. **k2a_dictionaries.py**:
   contains dictionary definitions embedded in one single function that returns an a array of dictionaries (datatype), each containing a definintion of
   1 selectable dictionary (online language dictionary) for the source language provided as argument (e.g. 'en' for English, or 'fr' for French)
   for each source language there may be several selectable dictionaries that vary as to Publisher (e.g. Merriam Webster) and Target Language.
   
4. **k2a_response_parsers.py**:
   contains customized parser functions, one for each online dictionary that extract the dictionary definitions for the looked-up words from the https responses of the dicionary websites.
   These functions are selected and called by the main program depending on what online dictionary the user has selected

**How to use:**
  - Connect your Kindle via USB to your computer. The vocab.db can be located at <path_to_mounted_volume>:/system/vocab.db
  - Copy the vocab.db file to a local directory on your computer (perhaps the same directory where the the kindle2anki.py and k2a_response_parsers.py files live)
  - Run the main program (no arguments needed if the all the files live in the same folder), the -h flag displays the usage:

```user@computer Anki Project % **./kindle2anki.py -h** 
usage: kindle2anki.py [-h] [-k K] [-d D] [-l L]

Create Anki card decks from Kindle vocabulary database

options:
  -h, --help  show this help message and exit
  -k K        Path to directory where kindle vocab.db resides, default='.'
  -d D        Name of Anki card deck, default='default.apkg'
  -l L        log level for http(s) sessions, default='WARNING'
```
**Caveats**
- the parser functions will cease to work if the respective Online Dictionary Site Editors decide to change the document structure of their html
- the lookups may cease to work once Online Dictionary Site Administrators implement functionality that bars scripted user agents
- Dictionary site adminstrators may implement limits top the number of queeries they allow from the same source, which may limit limit the size of your card decks and the volume of vocabulary covered in them.
