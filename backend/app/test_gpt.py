from services import gpt

if __name__ == "__main__":
    msg = [{"role": "user", "content": "안녕! GPT API가 잘 작동하는지 테스트 중이야."}]
    res = gpt.ask_gpt(msg)
    print("=== GPT 응답 ===")
    print(res)