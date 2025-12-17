# DSM Email

## install
```
pip install dsmemail
```

## how to use

```python
import dsmemail

status = dsmemail.sendEmail(
    subject="test", 
    message="helloworld", 
    emails=["admin@admin.com"],
    attachments=["test.txt"],
    host="https://email-service.data.storemesh.com",
    api_key="<API_KEY>"
)
print(status)
```
| variable      | dtype      | description                           |
| --------      | ---------  | ------------------------------------- |
| subject       | str        | subject of email                      |
| message       | str        | email body can contains html string   |
| emails        | List[str]  | email to send message                 |
| attachments   | List[str]  | list of filepath(str) to attach files |
| host          | str        | email server uri                      |
| api_key       | str        | api_key for email services            |  

output
```
[(True, 'email send to admin@admin.com sucess')]
```

#
status
```
True = send email sucess
False = send email fail
```

msg
```
string describe status
```