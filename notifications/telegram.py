import requests
def send(text,token,chat_id):
    if not token or not chat_id: return False
    r=requests.post(f"https://api.telegram.org/bot{token}/sendMessage",json={"chat_id":chat_id,"text":text},timeout=15); r.raise_for_status(); return True

