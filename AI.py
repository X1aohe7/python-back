# doctor.py
from zhipuai import ZhipuAI
from flask import Blueprint, jsonify
from flask import request  # 添加这一行来引入 request 模块

AI = Blueprint('AI', __name__)



@AI.route('/AITalk',methods=['POST'])
def AITalk():
    user_input = request.form.get('user_input', type=str)
    client = ZhipuAI(api_key="49fe57925ac55b13cddf26c3fcc7a1bf.TKJRCacGj07ik1ki")  # 填写您自己的APIKey
    conversation = []  # 用于保存对话上下文的列表
    conversation.append({"role": "user", "content": user_input})  # 将用户输入添加到对话上下文中
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=conversation,  # 使用包含对话上下文的消息列表
    )
    answer = response.choices[0].message.content
    conversation.append({"role": "assistant", "content": answer})  # 将助手的回复添加到对话上下文中
    return jsonify(answer)

