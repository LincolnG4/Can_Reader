import tago
from datetime import datetime

my_device = tago.Device('8c06628d-7781-4c1c-a679-b9bea76c9767')

data = {
    'variable': 'EngSpeed',
    'unit': 'rpm',
    'value': 12,
    'time': str(datetime.now(tz=None)),
    'location': {'lat': -25.579923, 'lng': -49.3957846}
    }

result = my_device.insert(data)
print(result)
