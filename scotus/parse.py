# Copyright (c) 2018  Floyd Terbo

import json
import logging
import os
import os.path
import sys
import time
import unicodedata

import PyPDF2

# Translation table to strip unicode punctuation, but not things like section symbols
TTABLE = { i:None for i in xrange(sys.maxunicode)
           if unicodedata.category(unichr(i)).startswith('P') }

# For some reason PyPDF2 resolves some text to the wrong code points
TTABLE[8482] = None # Single quotes
TTABLE[64257] = None  # Double quote open
TTABLE[64258] = None  # Double quote close
TTABLE[339] = None  # Endash
TTABLE[352] = None  # Emdash

def indexDir (path, force_pdf = False):
  logging.info("Indexing %s" % (path))
  fnames = [x for x in os.listdir(path) if x[-4:] == ".pdf"]

  indexes = {}
  for name in fnames:
    try:
      grams = {}
      txtpath = "%s/%s.txt" % (path, name[:-4])
      if os.path.exists(txtpath) and not force_pdf:
        with open(txtpath, "r") as word_file:
          words = word_file.read().split()
      else:
        with open("%s/%s" % (path, name), "rb") as fo:
          t0 = time.time()
          reader = PyPDF2.PdfFileReader(fo)
          words = []
          for page in range(reader.numPages):
            try:
              clean_text = reader.getPage(page).extractText().translate(TTABLE).lower()
              words.extend(clean_text.split())
            except KeyError:  # Some PDF pages don't have /Contents
              continue
          with open(txtpath, "w+") as dtxt:
            dtxt.write(u" ".join(words).encode('utf-8'))
          logging.debug("Parsing (%s) took %0.2f seconds" % (name, time.time() - t0))

      grams["1-gram"] = ngrams(words, 1)
      grams["2-gram"] = ngrams(words, 2)
      grams["3-gram"] = ngrams(words, 3)
      indexes[name] = grams
    except PyPDF2.utils.PdfReadError:
      continue

  with open("%s/indexes.json" % (path), "w+") as ij:
    logging.debug("Writing index json (%s)" % (path))
    ij.write(json.dumps(indexes))

    
def ngrams (wlist, n):
  output = {}
  for i in range(len(wlist)-n+1):
    gram = ' '.join(wlist[i:i+n])
    output.setdefault(gram, 0)
    output[gram] += 1
  return output

