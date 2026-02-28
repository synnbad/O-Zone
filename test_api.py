import httpx

# Test OpenAQ v2 API
response = httpx.get(
    'https://api.openaq.org/v2/locations',
    params={'city': 'Los Angeles', 'limit': 1},
    timeout=30
)

print(f'Status: {response.status_code}')
data = response.json()
print(f'Results: {len(data.get("results", []))}')

if data.get('results'):
    result = data['results'][0]
    print(f'Location: {result.get("name")} ({result.get("city")}, {result.get("country")})')
    print(f'Coordinates: {result.get("coordinates")}')
