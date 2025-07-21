import requests
import json
import time
from openai import OpenAI

try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    COOKIE = config.get('cookie')
    OPENAI_API_KEY = config.get('openai_api_key')
    OPENAI_API_BASE = config.get('openai_api_base', 'https://api.openai.com/v1')
    OPENAI_MODEL_NAME = config.get('openai_model_name', 'gpt-3.5-turbo')
    SYSTEM_PROMPT = config.get('system_prompt', '你是一个友好且乐于助人的助手。')

    if not COOKIE or COOKIE == "在此处粘贴你的Cookie":
        print("错误：请先在 config.json 文件中设置你的爱发电Cookie。")
        exit()
    if not OPENAI_API_KEY or OPENAI_API_KEY == "在此处粘贴你的OpenAI API Key":
        print("错误：请先在 config.json 文件中设置你的OpenAI API Key。")
        exit()
    
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE,
    )

except FileNotFoundError:
    print("错误：找不到 config.json 文件。请确保它与脚本在同一目录下。")
    exit()
except json.JSONDecodeError:
    print("错误：config.json 文件格式不正确。")
    exit()

API_BASE_URL = "https://afdian.com/api"
GET_DIALOGS_URL = f"{API_BASE_URL}/message/dialogs"
SEND_MSG_URL = f"{API_BASE_URL}/message/send"
MARK_AS_READ_URL = f"{API_BASE_URL}/message/messages"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'Content-Type': 'application/json',
    'Cookie': COOKIE,
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'locale-lang': 'zh-CN',
    'origin': 'https://afdian.com',
    'referer': 'https://afdian.com/message'
}

def get_unread_dialogs():
    """获取未读消息列表"""
    params = {'unread': '1', 'page': '1'}
    try:
        response = requests.get(GET_DIALOGS_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get('ec') == 200:
            return data.get('data', {}).get('list', [])
        else:
            print(f"获取未读列表失败: {data.get('em')}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"请求未读列表时发生网络错误: {e}")
        return []
    except json.JSONDecodeError:
        print(f"解析响应失败，内容: {response.text}")
        return []

def send_reply(user_id, content):
    """发送回复"""
    payload = {
        'user_id': user_id,
        'content': content,
        'type': '1'
    }
    try:
        response = requests.post(SEND_MSG_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        data = response.json()
        if data.get('ec') == 200:
            print(f"成功回复用户 {user_id}: {content}")
            return True
        else:
            print(f"回复用户 {user_id} 失败: {data.get('em')}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"发送回复时发生网络错误: {e}")
        return False

def mark_as_read(user_id):
    """通过访问消息历史记录将对话标记为已读"""
    params = {'user_id': user_id, 'type': 'old', 'message_id': ''}
    try:
        response = requests.get(MARK_AS_READ_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get('ec') == 200:
            print(f"成功将用户 {user_id} 的对话标记为已读。")
            return True
        else:
            print(f"标记已读失败: {data.get('em')}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"标记已读时发生网络错误: {e}")
        return False

def get_openai_reply(prompt):
    """调用OpenAI API获取回复"""
    try:
        print(f"正在为提示生成OpenAI回复: '{prompt}'")
        completion = client.chat.completions.create(
            model=OPENAI_MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )
        reply = completion.choices[0].message.content.strip()
        final_reply = f"{reply}\n\n(此回复由AI生成)"
        print(f"成功生成回复: '{final_reply}'")
        return final_reply
    except Exception as e:
        print(f"调用OpenAI API时出错: {e}")
        return "抱歉，我现在无法回复。我的大脑（AI）可能暂时离线了。"

def main_loop():
    """机器人主循环"""
    print("机器人已启动，开始监听新消息...")
    while True:
        try:
            unread_dialogs = get_unread_dialogs()
            
            if unread_dialogs:
                print(f"发现 {len(unread_dialogs)} 个未读对话。")
                for dialog in unread_dialogs:
                    user_id = dialog.get('user', {}).get('user_id')
                    message_content = dialog.get('desc')

                    if user_id:
                        print(f"处理来自用户 {user_id} 的新消息: '{message_content}'")
                        
                        reply_content = get_openai_reply(message_content)
                        
                        if send_reply(user_id, reply_content):
                            # 回复成功后，立即将该对话标记为已读
                            mark_as_read(user_id)
            else:
                print("暂无新消息，继续监听...")
            
            # 每15秒检查一次
            time.sleep(15)

        except KeyboardInterrupt:
            print("\n机器人已停止。")
            break
        except Exception as e:
            print(f"主循环发生未知错误: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main_loop()