import os

from flask import url_for, current_app

from tabulate import tabulate

from . import script_manager

from app import get_app


@script_manager.command
def list_routes():
    import urllib
    output = []
    for rule in get_app().url_map.iter_rules():
        methods = ','.join(rule.methods)
        output.append(map(urllib.parse.unquote, [rule.endpoint, methods, str(rule)]))
    
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


@script_manager.option('-m', '--method', default="POST", help="Use this method - only POST is supported, anything else should produce an error")
@script_manager.option('-i', '--foreign-id', required=True, help="Foreign ID for the badge")
@script_manager.option('-n', '--name', required=True, help="Badge name")
@script_manager.option('-l', '--level', required=True, help="Badge level")
@script_manager.option('-a', '--age', required=True, type=int, help="Age")
@script_manager.option('-f', '--flag', action='append', dest='flags', help="Flags")
def badgetest(method, foreign_id, name, level, age, flags):
    import requests, hmac, json, hashlib
    url = 'http://localhost:8000/api/badge'
    body = {'foreign_id': foreign_id, 'name': name, 'level': level, 'age': age}
    if flags:
        body['flags'] = flags
    body = json.dumps(body)

    h = hmac.new(
        current_app.config.get('API_SECRET').encode('utf-8'),
        digestmod=getattr(hashlib, current_app.config.get('API_HMAC_HASH'))
    )
    h.update(method.upper().encode('utf-8'))
    h.update(url.encode('utf-8'))
    h.update(body.encode('utf-8'))
    h = h.hexdigest()

    res = getattr(requests, method.lower())(
        url,
        data=body,
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'HMAC ' + h,
        }
    )

    print(res.status_code)
    print(res.text)
