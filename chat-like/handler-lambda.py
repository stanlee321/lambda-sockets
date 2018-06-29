from gripcontrol import WebSocketMessageFormat
from faas_grip import lambda_get_websocket, publish
import pickle
import boto3

from base64 import b64encode, b64decode

def handler(event, context):
	print('event is', event)

	try:
		print('NormalerWiese behavior')
		ws = lambda_get_websocket(event)
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

			if message.startswith('/user '):
				nick = message[6:]
				ws.meta['user'] = nick
				ws.send('user set to [%s]' % nick)
				ws.subscribe(nick)
				# Saving metadata to s3
				namen = nick
				print('namen', namen)
				s3_response = put_object_s3(event, namen=namen)
				print('s3 response', s3_response)

			#else:
				# send the message to all clients
			#	nick = ws.meta.get('nick') or 'anonymous'
			#	publish('room', WebSocketMessageFormat('%s: %s' % (nick, message)))
				# send the message to all clients
		response = ws.to_response()
		#response['headers']['Grip-Hold'] = 'stream'
		#response['headers']['Grip-Channel'] = 'room'
		return response

	except Exception as e:
		try:
			print('Entering to Unknow zone with exception, ', e)
			userID = _decode_sns(event)
			print('USER ID IN UNKNOW ZONE IS', userID)
			event_template = _read_object_s3(key = '%s.pkl' %userID)

			ws = lambda_get_websocket(event_template)

			# if this is a new connection, accept it and subscribe it to a channel

			ws.subscribe(userID)
			# here we loop over any messages
			print('sending user ID',userID)
			ws.meta['user'] = userID
			#ws.send('user [%s] set an infraction' % userID)

			while ws.can_recv():
				message = ws.recv()
				# if return value is None, then the connection is closed
				if message is None:
					ws.close()
					break
				#else:
					# send the message to all clients
				#	nick = ws.meta.get('nick') or 'anonymous'
			nick = ws.meta.get('user')
			print('WHAI IS MY NICK=?=????', nick)
			msg = 'man you have a infraction'
			publish(nick, WebSocketMessageFormat('%s: %s' % (nick, msg)))
			# send the message to all clients
			response = ws.to_response()

			return response
		except Exception as e:
			print('THis happen,', e)

def put_object_s3(data, namen=None):

	s3_client = boto3.client('s3')

	bucket='infractor-serve-assets-to-app'
	key='%s.pkl' % namen

	pickle_byte_obj = pickle.dumps(data)

	s3_client.put_object(
		Bucket = bucket,
		Key = key,
		Body = pickle_byte_obj,
		ACL='public-read'
	)
	return True

def _read_object_s3(key = None):
	bucket='infractor-serve-assets-to-app'

	s3 = boto3.resource('s3')
	filepath = '/tmp/' + 'event.pkl'
	with open(filepath, 'wb') as data:
		s3.Bucket(bucket).download_fileobj(key, data)

	with open(filepath, 'rb') as data:
		event = pickle.load(data)

	return event



def _decode_sns(event):
	print('EVENT from UNKNOW is', event)
	# read body as binary
	if event.get('isBase64Encoded'):
		sns_unicode = b64decode(event["Records"][0]["Sns"]["Message"])
		sns = sns_unicode.encode('utf-8')
		print('postID', sns)
		return sns
	else:
		sns_unicode = event["Records"][0]["Sns"]["Message"]
		sns = sns_unicode.encode('utf-8')
		print('not b64', sns)
		return sns


# Algorithm Try
# Save 
# IF conection is open,
# Accpet connection
# while ws can receive:
# receive message 
# set ws meta['nick'] to id received by /nick
# send this config to nick user



# Algorithm Except
# Load event as pickle from s3
# Create labmda_get_socket object with (event)
# Reemplaze ID field with generated generic ID
# Use userID from  SNS event
# Send a meta['nick'] message to this user

