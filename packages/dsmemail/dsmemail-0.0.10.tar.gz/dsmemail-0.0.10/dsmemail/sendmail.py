import os
import requests
import concurrent.futures
from .check import check_type

DSM_EMAIL_APIKEY = os.environ.get('DSM_EMAIL_APIKEY', None)
DSM_EMAIL_URI = os.environ.get('DSM_EMAIL_URI', None)

def _send_mail(args):
    r = requests.post(f"{args.get('host')}/email/api/emailMessage/",
            headers={
                "Authorization": f"Api-Key {args.get('api_key')}"
            },
            data={
                "subject": args.get('subject'),
                "message": args.get('message'),
                "email": args.get('email')
            },
            files=args.get('file')
    )
    if r.status_code == 201:
        return True, f"email send to {args.get('email')} sucess"
    elif r.status_code in [400, 401, 403]:
        return False, r.json()
    else:
        return False, f"{r.content}\nsome thing wrong {r.status_code}"

def sendEmail(subject=None, message=None, emails=None, attachments=[], host=DSM_EMAIL_URI, api_key=DSM_EMAIL_APIKEY):
    
    if host == None or api_key is None:
        raise Exception("please input `host` and `api_key` or set env `DSM_EMAIL_APIKEY` and `DSM_EMAIL_URI`")
    
    check_type(variable=subject, variableName="subject", dtype=str)
    check_type(variable=message, variableName="message", dtype=str)
    check_type(variable=emails, variableName="emails", dtype=list, child=str)
    check_type(variable=attachments, variableName="attachments", dtype=list, child=str)
    
    file = [("attachments", open(elm, 'rb')) for elm in attachments]
    datas = [{
        'subject': subject,
        'message': message,
        'email': email,
        'file': file,
        'host': host,
        'api_key': api_key
    } for email in emails]
    result = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        
        futures = [executor.submit(_send_mail, arg) for arg in datas]

        # Iterate over the future objects as they complete
        for future in concurrent.futures.as_completed(futures):
            result.append(future.result())
    return result