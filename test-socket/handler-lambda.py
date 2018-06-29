import boto3
import os

def handler(event, context):
	# with te inccominng hour as parameter to look in Loc table
	clientSNS = boto3.client('sns')

	# Send to socket
	clientSNS.publish(
		TopicArn = os.environ['SNS_TOPIC_NEW'],
		Message = 'ASDF'
	)