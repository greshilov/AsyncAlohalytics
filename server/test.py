import pyalohareciever
import time
import sys

with open('../aloha_request1', 'rb') as f:
    bt = f.read()

try:
    aloha_id, events = pyalohareciever.decode(bt)
except RuntimeError:
    exit(1)

print(sys.getsizeof(events))

for event in events:
    #print(time.gmtime(event.timestamp / 1000))
    print(event.key, '  ', event.value)
