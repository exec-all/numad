#!/usr/bin/env python
"""inputs: functions that grab data from elsewhere"""

from asyncio import coroutine, Task
from aioes import Elasticsearch

from .utils import wait_for_fd

import asyncio
import sys

def type_boost(doctype, boost_factor):
	"""Helper function to boost results from particular data stores"""
	return { "boost_factor": boost_factor, "filter": { "type": { "value": doctype } } }
	
@coroutine
def search_loop(loop, es, question):
	"""Perform a query against an elasticsearch cluster and clean up results"""
	q_dict = {
		"query": {
			"function_score": {
				"functions": [
					# This is a dummy boost, as ES complains if there are no functions to run.
					{ "boost_factor": 1.0 },
					type_boost('provsys', 3.0),
					{ "boost_factor": 2.5, "filter": { "query": { "query_string": { "query": 'url:"Blah"' } } } },
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

	# Few people have large large screens so limit to 30 results to cut down
	# on cycles spent
	# Short timeouts as a new key press is likley before this is reached
	# * is this actually sane??, we force kill queries anyway *
#	answer = yield from es.search('', None, q=question, size=30, timeout=1) # lucene query
	answer = yield from es.search('', None, body=q_dict, size=30, timeout=1) # ES query
	
	results = []

	for ans in answer['hits']['hits']:
		ans = ans['_source']
		results.append({'type':ans.get('doc_type'), 'title':ans.get('title'), 'url':ans.get('url')})

	return results

@coroutine
def input_loop(loop, term, buffer):
	"""Wait for a key press, then emulate a basic readline() on a provided buffer and return the new buffer
	
	Currently understands the following key presses:
	Backspace
	Enter (noop)
	"""

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
