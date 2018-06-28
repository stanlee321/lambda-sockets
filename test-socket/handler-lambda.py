from gripcontrol import HttpStreamFormat
from faas_grip import publish

def handler(event, context):
	try:
		sns = decode_sns(event)
	except:
		return {
			'statusCode': 400,
			'headers': {'Content-Type': 'text/plain'},
			'body': 'Not a WebSocket-over-HTTP request\n'
		}

	publish('mychannel', HttpStreamFormat('some data\n'))


def decode_sns(event):
	print('EVENT is', event)
	# read body as binary
	if event.get('isBase64Encoded'):
		sns_unicode = b64decode(event["Records"][0]["Sns"]["Message"])
		sns = sns.encode('utf-8')
		print('postID', sns)
		return sns
	else:
		sns_unicode = event["Records"][0]["Sns"]["Message"]
		sns = sns.encode('utf-8')
		print('not b64', sns)
		return sns
