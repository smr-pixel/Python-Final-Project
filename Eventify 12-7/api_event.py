import requests

response = requests.post('http://127.0.0.1:5000/api/events', json={
    'name': 'New Event',
    'date': '2023-12-31',
    'location': 'Soldiers and Sailors Memorial Hall',
    'description': 'This is a new event.',
    'capacity': 100,
    'price': 50.0
})
event = response.json()
print(event)