import os

from flask import url_for

from tabulate import tabulate

from . import script_manager

from app import get_app


@script_manager.command
def list_routes():
    import urllib
    output = []
    for rule in get_app().url_map.iter_rules():
        methods = ','.join(rule.methods)
        output.append(map(urllib.unquote, [rule.endpoint, methods, str(rule)]))
    
    print(tabulate(output, headers=['Endpoint', 'Methods', 'URL']))


@script_manager.option('-h', '--host', default='0.0.0.0', help="Bind to this host")
@script_manager.option('-p', '--port', default=8000, type=int, help="Bind to this port")
@script_manager.option('-D', '--no-debugger', action='store_false', dest='debugger', help="Disable the debugger")
@script_manager.option('-R', '--no-reloader', action='store_false', dest='reloader', help="Disable the reloader")
@script_manager.option('-t', '--threaded', action='store_true', help="Run threaded")
@script_manager.option('-P', '--processes', type=int, help="Run this many processes")
@script_manager.option('-s', '--ssl', action='store_true', help="Serve using SSL")
def runserver(host, port, debugger, reloader, threaded, processes, ssl):
    args = {
        'host': host,
        'port': port,
        'debug': debugger,
        'use_reloader': reloader,
    }

    if processes:
        args['processes'] = processes
    else:
        args['threaded'] = threaded

    if ssl:
        args['ssl_context'] = (
            'ssl_cert.cert',
            'ssl_key.key'
        )

    get_app().run(**args)
