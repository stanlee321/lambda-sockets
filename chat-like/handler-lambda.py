from gripcontrol import WebSocketMessageFormat
from faas_grip import lambda_get_websocket, publish

def handler(event, context):


	try:
		ws = lambda_get_websocket(event)
	except ValueError:
		return {
			'statusCode': 400,
			'headers': {'Content-Type': 'text/plain'},
			'body': 'Not a WebSocket-over-HTTP request\n'
		}

	# if this is a new connection, accept it and subscribe it to a channel
	if ws.is_opening():
		ws.accept()
		ws.subscribe('room')

	# here we loop over any messages
	while ws.can_recv():
		message = ws.recv()

		# if return value is None, then the connection is closed
		if message is None:
			ws.close()
			break

		if message.startswith('/nick '):
			nick = message[6:]
			ws.meta['nick'] = nick
			ws.send('nickname set to [%s]' % nick)
		else:
			# send the message to all clients
			nick = ws.meta.get('nick') or 'anonymous'
			publish('room', WebSocketMessageFormat('%s: %s' % (nick, message)))
			# send the message to all clients

	return ws.to_response()


