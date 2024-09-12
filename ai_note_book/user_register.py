from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from datetime import datetime
import os

app = Flask(__name__)

# 数据库连接
CUR_DIR = os.path.realpath(os.path.dirname(__file__))
# PARENT_DIR = os.path.dirname(CUR_DIR)
JOIN_DIR = os.path.join(CUR_DIR, "sqlite.db")
DATABASE_URL = "sqlite:///" + JOIN_DIR
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# 定义数据库模型
class UserData(db.Model):
    __tablename__ = 'user_data'

    user_id = db.Column(db.String, primary_key=True, nullable=False)
    user_creation_time = db.Column(db.DateTime, default=datetime.utcnow)
    user_name = db.Column(db.String)
    user_phone = db.Column(db.String)
    user_status = db.Column(db.Boolean, default=True)


# 创建数据库表
with app.app_context():
    db.create_all()


# 注册用户的路由
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json

    user_name = data.get('user_name')
    user_phone = data.get('user_phone')

    if not user_name or not user_phone:
        return jsonify({'error': 'Missing user_name or user_phone'}), 400

    new_user = UserData(
        user_id=str(uuid4()),
        user_name=user_name,
        user_phone=user_phone
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'user_id': new_user.user_id,
        'user_creation_time': new_user.user_creation_time,
        'user_name': new_user.user_name,
        'user_phone': new_user.user_phone,
        'user_status': new_user.user_status
    }), 201


if __name__ == '__main__':
    app.run(debug=True)