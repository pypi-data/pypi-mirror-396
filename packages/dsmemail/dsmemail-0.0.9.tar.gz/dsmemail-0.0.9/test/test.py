import os
os.environ['DSM_EMAIL_URI'] = "https://email-service.data.storemesh.com"
os.environ['DSM_EMAIL_APIKEY'] = ""

import dsmemail

result = dsmemail.sendEmail(subject="test", 
    message="helloworld", 
    emails=[""],
)
print(result)