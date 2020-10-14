#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SolveCryptogram Twitter bot reply constructor v0.08 published 14 Oct 20

         1         2         3         4         5         6         7         8
12345678901234567890123456789012345678901234567890123456789012345678901234567890
Author: @rsnbrgr
License: GPL v3.0
GitHub: https://github.com/rsnbrgr/SolveCryptogram
Wiki: https://github.com/rsnbrg/SolveCryptogram/wiki
Wrapper for GitHub project: https://github.com/aquach/cryptogram-solver

PROGRAMMING DECISIONS:
This program wraps logic around the SubSolver project by "aquach".  It takes text
from a tweet and returns a string that is tweet-ready for a reply.  We leave it to
the calling module to actually tweet the reply.

If this module returns a blank string, then it either found no work to do -- or
it couldn't perform a function for some reason.

If you run this module as __main__, it will perform logic tests to confirm
everything works.

PYTHON 2.7 vs. PYTHON 3.8:
Back in the days when I wrote all my 'bots in v2.7, I simply imported aquach's
module and called its methods.  Poof magic, everything worked like a champ.

And then I upgraded all my 'bots to v3.x.  Python's "2to3" encounters error #22
when it tries to upgrade aquach's SubSolver module to v3.x.  This forced me to
write a bash file so I can call it via a subprocess.run().  This module now writes
to cryptogram.txt; then it reads plaintext.txt or substitutions.txt depending on
the keyword a user specified in their tweet.

Again, big kudos to "aquach" for his great work!  I'm waaaaay too lazy to write
it myself :-)
"""

# We do some interesting IMPORTs here
import logging
if __name__ == "__main__":
    logging.basicConfig(filename = "SolveCryptogram.log",
                        format = "%(asctime)s %(levelname)s: %(message)s",
                        level = 11)
    logging.info(("\n"+("="*80))*2)
import random
import string
import subprocess

# We MUST know where the sub_solver launcher & other files reside!
BashSolver = "/home/rob/.local/lib/python2.7/site-packages/CryptoSolver"
CryptoFile = "/home/rob/.local/lib/python2.7/site-packages/cryptogram.txt"
PlTxtFile  = "/home/rob/.local/lib/python2.7/site-packages/plaintext.txt"
SubstiFile = "/home/rob/.local/lib/python2.7/site-packages/substitutions.txt"

SortedAlphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

KeyWordHelp     = "help"
KeyWordDecipher = "decipher:"
KeyWordDecypher = "decypher:"
KeyWordEncipher = "encipher:"
KeyWordEncypher = "encypher:"
KeyWordSolve    = "solve:"
AllKeyWords     = {KeyWordHelp,
                   KeyWordDecipher,
                   KeyWordDecypher,
                   KeyWordEncipher,
                   KeyWordEncypher,
                   KeyWordSolve}


# Tweet processing strings
ProcessHelpRequest = """These commands must include a colon:
\n"solve: {cryptogram}" -> solution set
"decypher: {cryptogram}" -> plaintext
\nSee http://github.com/rsnbrgr/SolveCryptogram/wiki/SolveCryptogram for more
"""
ProcessFailedToSolveCryptogram  = "Sorry, I couldn't solve your cryptogram.\n\nDid you accidentally include NON-cryptogram text after the keyword 'solve:'?"
ProcessSnarkedToSolveCryptogram = "Sorry, I couldn't decypher {0}'s cryptic tweet because it fails the test of logical reasoning. Did you quote it in context?"


# Logging strings
LogInfoNoKeywordsInText            = "No keywords in text"
LogInfoTooManyKeywords             = "Twitter user's SolveCryptogram request specified too many keywords"
LogErrorImpossiblyNegativeKeywords = "TotalKeywordsIn() returned a negative value"


TestStrings = [
    """@SolveCryptogram Please help
    """,

    """@SolveCryptogram Please encipher: "I think, therefore I am." Rene Descartes
    """,

    """@SolveCryptogram Please encypher: "I think, therefore I am." Rene Descartes
    """,

    """Check out @SolveCryptogram for commands like "solve:" and "decypher:".  Learn more by sending a tweet to @SolveCryptogram with the word "help" in it 
    """,

    """@SolveCryptogram Please solve:
    "X QXMXSABC CWBK GXU QB KEB QBLK GBCWAWSB. W OXL BXKWSV KPP GHAE VPPC BXKL. QHK ZBPZMB APSLWCBF KEXK ZXFK PJ UPHF RPQ, UPH YSPO? BXK. XSC W CP!" - XMKPS QFPOS
    """,

    """@SolveCryptogram Please decipher:
    "X QXMXSABC CWBK GXU QB KEB QBLK GBCWAWSB. W OXL BXKWSV KPP GHAE VPPC BXKL. QHK ZBPZMB APSLWCBF KEXK ZXFK PJ UPHF RPQ, UPH YSPO? BXK. XSC W CP!" - XMKPS QFPOS
    """,

    """@SolveCryptogram Please decypher:
    "X QXMXSABC CWBK GXU QB KEB QBLK GBCWAWSB. W OXL BXKWSV KPP GHAE VPPC BXKL. QHK ZBPZMB APSLWCBF KEXK ZXFK PJ UPHF RPQ, UPH YSPO? BXK. XSC W CP!" - XMKPS QFPOS
    """
    ]

def WriteStringToCryptoFile(ThisString):
    """Overwrites the cryptogram.txt file with a string of your choice
    
    Returns True if successful, else obviously it returns False
    """
    
    try:
        with open(CryptoFile, "w") as f:
            f.write(ThisString)
        return True
    except:
        logging.error("WriteStringToCryptoFile returned an error")
        return False

def ReadStringsFromSolutionFile(ThisFilename):
    """Reads the given file, returning it as a list of strings
    
    A null list indicates some sort of failure
    """
    
    try:
        with open(ThisFilename, "r") as f:
            return f.readlines()
    except:
        logging.error("ReadStringsFromSolutionsFile returned an error")
        return []

def ValidRandomAlphabet():
    """Returns a random alphabet making sure no letter represents itself

    CREDIT WHERE DUE: contributor Mark Byers at
    https://stackoverflow.com/questions/2668312/shuffle-string-in-python
    """
    Validated = False
    while not Validated:
        # We begin by assuming valid until proven otherwise
        Validated = True

        RandomAlphabet = list(SortedAlphabet)
        random.shuffle(RandomAlphabet)
        RandomAlphabet = ''.join(RandomAlphabet)

        for x in range(len(SortedAlphabet)):
            if SortedAlphabet[x] == RandomAlphabet[x]:
                Validated = False
                break
    # The while loop has validated a randomized alphabet, so...
    return RandomAlphabet


def TotalKeywordsIn(ThisString):
    """Counts each keyword in the string you provide.

    A properly constructed request contains one keyword.  If it contains
    more, well, it's not a valid syntax.  If it contains none, then it's
    probably just a reply to a tweet we previously sent or maybe it's
    someone telling another person about @SolveCryptogram.  If it contains
    multiple keywords, then it might be someone copying our help text in a
    reply to someone else.
    """
    TotalKeyWords = 0
    for kw in AllKeyWords:
        if kw in ThisString:
            TotalKeyWords += 1
    return TotalKeyWords
    

def ProcessCryptogramRequest(TweetFullText):
    """Calls the appropriate function based on the user's request
    """
    # Pre-process the tweet's text
    CryptogramText = TweetFullText.lower()
    logging.info(CryptogramText)
    if (TotalKeywordsIn(CryptogramText) < 0):
        logging.error(LogErrorImpossiblyNegativeKeywords)
        return ""
    elif (TotalKeywordsIn(CryptogramText) == 0):
        logging.info(LogInfoNoKeywordsInText)
        return ""
    elif (TotalKeywordsIn(CryptogramText) == 1):
        if KeyWordHelp in CryptogramText:
            return ProcessHelpRequest
        elif (KeyWordDecipher in CryptogramText) or (KeyWordDecypher in CryptogramText):
            return Decypher(CryptogramText)
        elif (KeyWordEncipher in CryptogramText) or (KeyWordEncypher in CryptogramText):
            return Encypher(CryptogramText)
        elif KeyWordSolve in CryptogramText:
            return Solve(CryptogramText)
        else:
            return ""
    else:
        logging.info(LogInfoTooManyKeywords)
        return ""


def Decypher(CryptogramText):
    # Remove everything up to the keyword "decipher:" OR "decypher:"
    logging.debug("REQUEST: " + CryptogramText)
    if KeyWordDecipher in CryptogramText:
        CryptogramText = CryptogramText[(CryptogramText.find(KeyWordDecipher)+len(KeyWordDecipher)):].strip()
    if KeyWordDecypher in CryptogramText:
        CryptogramText = CryptogramText[(CryptogramText.find(KeyWordDecypher)+len(KeyWordDecypher)):].strip()

    # Now let's remove any excess whitespace & EOLs
    CryptogramText = " ".join(CryptogramText.split())
    logging.debug("STRIPPED TO: " + CryptogramText)

    # Let's solve this cryptogram!
    if WriteStringToCryptoFile(CryptogramText):
        subprocess.run(BashSolver)
        DecypherList = ReadStringsFromSolutionFile(PlTxtFile)
        logging.debug(DecypherList)
        if DecypherList:
            return DecypherList[0]
        else:
            return ProcessFailedToSolveCryptogram
    else:    
        return ProcessFailedToSolveCryptogram


def Solve(CryptogramText):
    # Remove everything up to the keyword "solve:".  Note that our own
    # Twitter handle contains the word "solve", hence we need to find a
    # colon!
    logging.debug("REQUEST: " + CryptogramText)
    CryptogramText = CryptogramText[(CryptogramText.find(KeyWordSolve)+len(KeyWordSolve)):].strip()
    
    # Now let's remove any excess whitespace & EOLs
    CryptogramText = " ".join(CryptogramText.split())
    logging.debug("STRIPPED TO: " + CryptogramText)

    # Let's solve this cryptogram!
    if WriteStringToCryptoFile(CryptogramText):
        subprocess.run(BashSolver)
        SubstitutionList = ReadStringsFromSolutionFile(SubstiFile)
        logging.debug(SubstitutionList)
        if SubstitutionList:
            TweetString = "Try these substitutions:\n"
            for x in SubstitutionList:
                TweetString += '\n' + x.strip()
            return TweetString
        else:
            return ProcessFailedToSolveCryptogram
    else:    
        return ProcessFailedToSolveCryptogram


def Encypher(PlainText):
    # Remove everything up to the keyword "encypher:" or encipher:"
    logging.debug("REQUEST: " + PlainText)
    if KeyWordEncipher in PlainText:
        PlainText = PlainText[(PlainText.find(KeyWordEncipher)+len(KeyWordEncipher)):].strip()
    if KeyWordEncypher in PlainText:
        PlainText = PlainText[(PlainText.find(KeyWordEncypher)+len(KeyWordEncypher)):].strip()
    logging.debug("STRIPPED TO: " + PlainText)

    # Convert PlainText to lowercase
    PlainText = PlainText.lower()
    # Convert RandomAlphabet to uppercase
    RandomAlphabet = ValidRandomAlphabet().upper()

    # Replace all PlainText letters with their encyphers
    EncypherText = str(PlainText)
    for x in range(len(SortedAlphabet)):
        EncypherText = EncypherText.replace(SortedAlphabet[x].lower(),
                                            RandomAlphabet[x])
    return EncypherText


def main():
    for TestString in TestStrings:
        print("REQUEST:\n{0}".format(TestString))
        print("REPLY:\n{0}".format(ProcessCryptogramRequest(TestString)))
        print("="*80, "\n\n")

if __name__ == "__main__":
    main()
