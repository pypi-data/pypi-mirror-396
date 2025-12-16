"""
#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
@Project :vgis_python_package
@File    :utils.py
@IDE     :PyCharm
@Author  :chenxw
@Date    :2025/8/1 14:17
@Descr:
"""
import base64
import json
import os
import platform
import re
import time
from datetime import datetime
from io import BytesIO
from typing import List

import cv2
import psycopg2
import requests
from PIL import Image
from toollib.guid import SnowFlake

ALLOWED_ARCHIVE_EXTENSIONS = {'zip', 'tar', 'gz', 'bz2'}

platformType = platform.system().lower()



# 调用AI服务
@staticmethod
def toggle_ai_service(url, pay_json):
    headers = {
        # 'Authorization': 'Token {}'.format(token_value),
        'Content-Type': 'application/json',
        'Cookie': 'sessionid=k22jiy8ktaqh13ddbdu5tfdp8dgizr6w'
    }
    payload = json.dumps(pay_json)
    response = requests.request("POST", url, headers=headers, data=payload)
    return json.loads(response.text)


# 上传文件
@staticmethod
def upload_file_service(upload_url, file_path):
    with open(file_path, 'rb') as f:
        files = {'file': (file_path.split('/')[-1], f)}
        response = requests.post(upload_url, files=files)
        # 返回JSON响应
    if "file_path" in response.json():
        return response.json()["file_path"]
    else:
        assert "文件上传失败"

# 上传并解压获取解压后的文件夹路径
@staticmethod
def upload_extract_filezip_and_get_dir_service(upload_url, zip_file_path):
    with open(zip_file_path, 'rb') as f:
        files = {'file': (zip_file_path.split('/')[-1], f)}
        response = requests.post(upload_url, files=files)
        # 返回JSON响应
    if "extract_dir" in response.json():
        return response.json()["extract_dir"]
    else:
        assert "压缩包上传失败"



# 上传并解压获取指定解压后指定后缀的文件路径
@staticmethod
def upload_extract_filezip_and_get_file_by_extension_service(upload_url, zip_file_path, analysis_file_extension):
    with open(zip_file_path, 'rb') as f:
        files = {'file': (zip_file_path.split('/')[-1], f)}
        querystring = {"analysis_file_extension": analysis_file_extension}
        response = requests.post(upload_url, files=files, params=querystring)
        # 返回JSON响应
    if "analysis_file_path" in response.json():
        return response.json()["analysis_file_path"]
    else:
        assert "压缩包上传失败"


# 获取唯一码：雪花ID
@staticmethod
def snowflakeId():
    # worker_id  = 0,
    # datacenter_id = 0,
    snow = SnowFlake(worker_id_bits=0, datacenter_id_bits=0)
    return snow.gen_uid()


# 将base64字符串保存为图片
@staticmethod
def save_base64_image(base64_str: str, output_path: str):
    """
    将Base64图像数据保存到本地文件，自动从Base64字符串中提取图像类型

    参数:
    base64_str: 包含MIME类型前缀的Base64字符串
    output_path: 输出文件路径（可以带或不带扩展名）

    返回:
    实际保存的文件路径
    """
    try:
        # 提取MIME类型（如"image/jpeg"）
        mime_match = re.search(r'data:(image/[^;]+);base64', base64_str)
        if not mime_match:
            raise ValueError("无效的Base64图像格式，缺少MIME类型信息")

        mime_type = mime_match.group(1)
        # 提取纯Base64数据（移除前缀）
        base64_data = base64_str.split(",")[1]

        # 将MIME类型映射到文件扩展名
        mime_to_ext = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
            "image/bmp": ".bmp",
            "image/tiff": ".tiff",
            "image/svg+xml": ".svg"
        }

        # 获取文件扩展名
        file_ext = mime_to_ext.get(mime_type.lower())
        if not file_ext:
            # 对于未知类型，使用MIME类型中的最后部分作为扩展名
            file_ext = "." + mime_type.split("/")[-1]
            print(f"警告: 未知的图像类型 '{mime_type}', 使用扩展名 '{file_ext}'")

        # 确保输出路径有正确的扩展名
        filename, orig_ext = os.path.splitext(output_path)
        if not orig_ext or orig_ext.lower() != file_ext:
            output_path = filename + file_ext

        # 解码并保存图像
        image_data = base64.b64decode(base64_data)
        with open(output_path, "wb") as f:
            f.write(image_data)

        print(f"图片已保存至: {output_path} (类型: {mime_type})")
        return output_path

    except (ValueError, IndexError) as e:
        print(f"Base64格式错误: {e}")
    except base64.binascii.Error as e:
        print(f"Base64解码失败: {e}")
    except IOError as e:
        print(f"文件写入失败: {e}")
    except Exception as e:
        print(f"未知错误: {e}")
    return None


# 获取指定路径图片的尺寸大小
@staticmethod
def get_size_of_image(image_path):
    # 打开图像文件
    img = Image.open(image_path)
    # 获取图像尺寸 (宽度, 高度)
    return img.size


# 获取url图片的尺寸大小
@staticmethod
def get_size_of_url_image_type(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    return img.size


# 获取视频文件信息
@staticmethod
def get_video_info(file_path):
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        raise ValueError("无法打开视频文件")

    # 获取宽度（分辨率）
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 获取总帧数和帧率
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # 计算时长（秒）
    duration = total_frames / fps if fps > 0 else 0

    cap.release()
    return {
        "width": width,  # 视频宽度（像素）
        "height": height,  # 视频高度（像素）
        "duration": duration,  # 视频时长（秒）
        "fps": fps  # 帧率（可选）
    }


# 针对推理结果，根据英文名获取中文名
@staticmethod
def get_predict_cname_by_ename(ename):
    if ename == "storagetank":
        return "储油罐"


# 获取文件路径列表中的后缀
@staticmethod
def get_file_extensions(file_paths: List[str], with_dot: bool = True) -> List[str]:
    """
    获取文件路径列表的后缀

    Args:
        file_paths: 文件路径列表
        with_dot: 是否包含点号，True返回".zip"，False返回"zip"

    Returns:
        后缀列表
    """
    extensions = []
    for file_path in file_paths:
        ext = os.path.splitext(file_path)[1]
        if not with_dot:
            ext = ext.lstrip('.')
        extensions.append(ext)
    return extensions[0]


# 判断文件名后缀是否在允许压缩名列表中
@staticmethod
def allowed_archive(filename):
    """检查文件是否为允许的压缩格式"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_ARCHIVE_EXTENSIONS


@staticmethod
def snowflakeId():
    # worker_id  = 0,
    # datacenter_id = 0,
    snow = SnowFlake(worker_id_bits=0, datacenter_id_bits=0)

    return snow.gen_uid()

def get_operate_db_info(task_id,host,port,user,password,db_name,dbengine,table_name):
    operate_db_info = {"db_conn_info": {"host": host, "port": port, "user": user, "password": password,
                                        "db_name": db_name, "dbengine": dbengine},
                       "update_sql": "update " + table_name + " set \"status\" = {status} , \"update_time\" = '{update_time}' where id =" + str(
                           task_id)}
    return operate_db_info
# 增加算法执行到进度表
def add_alg_task(task_id, table_name, task_id_field, task_status_field, alg_type, alg_model, db_info):
    # 获取当前时间
    now = datetime.now()
    # 将当前时间格式化为字符串
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")

    db_conn_info = db_info["db_conn_info"]
    insert_sql = "insert into " + table_name + " (\"" + task_id_field + "\",\"" + task_status_field + "\",\"type\",\"alg\",\"create_time\",\"update_time\") values(" + str(task_id) + ",-1,'" + str(alg_type) + "','" + str(alg_model) + "','" + str(time_str) + "','" + str(time_str) + "')"
    print(insert_sql)
    if "postgresql" in db_conn_info["dbengine"].lower() or "postgis" in db_conn_info["dbengine"].lower():
        # Connect to the database
        conn = psycopg2.connect(
            host=db_conn_info['host'],
            port=db_conn_info['port'],
            database=db_conn_info['db_name'],
            user=db_conn_info['user'],
            password=db_conn_info['password']
        )

        # Create a cursor object
        cur = conn.cursor()

        # insert record into the table
        cur.execute(insert_sql)

        # Commit the transaction
        conn.commit()

        # Close the cursor and connection
        cur.close()
        conn.close()

# 更新算法执行进度
def update_alg_progress(status, db_info):
    # 获取当前时间
    now = datetime.now()
    # 将当前时间格式化为字符串
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")

    db_conn_info = db_info["db_conn_info"]
    update_sql = db_info["update_sql"].replace("{status}", str(status)).replace("{update_time}", str(time_str))

    if "postgresql" in db_conn_info["dbengine"].lower() or "postgis" in db_conn_info["dbengine"].lower():
        # Connect to the database
        conn = psycopg2.connect(
            host=db_conn_info['host'],
            port=db_conn_info['port'],
            database=db_conn_info['db_name'],
            user=db_conn_info['user'],
            password=db_conn_info['password']
        )

        # Create a cursor object
        cur = conn.cursor()

        # update record inthe table
        cur.execute(update_sql)

        # Commit the transaction
        conn.commit()

        # Close the cursor and connection
        cur.close()
        conn.close()
