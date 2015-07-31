#!/usr/bin/env python
"""umad: pull results from umad"""

from argparse import ArgumentParser
from asyncio import coroutine, Task
from aioes import Elasticsearch
from blessed import Terminal

from .render import render_search_results, render_query_field
from .inputs import input_loop, search_loop

from . import DEFAULT_ES_SERVER, UMAD_INDEX, DOC_TYPE_ALL

import asyncio
import sys


@coroutine
def display_loop(term):
	query = ""
	# avoid recreating this all the time due to implicit dns lookups in creation
	es = Elasticsearch(ES_SERVERS)

	loop = asyncio.get_event_loop()

	input = Task(input_loop(loop, term, query))
	search = Task(search_loop(loop, es, query))

	jobs = [input, search]
	
	while True:
		done, pending = yield from asyncio.wait(jobs)
		jobs = []

		if search in done:
			results = search.result()
			render_search_results(term, results)

		if input in done:
			query = input.result()
			render_query_field(term, query)
			input = Task(input_loop(loop, term, query))
			jobs.append(input)

			# we wont be using the results anymore so just discard the worker
			if len(query) > 1:
				search.cancel()
				search = Task(search_loop(loop, es, query))
				jobs.append(search)
			else:
				# force a clear of the results
				render_search_results(term, [])

		sys.stdout.flush()

		jobs += pending


def main(argv=sys.argv[1:]):
	args = ArgumentParser()
	args.add_argument("-s", "--servers", default=DEFAULT_ES_SERVER,
		help='A list of elastic search servers seperated by "," against which to run queries (Default: %(default)s)')
	
	options = args.parse_args(argv)
	
	options.servers = [x.strip() for x in options.servers.split(",")]
	
	loop = asyncio.get_event_loop()
	t = Terminal()
	
	with t.fullscreen():
		with t.cbreak():
			# this blank print statment forces blessings to go to 
			# 'all screen' mode as it wont send output out stdout
			# on its own
			print(t.clear)
			render_query_field(t, "")
			render_search_results(t, [])
	
			sys.stdout.flush()
	
			try:
				loop.run_until_complete(display_loop(t))
			except KeyboardInterrupt:
				print("Exiting")
