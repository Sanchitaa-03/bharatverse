from app import app
from database.init_db import ensure_student_demo_account

ensure_student_demo_account()
client = app.test_client()
client.post('/login', data={'demo_login': 'student'}, follow_redirects=False)
resp = client.get('/map/indus_valley', follow_redirects=False)
print('status', resp.status_code)
print('location', resp.headers.get('Location'))
print('contains_map_title', 'Civilization Map' in resp.get_data(as_text=True))
