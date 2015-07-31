#!/usr/bin/env python
"""render: code that deals with putting the data directly on to the terminal"""

def render_search_results(term, results):
	if results:
		# 2's here come from search fields plus bars (------)
		# 3 ifs fromt he fact that each search result is 2 fields of data
		# plus a bar (--------)
		results = results[:(term.height - 2 - 2 - 2)//3]


		# We want to list all the datastores we retrived info from
		# as we would like to be able to deselect irrelevent data stores
		# in the future
		categories = {result['type'] for result in results}

		# Move to top os search results area
		print(term.move(2,0))
		print(term.clear_eos, end='')

		# Populate categories section with a faked up checkbox
		for category in sorted(categories):
			print("(x) {} ".format(category), end='')
		print()

		# bar code
		print(term.move(3,0))
		print("=" * term.width)

		# move to results area and start rendering
		print(term.move(4,0))
		for result in results:
			print(result['title'], end='')
			print(term.move_x(term.width - len(result['type'])), end='')
			print(result['type'])
			print("URL: {}".format(result['url']))
			print("-" * term.width)
	else:
		# Make 'no data' clear the display rather than have a seperate clear function
		print(term.move(2,0))
		print(term.clear_eos, end='')
		print(term.move(3,0))
		print("=" * term.width)

def render_query_field(term, query):
	if query is not None:
		# Pre calculate the display string as there once was a time we needed its
		# length for rendering purposes
		search_line = "{t.bold}Search{t.normal}: {query}".format(t=term, query=query)

		print(term.move(0, 0))
		# ensure we clear away old text as if backspace is hit
		# new text will be shorter than old text and data may be
		# present on the terminal
		print(term.clear_eol, end='')
		print(search_line, end='')

		# bar code (just rolls off the tounge)
		print(term.move(1, 0))
		print("=" * term.width, end='')
