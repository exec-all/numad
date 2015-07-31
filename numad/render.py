#!/usr/bin/env python
"""render: code that deals with putting the data directly on to the terminal"""

def render_search_results(term, results):
	if results:
		results = results[:(term.height - 2 - 2 - 2)//3]

		categories = {result['type'] for result in results}

		print(term.move(2,0))
		print(term.clear_eos, end='')

		for category in sorted(categories):
			print("(x) {} ".format(category), end='')
		print()

		print(term.move(3,0))
		print("=" * term.width)

		print(term.move(4,0))
		for result in results:
			print(result['title'], end='')
			print(term.move_x(term.width - len(result['type'])), end='')
			print(result['type'])
			print("URL: {}".format(result['url']))
			print("-" * term.width)
	else:
		print(term.move(2,0))
		print(term.clear_eos, end='')
		print(term.move(3,0))
		print("=" * term.width)

def render_query_field(term, query):
	if query is not None:
		search_line = "{t.bold}Search{t.normal}: {query}".format(t=term, query=query)

		print(term.move(0, 0))
		print(term.clear_eol, end='')
		print(search_line, end='')

		print(term.move(1, 0))
		print("=" * term.width, end='')
