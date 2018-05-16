# scotus-tools

Basic tools for working with the new electronic docket available at the United States Supreme Court.

There are no real docs here, but a brief rundown of each tool is below:

* `ordergrab`

Downloads all orders for a given term.

* `orderparse`

Provides some really horrible PDF parsing that allows you to search orders by section.

* `docketgrab`

Downloads all petitions for dockets after the given number, or all documents for a specific docket.

* `docketindexer`

Parses all docket PDFs that are present on your system and produces unigram and bigram indexes for
fast(ish) searches.

* `docketsearch`

Searches docket filings for the query term specified.

In general all tools that download files will be smart and not download files you already have (based on
using a common `root` directory, which is `.` by default).  Most tools support optionally operating in
parallel for faster processing.


None of this code pretends to be good or efficient.
