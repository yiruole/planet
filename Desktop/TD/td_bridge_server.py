import json
import traceback


def onHTTPRequest(webServerDAT, request, response):
    uri = request['uri']
    method = request['method'].upper()

    response['headers'] = {'Content-Type': 'application/json'}

    try:
        if uri == '/network' and method == 'GET':
            data = _get_network()

        elif uri == '/params' and method == 'GET':
            op_path = request['pars'].get('op', '')
            data = _get_params(op_path)

        elif uri == '/params' and method == 'POST':
            body = json.loads(request['data'] or '{}')
            data = _set_param(body.get('op', ''), body.get('param', ''), body.get('value'))

        elif uri == '/exec' and method == 'POST':
            body = json.loads(request['data'] or '{}')
            data = _exec_code(body.get('code', ''))

        else:
            response['statusCode'] = 404
            response['statusReason'] = 'Not Found'
            response['data'] = json.dumps({'error': 'route not found'})
            return response

        response['statusCode'] = 200
        response['statusReason'] = 'OK'
        response['data'] = json.dumps(data)

    except Exception as e:
        response['statusCode'] = 500
        response['statusReason'] = 'Error'
        response['data'] = json.dumps({'error': str(e), 'trace': traceback.format_exc()})

    return response


def _get_network():
    ops = []
    for o in root.findChildren(depth=4):
        try:
            ops.append({
                'path':    o.path,
                'name':    o.name,
                'type':    o.OPType,
                'family':  o.family,
                'x':       o.nodeX,
                'y':       o.nodeY,
                'inputs':  [i.path if i else None for i in o.inputs],
                'outputs': [c.path for c in o.outputs],
            })
        except Exception:
            pass
    return {'count': len(ops), 'ops': ops}


def _get_params(op_path):
    o = op(op_path)
    if not o:
        return {'error': f'not found: {op_path}'}
    params = {}
    for p in o.pars():
        try:
            params[p.name] = {'val': p.eval(), 'label': p.label}
        except Exception:
            pass
    return {'op': op_path, 'type': o.OPType, 'params': params}


def _set_param(op_path, param_name, value):
    o = op(op_path)
    if not o:
        return {'error': f'not found: {op_path}'}
    try:
        setattr(o.par, param_name, value)
        return {'ok': True, 'op': op_path, 'param': param_name, 'value': value}
    except Exception as e:
        return {'error': str(e)}


def _exec_code(code):
    local_ns = {'result': None}
    try:
        exec(compile(code, '<bridge>', 'exec'), {**globals()}, local_ns)
        return {'ok': True, 'result': str(local_ns.get('result', ''))}
    except Exception as e:
        return {'ok': False, 'error': str(e), 'trace': traceback.format_exc()}
