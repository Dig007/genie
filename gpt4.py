import requests
import json
import time

def get_new_token():
    url = "https://securetoken.googleapis.com/v1/token?key=AIzaSyBkanDK4DjniXPjw7TWA1dp9bUeOyHov6c"
    headers = {
        "Content-Type": "application/json",
        "X-Android-Package": "co.appnation.geniechat",
        "X-Android-Cert": "43D7F272E99AD8C847D911AA565AE3BCD74188CD",
        "Accept-Language": "in-ID, en-US",
        "X-Client-Version": "Android/Fallback/X22001002/FirebaseCore-Android",
        "X-Firebase-GMPID": "1:467270152911:android:9e21622fbcb4a9cc673dba",
        "X-Firebase-Client": "H4sIAAAAAAAAAKtWykhNLCpJSk0sKVayio7VUSpLLSrOzM9TslIyUqoFAFyivEQfAAAA",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; Redmi Note 5 Build/RQ3A.211001.001)",
        "Host": "securetoken.googleapis.com"
    }
    data = {
        "grantType": "refresh_token",
        "refreshToken": "AMf-vBxztAkcjH5-szemDJOy1l2cJJda4-Gfyl3J05wMDKGyy4WVs-ItlHEqhVPEMMoKii8LLYKV-z27l153-pbxZ6znyqEENOECofAs9QWXSaRUj3MUnUoWADI1YkPCgdSuumil-POoQqlBd4KaSxV4XsskgcRMwx2kFlyS0_HeBHO94AACOEM"
    }
    
    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()

    access_token = response_data["access_token"]
    expires_in = int(response_data["expires_in"])
    expires_at = time.time() + expires_in

    with open("token_info.txt", "w") as file:
        token_info = json.dumps({
            "access_token": access_token,
            "expires_at": expires_at
        })
        file.write(token_info)

    return access_token, expires_at

def send_request(data, token):
    url = "https://genie-production-yfvxbm4e6q-uc.a.run.app/v3/completions?stream=true"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    for attempt in range(3):
        try:
            response = requests.post(url, headers=headers, json=data, stream=True)
            return response
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error on attempt {attempt + 1}: {e}")
            if attempt < 2:
                time.sleep(3)
            else:
                raise

def process_response(response):
    chat_response = ""
    for chunk in response.iter_lines():
        line = chunk.decode("utf-8")
        if line.startswith('event: completion'):
            continue
        if line.startswith('data:'):
            try:
                data_dict = json.loads(line[6:])
                chat_response += data_dict.get('content', '')
            except json.decoder.JSONDecodeError as e:
                print("JSONDecodeError:", e)
                continue
        if line.startswith('event: done'):
            break
    return chat_response.strip()

def chat_with_ai():
    try:
        with open("token_info.txt", "r") as file:
            token_info = json.load(file)
        token = token_info["access_token"]
        expires_at = token_info["expires_at"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        token, expires_at = get_new_token()

    model_name = "OPEN_AI_CHATGPT_4_0_CHAT_MODEL"
    parameters = {
        "maxTokens": 1000,
        "temperature": 1,
        "topP": 1,
        "frequencyPenalty": 0,
        "presencePenalty": 0,
        "n": 1,
        "stop": []
    }

    messages = [
        {"role": "system", "content": "Kamu adalah asisten AI bernama ChatGPT."}
    ]

    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            break
        messages.append({"role": "user", "content": user_input})
        
        messages.append({"role": "system", "content": "Ai harus menjawab menggunakan bahasa indonesia dengan gaya tsundere."})
        
        if time.time() >= expires_at:
            token, expires_at = get_new_token()

        data = {
            "model": model_name,
            "parameters": parameters,
            "messages": messages,
            "user": "fZ4639Y3m2ds3KbFFhr7zQnayA62"
        }
        response = send_request(data, token)
        chat_response = process_response(response)
        print("AI Assistant:", chat_response)

        messages.append({"role": "assistant", "content": chat_response})

        if time.time() >= expires_at:
            token, expires_at = get_new_token()

if __name__ == "__main__":
    chat_with_ai()