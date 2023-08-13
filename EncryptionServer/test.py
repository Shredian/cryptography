import requests
user_id = 1
file_id = 1

def main():
    data = {'cypher_type': 'XTR'}
    requests.post(f"http://127.0.0.1:8000/api/upload?file_id={file_id}&user_id{user_id}",
                  files={'file': open("8.png", 'rb')})


if __name__ == "__main__":
    main()
