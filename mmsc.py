from werkzeug.security import generate_password_hash

def generate_hash(password):
    hashed_password = generate_password_hash(password)
    return hashed_password

if __name__ == '__main__':
    # 输入你想要哈希的密码
    password = input("请输入要生成哈希的密码: ")
    hashed_password = generate_hash(password)
    print(f"生成的哈希密码为: {hashed_password}")
