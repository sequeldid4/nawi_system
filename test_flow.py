import requests

s = requests.Session()
r = s.get('http://127.0.0.1:5000/inspector/instrument-profile')
csrf_token = r.text.split('name="csrf_token" type="hidden" value="')[1].split('"')[0]
print("CSRF Token:", csrf_token)

r1 = s.post('http://127.0.0.1:5000/inspector/instrument-profile', data={
    'csrf_token': csrf_token,
    'mfg_name': 'Test Mfg', 'mfg_address': 'Addr 1',
    'model_num': 'M1', 'serial_num': 'S1', 'scale_type': 'platform',
    'accuracy_class': 'III', 'max_capacity': '1000', 'min_capacity': '20',
    'e_value': '1', 'd_value': '1'
}, allow_redirects=False)
print("Profile Status:", r1.status_code)
if r1.status_code == 200:
    print("Form errors probably:", r1.text[-500:])

