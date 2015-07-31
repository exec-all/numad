# numad #
ncurses interface to elastic search

## Features ##
 * Type ahead searching (searches on every key push
 * Curses interface
 * Search runs in background and does not block input

## TODO ##
 * Caching of results
 * Caching and intergration of partial results as an interum mesure until real 
   request arrives back
 * Split of GUI stuff into seeprate lib for reuse

## History ##
Anchor dumps all its info into a search engine called 'umad' written in python 
and backed by elastic search. Pulling this info out was done via a web 
interface that while simple, still took longer than 'instant' to render. this 
was further magnified by the use of a weak cpu and a cpu hungry web browser.

to remedy this and make an interface that could be used nicely by ssh'ing into 
a box, a ncurses client was created. as this had no hard dependencies on 
internal things and was basically a generic interface to elastic search it made 
more sense to make it available to a wider audience rather than keep it 
internal and have one or two people use it
