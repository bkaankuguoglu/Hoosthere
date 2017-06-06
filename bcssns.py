import boto
import boto.exception
import boto.sns
import pprint
import re
import json

def send_push(body, device_id):
    region = [r for r in boto.sns.regions() if r.name==u'eu-central-1'][0]

    sns = boto.sns.SNSConnection(
        region=region,
    )   
    
    try:
        endpoint_response = sns.create_platform_endpoint(
            platform_application_arn='arn:aws:sns:eu-central-1:727045919079:app/APNS_SANDBOX/Hoo',
            token=device_id,
        )   
        endpoint_arn = endpoint_response['CreatePlatformEndpointResponse']['CreatePlatformEndpointResult']['EndpointArn']
    except boto.exception.BotoServerError, err:
        # Yes, this is actually the official way:
        # http://stackoverflow.com/questions/22227262/aws-boto-sns-get-endpoint-arn-by-device-token
        result_re = re.compile(r'Endpoint(.*)already', re.IGNORECASE)
        result = result_re.search(err.message)
        if result:
            endpoint_arn = result.group(0).replace('Endpoint ','').replace(' already','')
        else:
            raise
            
    print "ARN:", endpoint_arn
    body = {'aps': {'alert': body, 'sound': 'default'}}
    body_json = json.dumps(body, ensure_ascii=False)

    message = {'default': 'The default message',
           'APNS_SANDBOX': body_json}

    MESSAGE_JSON = json.dumps(message, ensure_ascii=False)
    publish_result = sns.publish(
        target_arn=endpoint_arn,
        message=MESSAGE_JSON,
        message_structure='json',
    )
    print "PUBLISH"
    pprint.pprint(publish_result)