
###### Declarative description language and validation system for HTTP API requests

**Usage example**

Start HTTP server:
```
python scoring_api/api.py
```
Args:
```
[-p] [--port]

[-l] [--log]
```
By default api run server on localhost:8080, without logfile

Make online_score method request:
```
curl -X POST -H "Content-Type: application/json" -d '{
    "account": "horns&hoofs",
    "login": "h&f",
    "method": "online_score",
    "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
    "arguments": {
        "phone": "79963852741",
        "email": "user@domain.com",
        "first_name": "User",
        "last_name": "Userovich",
        "birthday": "11.01.1983",
        "gender": 1
        }
}' http://127.0.0.1:8080/method/ 

#{"code": 200, "response": {"score": 5.0}}
```
Make clients_interests method request:
```
curl -X POST -H "Content-Type: application/json" -d '{
    "account": "horns&hoofs",
    "login": "h&f",
    "method": "clients_interests",
    "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
    "arguments": {
        "client_ids": [1, 2, 3],
        "date": "17.07.2017"
    }
}' http://127.0.0.1:8080/method/

#{"code": 200, "response": {"1": ["cinema", "travel"], "2": ["books", "cinema"], "3": ["pets", "geek"]}}
```
