import base64
import json
import random
import string
import hashlib


def read_json_file(file_path):
    """读取JSON文件并返回JSON数据。"""
    try:
        # 打开文件并读取内容
        with open(file_path, 'r', encoding='utf-8') as file:
            # 将文件内容解析为JSON对象
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
    except json.JSONDecodeError:
        print(f"文件 {file_path} 不是有效的JSON格式。")
    except Exception as e:
        print(f"读取文件时发生错误：{e}")


def write_json_data_to_file(data, file_path):
    """将JSON数据写入到文件中，如果文件存在则替换其内容。"""
    try:
        # 打开文件，使用'w'模式，如果文件存在则覆盖
        with open(file_path, 'w') as file:
            # 将JSON数据写入文件
            json.dump(data, file)
        print(f"数据已成功写入到 {file_path}")
    except Exception as e:
        print(f"写入文件时发生错误：{e}")


def generate_random_key(intensity):
    """生成一个随机长度的base64编码样式的字符串作为键名，长度随机且不超过60"""
    length = random.randint(10, min(60, intensity))  # 确保长度在20到60或intensity的最小值之间
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return base64.urlsafe_b64encode(random_string.encode()).decode()


def generate_random_value(intensity):
    """生成一个随机长度的base64编码样式的字符串作为值，长度随机且不超过60"""
    length = random.randint(10, min(60, intensity))  # 同上
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return base64.urlsafe_b64encode(random_string.encode()).decode()


def encrypt_json(data, intensity, nested_intensity, encrypt_flag, depth=0, max_depth=10):
    """递归地根据强度intensity在data中添加随机键值对"""
    if encrypt_flag:
        if depth > max_depth:
            return data  # 达到最大递归深度则停止递归

        if not isinstance(data, dict):
            raise ValueError("The input data must be a dictionary.")

        # 深拷贝原始数据
        new_data = json.loads(json.dumps(data))

        # 获取所有键的列表，以避免迭代过程中修改字典大小
        keys = list(new_data.keys())

        for key in keys:
            value = new_data[key]

            # 如果当前值是一个字典，递归处理
            if isinstance(value, dict):
                new_data[key] = encrypt_json(value, intensity, nested_intensity, encrypt_flag, depth + 1, max_depth)
            # 如果当前值不是字典，添加随机键值对
            else:
                for _ in range(intensity):
                    # 动态调整键长度

                    key_length = random.randint(10, intensity)
                    value_length = random.randint(10, intensity)
                    new_key = generate_random_key(key_length)
                    new_value_str = generate_random_value(value_length)
                    new_data[new_key] = new_value_str

        # 如果字典为空，则直接填充随机键值对
        if not new_data and depth == 0:
            for _ in range(nested_intensity):
                key_length = random.randint(10, intensity)
                value_length = random.randint(10, intensity)
                new_key = generate_random_key(key_length)
                new_value_str = generate_random_value(value_length)
                new_data[new_key] = new_value_str

        return new_data
    else:
        return data


def generate_md5_key(seed, intensity):
    """使用给定的seed和强度生成一个MD5哈希值作为键名"""
    # 生成随机长度的字符串作为seed
    random_length = random.randint(10, intensity)
    random_string = seed + ''.join(random.choices(string.ascii_letters + string.digits, k=random_length))
    # 使用MD5哈希算法
    hash_object = hashlib.md5()
    hash_object.update(random_string.encode())
    # 返回MD5哈希的十六进制表示
    return hash_object.hexdigest()


def insert_zero_width_spaces(value, intensity):
    """在字符串值中根据强度在随机位置插入零宽度空格（\u200d）"""
    value_str = str(value)
    spaces_count = random.randint(0, min(10, intensity))
    for _ in range(spaces_count):
        insert_index = random.randint(0, len(value_str))
        value_str = value_str[:insert_index] + '\u200d' + value_str[insert_index:]
    return value_str


def inject_random_pairs_recursive(data, intensity, fixed_string, nested_intensity, encrypt_flag, depth=0, max_depth=10):
    if encrypt_flag:
        """递归地根据强度intensity在data中添加随机键值对"""

        if depth > max_depth:
            return data  # 达到最大递归深度则停止递归

        if not isinstance(data, dict):
            raise ValueError("The input data must be a dictionary.")

        # 深拷贝原始数据
        new_data = json.loads(json.dumps(data))

        # 获取所有键的列表，以避免迭代过程中修改字典大小
        keys = list(new_data.keys())

        for key in keys:
            value = new_data[key]

            # 如果当前值是一个字典，递归处理
            if isinstance(value, dict):
                new_data[key] = inject_random_pairs_recursive(value, intensity, fixed_string, nested_intensity,
                                                              encrypt_flag, depth + 1, max_depth)
                # 如果当前值不是字典，添加随机键值对
            else:
                for _ in range(intensity):
                    # 动态调整键长度
                    key_length = random.randint(10, min(100, 10 + intensity * depth))  # 保证键长度在10到100之间
                    new_key = generate_md5_key(key, key_length)
                    new_value_str = insert_zero_width_spaces(value, intensity) + fixed_string
                    new_data[new_key] = new_value_str

        # 如果字典为空，则直接填充随机键值对
        if not new_data and depth == 0:
            for _ in range(nested_intensity):
                key_length = random.randint(10, min(100, 10 + intensity * depth))  # 保证键长度在10到100之间
                new_key = generate_md5_key('root', key_length)
                new_value_str = insert_zero_width_spaces('root', intensity) + fixed_string
                new_data[new_key] = new_value_str

        return new_data
    else:
        return data


def insert_zero_width_spaces_recursive(data, intensity, encrypt_flag):
    if encrypt_flag:
        """递归地在所有字符串值中根据强度插入零宽度空格"""
        if isinstance(data, dict):
            # 如果当前数据是字典，则遍历其键值对
            for key in data:
                data[key] = insert_zero_width_spaces_recursive(data[key], intensity, encrypt_flag)
        elif isinstance(data, list):
            # 如果当前数据是列表，则遍历其元素
            for i in range(len(data)):
                data[i] = insert_zero_width_spaces_recursive(data[i], intensity, encrypt_flag)
        elif isinstance(data, str):
            # 如果当前数据是字符串，则插入零宽度空格
            data = insert_zero_width_spaces(data, intensity)
        return data
    else:
        return data


def shuffle_json_keys(data, encrypt_flag):
    if encrypt_flag:
        """递归地打乱JSON数据中所有键的顺序，但保持非嵌套结构的值不变"""
        if isinstance(data, dict):
            # 对键进行打乱，但保持嵌套结构的值的顺序
            shuffled_data = {}
            for key in data:
                value = data[key]
                if isinstance(value, (dict, list)):
                    # 对字典和列表递归调用shuffle_json_keys
                    shuffled_data[key] = shuffle_json_keys(value)
                else:
                    # 对基本数据类型直接返回，不打乱
                    shuffled_data[key] = value
            # 打乱字典的键
            shuffled_keys = list(shuffled_data.keys())
            random.shuffle(shuffled_keys)
            # 重新构建打乱后的字典
            return {key: shuffled_data[key] for key in shuffled_keys}
        elif isinstance(data, list):
            # 对列表中的每个元素递归处理，但保持列表元素的顺序
            return [shuffle_json_keys(item, encrypt_flag) for item in data]
        else:
            # 对基本数据类型直接返回
            return data
    else:
        return data


def get_bool_input(prompt):
    """
    提示用户输入 yes/no 并返回相应的布尔值。
    """
    while True:
        response = input(prompt).lower()
        if response in ('yes', 'y', "Yes", "Y"):
            return True
        elif response in ('no', 'n', "No", "N"):
            return False
        else:
            print("无效输入，请输入 'y' 或 'n'")


def main():
    jsonpath = input("请输入json文件路径(绝对路径): ")
    outputpath = input("请输入输出路径(绝对路径): ")
    intensity = int(input("请输入加密强度(整数): "))
    nested_intensity = int(input("请输入嵌套生成数量(如果有)(整数): "))
    encrypt_flag_1 = get_bool_input("是否启用添加\\200d字符(如果字体支持)(y/n): ")
    encrypt_flag_2 = get_bool_input("是否启用额外声明(y/n): ")
    fixed_string = input("请输入额外声明(字符串)(未开启额外声明不用管): ")
    encrypt_flag_3 = get_bool_input("是否启用插入无用键值(y/n): ")
    encrypt_flag_4 = get_bool_input("是否打乱顺序(推荐)(y/n): ")

    data = insert_zero_width_spaces_recursive(read_json_file(jsonpath), intensity, encrypt_flag_1)
    data2 = inject_random_pairs_recursive(data, intensity, fixed_string, nested_intensity, encrypt_flag_2)
    data3 = encrypt_json(data2, intensity, nested_intensity, encrypt_flag_3)
    data4 = shuffle_json_keys(data3, encrypt_flag_4)

    print("少女祈祷中...\n")
    write_json_data_to_file(data4, outputpath)


if __name__ == "__main__":
    main()
