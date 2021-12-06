# python -m pytest -v --cov

import pytest
from app import app

@pytest.fixture
def client():
    return app.test_client()


def test_home(client):
    resp = client.get('/')
    assert resp.status_code == 200
 
def test_blacklist_bad_http_method(client):
    resp = client.post('/urlinfo/1/www.sfu.ca')
    assert resp.status_code == 405

def test_blacklist_no_content(client):
    resp = client.get('/urlinfo/1/')
    assert resp.status_code == 404
    assert isinstance(resp.json, dict)
    assert resp.json.get('status', 404)

def test_blacklist_no_query(client):
    resp = client.get('/urlinfo/1/www.sfu.ca')
    assert resp.status_code == 200
    assert isinstance(resp.json, dict)
    assert not resp.json.get('approved')
    assert resp.json.get('status', 200)


def test_blacklist_approved(client):
    resp = client.get('/urlinfo/1/www.sfu.ca/about/economic-recovery/1-10.html')
    assert resp.status_code == 200
    assert isinstance(resp.json, dict)
    assert resp.json.get('approved')
    assert resp.json.get('status', 200)
   

def test_blacklist_not_approved(client):
    resp = client.get('/urlinfo/1/www.sfu.ca:443/cgi-bin/test.pl?first=first_tst&second=second-value')
    assert resp.status_code == 200
    assert isinstance(resp.json, dict)
    assert not resp.json.get('approved')
    assert resp.json.get('status', 200)

# TODO: Test functions in webapp
# TODO: Test Mongo DB 
"""
www.sfu.ca/about/economic-recovery/1-10.html
www.sfu.ca/about/economic-recovery/1-10.html
www.sfu.ca/about/economic-recovery/1-10.html

ubc.ca/academics/
ubc.ca/academics/

umbrella.cisco.com/?dtid=osscdc000283
umbrella.cisco.com/?dtid=osscdc000283

www.geeksforgeeks.org:443/python-build-a-rest-api-using-flask/
www.geeksforgeeks.org:443/python-build-a-rest-api-using-flask/

"""