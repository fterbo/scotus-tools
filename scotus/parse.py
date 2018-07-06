# Copyright (c) 2018  Floyd Terbo

import json
import logging
import os
import os.path
import sys
import time
import unicodedata

import PyPDF2

JUSTICES = { 17 : set([u"ROBERTS,", u"GINSBURG,", u"KENNEDY,", u"THOMAS,", u"ALITO,",
                       u"GORSUCH,", u"SOTOMAYOR,", u"KAGAN,", u"BREYER,"])}

def getPuncFilter (tt = {}):
  if not tt:
    # Translation table to strip unicode punctuation, but not things like section symbols
    tt = { i:None for i in xrange(sys.maxunicode)
               if unicodedata.category(unichr(i)).startswith('P') }

    # For some reason PyPDF2 resolves some text to the wrong code points
    tt[8482] = None # Single quotes
    tt[64257] = None  # Double quote open
    tt[64258] = None  # Double quote close
    tt[339] = None  # Endash
    tt[352] = None  # Emdash
  return tt

def getFixTable (tt = {}):
  if not tt:
    tt = { i:None for i in xrange(sys.maxunicode)
               if unicodedata.category(unichr(i)).startswith('P') }
    del tt[0x2E]
    del tt[0x2C]
    del tt[0x3B]
    del tt[0x2024]
    del tt[0x2027]
    tt[0x152] = ord("-")
    tt[0x153] = ord('-')
    tt[0x160] = ord('-')
    tt[0x201D] = ord('"')
    tt[0x201C] = ord('"')
    tt[0x2122] = ord("'")
    tt[0xFB01] = ord('"')
    tt[0xFB02] = ord('"')
  return tt



def getPdfWords (path, translate = getPuncFilter):
  import PyPDF2

  tt = translate()
  wd = {}
  with open(path, "rb") as fo:
    reader = PyPDF2.PdfFileReader(fo, strict=False)
    for pno,page in enumerate(range(reader.numPages)):
      try:
        clean_text = reader.getPage(page).extractText().translate(tt)
        wd[pno] = clean_text.split()
      except KeyError: # Some PDF pages don't have /Contents
        continue
  return wd


def indexDir (path, force_pdf = False):
  logging.info("Indexing %s" % (path))
  fnames = [x for x in os.listdir(path) if x[-4:] == ".pdf"]
  tt = getPuncFilter()

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
              clean_text = reader.getPage(page).extractText().translate(tt).lower()
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

def getDisposition(path):
  f = open(path, "rb")
  reader = PyPDF2.PdfFileReader(f)
  tt = getFixTable()
  for idx in range(reader.numPages):
    text = reader.getPage(idx).extractText().translate(tt)
    if text.count("Opinion of"):
      disp_pno = idx - 1
      break

  text = reader.getPage(disp_pno).extractText().translate(tt)
  start = False
  dpt = []
  tlist = "".join(text.split("\n")).split()
  tabr = set([u"C. J.,", u"J.,", u"C."])
  for idx,word in enumerate(tlist):
    if word in JUSTICES[17] and tlist[idx+1] in tabr:
      start = True
    if start:
      dpt.append(word)

  return " ".join(dpt)


def getQP (path):
  starts = ["QUESTION", "QUESTIONS"]
  ends = {"TABLE" : ["OF", "CONTENTS"],
          "PARTIES" : ["TO"],
          "CORPORATE" : ["DISCLOSURE", "STATEMENT"],
          "LIST" : ["OF", "PARTIES"]}
  qptext = []

  wps = getPdfWords(path, getFixTable)
  inq = False
  inqp = False
  for pno,pagewords in wps.items():
    for idx,word in enumerate(pagewords):
      if inqp:
        if word in ends.keys():
          nxt = ends[word]
          match = True
          for nidx,term in enumerate(nxt, 1):
            if pagewords[idx+nidx] != term:
              match = False
          if match:
            return qptext
        qptext.append(word)
      elif inq:
        if word == "PRESENTED":
          inqp = True
        else:
          inq = False
      elif word in starts:
        inq = True