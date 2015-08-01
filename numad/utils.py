#!/usr/bin/env python
"""utils: useful functions that do not belong in other modules"""

from asyncio import coroutine, Future, get_event_loop

# This function is being moved to text11/waytext once the design of that
# lib is finalised and intergrated here
@coroutine
def wait_for_fd(fd, *, loop=None):
	"""Given a file descriptor, block on it until we have input to read"""
	if hasattr(fd, 'fileno'):
		fd = fd.fileno()
	
	if not loop:
		loop = get_event_loop()
	
	waiter = Future(loop=loop)
	loop.add_reader(fd, lambda : waiter.set_result(None))
	yield from waiter
	loop.remove_reader(fd)
