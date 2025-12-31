import requests,json
ses = requests.Session()

def register():
    data = { 
        "username": "fallxavier",
        "name": "FallXavier",
        "email": "fallxavier@zero.com",
        "password": "Falah123!"
    }
    
    post = ses.post("http://127.0.0.1:8000/user/register", params=data)
    print(post.text)
    
def profile():
    headers = {
        "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjQ1ODEyMDYsInN1YiI6IjNlYWQzOTMyLTliMTItNDczYi1hY2EyLWZkZTlhZWQ4MjNjOCIsInR5cGUiOiJhY2Nlc3MifQ.te3JDssGbON08ebQHKotKVpE_784D2bSFA8y0mKBIms"
    }
    post = ses.get("http://127.0.0.1:8000/user/profile", headers=headers)
    print(post.text)
    
def refresh():
    data = {
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjcxNzIwNTYsInN1YiI6IjNlYWQzOTMyLTliMTItNDczYi1hY2EyLWZkZTlhZWQ4MjNjOCIsImp0aSI6Ijk1MWY2OTg4LTJmYWEtNDNlZC1hZjFiLTRkOTRlNmJiYmRlMiIsInR5cGUiOiJyZWZyZXNoIn0.P_QVmbD9ILyOfjeoMIFH3FXaQShm9dDWIMm9HOSjc-k"
    }
    post = ses.post("http://127.0.0.1:8000/user/refresh", json=data)
    print(post.text)
    
profile()