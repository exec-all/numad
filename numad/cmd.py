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
def display_loop(term, es_servers):
	"""Starts and waits on inputs, slightly mangles data and sends them to be rendered
	
	This corresponds loosly with an event loop in game programming
	"""
	query = ""
	# avoid recreating this all the time due to implicit dns lookups in creation
	es = Elasticsearch(es_servers)

	loop = asyncio.get_event_loop()

	input = Task(input_loop(loop, term, query))
	search = Task(search_loop(loop, es, query))

	jobs = [input, search]
	
	while True:
		done, pending = yield from asyncio.wait(jobs)
		jobs = []


		# this needs to come before input handling as it may try
		# and cancel a compleated job before its processed. as resuls
		# take a bit to come back its better to just briefly display them
		if search in done:
			results = search.result()
			render_search_results(term, results)

		if input in done:
			query = input.result()
			render_query_field(term, query)
			# we wrap this is a task for the membership query above
			# if we just pass in a corutine, asyncio.wait takes it upon
			# itself to wrap that in a Task and the comparison will always
			# fail
			input = Task(input_loop(loop, term, query))
			jobs.append(input)

			# ES does not return results to us for short queries, so just short
			# circuit them and avoid network traffic
			if len(query) > 1:
				# we wont be using the results anymore so just discard the worker
				search.cancel()
				search = Task(search_loop(loop, es, query))
				jobs.append(search)
			else:
				# force a clear of the results
				render_search_results(term, [])

		sys.stdout.flush()

		# Make sure we resubmit any jobs that have not yet been compleated
		# otherwise we leak them and things go into limbo
		jobs += pending


def main(argv=sys.argv[1:]):
	args = ArgumentParser()
	args.add_argument("-s", "--servers", default=DEFAULT_ES_SERVER,
		help='A list of elastic search servers seperated by "," against which to run queries (Default: %(default)s)')
	
	options = args.parse_args(argv)
	
	# post process argparsing results
	options.servers = [x.strip() for x in options.servers.split(",")]
	
	loop = asyncio.get_event_loop()
	t = Terminal()
	
	# Do this as a fullscreen app where possible to avoid poluting
	# terminal and screwing up cursor position
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
				loop.run_until_complete(display_loop(t, options.servers))
			except KeyboardInterrupt:
				# We want to catch this as its out primary exit method. if
				# uncaught we end up displaying a interleaved (with old output)
				# stack trace that would incorectly lead users to assume they 
				# crashed the program
				print("Exiting")
