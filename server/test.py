import pyalohareciever
import time
import sys

with open('../etc/aloha_message', 'rb') as f:
    bt = f.read()

try:
    aloha_id, events = pyalohareciever.decode(bt)
except RuntimeError:
    exit(1)

print(sys.getsizeof(events))

for event in events:
    print(event.key, '  ', event.value, ' ', event.location, '  ', event.pairs)
