# kindle2anki
Create Anki Card Decks from Kindle vocab.db

This little project helps avid language learners to create Anki Card Decks for the vocabulary they looked up from Kindle E-Books (from dictioinaries installed within Kindle). Kindle stores these look-ups within an internal sqlite3 database and offers basic flash-card study functionality to review the vocabluary however without the spaced repetition algorithm implemented.

The project contains two files:

1. **kindle2anki.py**:
   The main program: 
   - queries the kindle vocab.db for books that contain words that where looked up from within kindle
   - has you select a book for which you want to extract the vocabluary and create a card deck
   - has you select a dictionary from a choice of configured dictionaries for the language of the chosen book
   - has you select a card type: 
    Type 'A' Front: looked up word with enclosing text passage from kindle book / Back: dictionary definitions of word
    Type 'B' Front: dicionary definitions of word / Back: word and text enclosing text passage from kindle book
   - looks up the word definitions from chosen online dictionary
   - creates card deck with one card of the chosen type with one card for each word from the looked-up words of the chosen book
   
2. **k2a_response_parsers.py**:
   contains customized parser functions, one for each online dictionary that extract the dictionary definitions for the looked-up words
   from the https responses of the dicionary websites. These functions are selected and called by the main program depending on what
   online dictionary the user has selected. They may become disfunctional (i.e. require updating) if a site operator changes the document structure
   of their responses to dictionary queries.

Howto use:
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
