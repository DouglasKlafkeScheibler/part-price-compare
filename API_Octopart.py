import requests

# URL = "https://course-javasb-dks.herokuapp.com/users"
URL = 'https://octopart.com/api/v4/endpoint'
URL += '&queries=[{"mpn":"CL21B104MBCNNNC"}]'
URL += '&token=32723278-289c-4992-bfaa-b2ec91329f7b'

data = requests.get(url = URL)
response = data.json()
print(response)

# print request time (in milliseconds)
# print(response)

# print mpn's
# for result in response['results']:
#     for item in result['items']:
#         print(item['mpn'])