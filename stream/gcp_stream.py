#!/usr/bin/env python
#-*- coding: utf-8 -*-
from sseclient import SSEClient as EventSource
import json, os
from google.cloud import pubsub_v1

def create_subscription(topic_name):
    subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(
        project_id=os.getenv('PROJECT_ID'),
        sub=os.getenv('TOPIC_ID'),  # Set this to something appropriate.
    )
    subscriber = pubsub_v1.SubscriberClient()
    subscriber.create_subscription(name=subscription_name, topic=topic_name)

topic_name = 'projects/{project_id}/topics/{topic}'.format(
    project_id=os.getenv('PROJECT_ID'),
    topic=os.getenv('TOPIC_ID'),  # Set this to something appropriate.
)

publisher = pubsub_v1.PublisherClient()
project = publisher.project_path(os.getenv("PROJECT_ID"))
topics = []

for page in publisher.list_topics(project).pages:
    for topic in page:
        topics.append(topic.name)

if not topic_name in topics: 
    publisher.create_topic(topic_name)
    # create_subscription(topic_name)

url = 'https://stream.wikimedia.org/v2/stream/recentchange'
for event in EventSource(url):
    if event.event == 'message':
        try:
            change = json.loads(event.data)
        except ValueError as e:
            print(e)
        else:
            #print('{user} edited {title}'.format(**change))
            if not change["bot"]:
                response = publisher.publish(topic_name, bytes(json.dumps(change),"utf-8"))
                print(response.result())
