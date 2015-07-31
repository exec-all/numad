#!/usr/bin/env python
"""umad: pull results from umad"""

from argparse import ArgumentParser
from asyncio import coroutine, Task
from aioes import Elasticsearch
from blessed import Terminal
from time import sleep

from .render import render_search_results, render_query_field
from .utils import wait_for_fd

from . import DEFAULT_ES_SERVER, UMAD_INDEX, DOC_TYPE_ALL

import asyncio
import sys
import os

def type_boost(doctype, boost_factor):
	return { "boost_factor": boost_factor, "filter": { "type": { "value": doctype } } }
	
@coroutine
def search_loop(loop, es, question):
	q_dict = {
		"query": {
			"function_score": {
				"functions": [
					# This is a dummy boost, as ES complains if there are no functions to run.
					{ "boost_factor": 1.0 },
					type_boost('provsys', 3.0),
					{ "boost_factor": 2.5, "filter": { "query": { "query_string": { "query": "url:\"redacted" } } } },
				],
				"query": {
					"query_string": {
						"query": question,
						"default_operator": "and",
						"fields": [ "title^1.5", "customer_name", "blob" ]
					}
				},
				"score_mode": "multiply"
			}
		},
    }

#	answer = yield from es.search('', None, q=question, size=30, timeout=1)
	answer = yield from es.search('', None, body=q_dict, size=30, timeout=1)
	
	results = []

	for ans in answer['hits']['hits']:
		ans = ans['_source']
		results.append({'type':ans.get('doc_type'), 'title':ans.get('title'), 'url':ans.get('url')})

	return results

@coroutine
def input_loop(loop, term, buffer):

	yield from wait_for_fd(sys.stdin)
	
	key = True
	while key:
		# blocking but with a short timeout
		# as a nice side effect this will inhibit
		# new searches that are likley to be retired
		# before compleation due to typing quickly
		#
		# full effects still not fully understood 
		# (may be causing input lag)
		key = term.inkey(timeout=0.1)
	
		if key.name:
			if key.name == "KEY_DELETE":
				buffer = buffer[:-1]
			if key.name == "KEY_ENTER":
				pass
		else:
			buffer += str(key)

	return buffer

@coroutine
def display_loop(term):
	query = ""
	# avoid recreating this all the time due to implicit dns lookups in creation
	es = Elasticsearch(ES_SERVERS)

	loop = asyncio.get_event_loop()
#	loop.add_reader(sys.stdin.fileno())

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
