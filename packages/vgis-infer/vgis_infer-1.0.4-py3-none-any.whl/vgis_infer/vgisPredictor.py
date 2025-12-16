#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    :  2025/8/1 14:15
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : vgisPredictor.py
# @Descr   : AI预测器
# @Software: PyCharm
import os.path
import uuid

from vgis_infer import utils
from vgis_infer.utils import get_file_extensions, allowed_archive


# 直接对接遥感AI算法发布接口，不是服务网关接口
# 图片预测器
class VGISImagePredictor:
    # 初始化
    def __init__(self, common_ai_service_url, object_detect_ai_service_url, change_detect_ai_service_url):
        self.common_ai_service_url = common_ai_service_url
        self.object_detect_ai_service_url = object_detect_ai_service_url
        self.change_detect_ai_service_url = change_detect_ai_service_url

    # 对图片进行目标识别(支持单个或多个图片）
    # image_datas里是数组
    def predictor_image(self, image_datas, params):
        # 请求AI服务
        payjson = {}
        payjson["input_path"] = image_datas
        payjson["object_name"] = params["object_name"]
        payjson["alg_model"] = params["alg_model"]
        payjson["conf_value"] = params["conf_value"]
        payjson["iou_value"] = params["iou_value"]
        payjson["source_type"] = "image"
        if "pic_type" not in params:
            params["pic_type"] = "common_pics"
        payjson["pic_type"] = params["pic_type"]
        payjson["alg_result"] = "{}_result.json".format(uuid.uuid4())
        if "is_segment" in params:
            payjson["is_segment"] = params["is_segment"]
            payjson["segment_method"] = params["segment_method"]
        if "is_save_db" in params:
            payjson["is_save_db"] = params["is_save_db"]
            payjson["operate_db_info"] = params["operate_db_info"]

        image_widths = []
        image_heights = []
        # 普通图片
        if params["pic_type"] == "common_pics":
            if params["image_type"] == "url":
                for image_data in image_datas:
                    image_width, image_height = utils.get_size_of_url_image_type(image_data)
                    image_widths.append(image_width)
                    image_heights.append(image_height)
            if params["image_type"] == "base_64":
                payjson["input_path"] = []
                for image_data in image_datas:
                    image_path = os.path.join(os.getcwd(), "tmp", uuid.uuid4().hex + ".jpg")
                    image_path = utils.save_base64_image(image_data, image_path)
                    image_width, image_height = utils.get_size_of_image(image_path)
                    image_widths.append(image_width)
                    image_heights.append(image_height)
                    upload_file_path = utils.upload_file_service(self.common_ai_service_url + "/upload", image_path)
                    payjson["input_path"].append(upload_file_path)
                    os.remove(image_path)
            if params["image_type"] == "path":
                payjson["input_path"] = []
                for image_data in image_datas:
                    image_width, image_height = utils.get_size_of_image(image_data)
                    image_widths.append(image_width)
                    image_heights.append(image_height)
                    upload_file_path = utils.upload_file_service(self.common_ai_service_url + "/upload", image_data)
                    payjson["input_path"].append(upload_file_path)
        # 空间图片
        elif params["pic_type"] == "spatial_pic":
            payjson["bands"] = params["bands"]
            payjson["input_path"] = []
            payjson["epsg_value"] = params["epsg_value"]
            extension = get_file_extensions(image_datas, with_dot=True)
            for image_data in image_datas:
                if allowed_archive(extension):
                    upload_analysis_file_path = utils.upload_extract_filezip_and_get_file_by_extension_service(
                        self.common_ai_service_url + "/upload-and-extract", image_data,
                        params["analysis_file_extension"])
                else:
                    upload_analysis_file_path = utils.upload_file_service(self.common_ai_service_url + "/upload",
                                                                          image_data)
                payjson["input_path"].append(upload_analysis_file_path)

        # 支持对
        # token_value = utils.get_ai_service_token(self.ai_service_url)
        return_results = utils.toggle_ai_service(self.object_detect_ai_service_url + "/vgis_object_detect", payjson)
        all = {}

        index = 0
        if return_results["success"]:
            all["success"] = True
            all["info"] = "执行成功"
            res = {}
            res["version"] = "1.0"
            res["imageListInfers"] = []
            if params["pic_type"] == "common_pics":
                for result_box_list in return_results["yolo_results"]:
                    res2 = {}
                    res2["imageIndex"] = index
                    res2["imageInferResults"] = []
                    res2["imagePath"] = image_datas[index] if params["image_type"] != "base_64" else None
                    res2["imageData"] = None
                    res2["imageWidth"] = image_widths[index]
                    res2["imageHeight"] = image_heights[index]
                    for result_box in result_box_list:
                        xmin = result_box["xmin"]
                        ymin = result_box["ymin"]
                        xmax = result_box["xmax"]
                        ymax = result_box["ymax"]
                        name = result_box["name"]
                        confidence = result_box["confidence"]
                        res2["imageInferResults"].append(
                            {"id": utils.snowflakeId(), "label": name, "text": utils.get_predict_cname_by_ename(name),
                             "shapes": [
                                 {"shape_type": "hbb",
                                  "points": [[xmin, ymin], [xmin, ymax], [xmax, ymax], [xmax, ymin]]}],
                             "conf": confidence})
                    res["imageListInfers"].append(res2)
                    index += 1
            elif params["pic_type"] == "spatial_pic":
                pic_counts = return_results["pic_counts"]
                for pic_index in range(pic_counts):
                    obj = {}
                    obj["count"] = return_results["shp_counts"][pic_index]
                    # 返回在AI服务器上返回的分析结果shp路径
                    obj["shp_path"] = return_results["shp_paths"][pic_index]
                    # 将shp做后处理并转换geojson
                    payload = {}
                    payload["input_shp_path"] = obj["shp_path"]
                    payload["epsg_value"] = params["epsg_value"]
                    geojson_res = utils.toggle_ai_service(self.common_ai_service_url + "/handle_shp_geojson", payload)
                    obj["new_shp_path"] = geojson_res["new_shp_path"]
                    obj["new_cp_shp_path"] = geojson_res["new_cp_shp_path"]
                    obj["all_geojson_path"] = geojson_res["all_geojson_path"]
                    obj["all_geojson_url"] = geojson_res["all_geojson_url"]
                    obj["all_zip_path"] = geojson_res["all_zip_path"]
                    obj["all_zip_url"] = geojson_res["all_zip_url"]
                    payload = {}
                    # geoserver要发布的shp路径(拷贝到容器共享目录里的，宿主机geoserver才能访问到）
                    payload["input_shp_path"] = obj["new_cp_shp_path"]
                    # 发布shp服务
                    publish_res = utils.toggle_ai_service(self.common_ai_service_url + "/publish_shp_service", payload)
                    obj["topojson_vector_tiles_url"] = publish_res["topojson_vector_tiles_url"]
                    obj["geojson_vector_tiles_url"] = publish_res["geojson_vector_tiles_url"]
                    obj["utfgrid_vector_tiles_url"] = publish_res["utfgrid_vector_tiles_url"]
                    obj["mvt_vector_tiles_url"] = publish_res["mvt_vector_tiles_url"]
                    res["imageListInfers"].append(obj)
            all["data"] = res
        else:
            all["success"] = False
            all["info"] = return_results["info"]
        return all

    # 对图片对进行变化检测(支持多个图片对）
    # image_datas里是对象数组[{"img_before_path":img_before_path,"img_after_path":img_after_path}]
    def change_pair_image(self, image_datas, params):
        # 请求AI服务
        payjson = {}
        payjson["input_path"] = image_datas
        payjson["object_type"] = params["object_type"]
        payjson["alg_model"] = params["alg_model"]
        payjson["alg_result"] = "{}_result.json".format(uuid.uuid4())
        if "is_segment" in params:
            payjson["is_segment"] = params["is_segment"]
            payjson["segment_method"] = params["segment_method"]
        if "sat_seg_method" not in params:
            payjson["sat_seg_method"] = "default"
        else:
            payjson["sat_seg_method"] = params["sat_seg_method"]
        if "sat_obj_method" not in params:
            payjson["sat_obj_method"] = "objdetection"
        else:
            payjson["sat_obj_method"] = params["sat_obj_method"]
        if "is_save_db" in params:
            payjson["is_save_db"] = params["is_save_db"]
            payjson["operate_db_info"] = params["operate_db_info"]

        payjson["epsg_value"] = params["epsg_value"]
        payjson["alg_result"] = "{}_result.json".format(uuid.uuid4())
        # 针对多个图像对进行变化检测，需要调用多次AI服务
        return_results = []
        data_index = 0
        for image_data in image_datas:
            band = params["bands"][data_index]
            band = [band["before_band"], band["after_band"]]
            payjson["bands"] = band
            img_before_path = image_data["before_image"]
            img_after_path = image_data["after_image"]
            extension = get_file_extensions([img_before_path], with_dot=True)
            if allowed_archive(extension):
                upload_analysis_before_file_path = utils.upload_extract_filezip_and_get_file_by_extension_service(
                    self.common_ai_service_url + "/upload-and-extract", img_before_path,
                    params["analysis_file_extension"])
                upload_analysis_after_file_path = utils.upload_extract_filezip_and_get_file_by_extension_service(
                    self.common_ai_service_url + "/upload-and-extract",
                    img_after_path,
                    params[
                        "analysis_file_extension"])
            else:
                upload_analysis_before_file_path = utils.upload_file_service(self.common_ai_service_url + "/upload",
                                                                             img_before_path)
                upload_analysis_after_file_path = utils.upload_file_service(self.common_ai_service_url + "/upload",
                                                                            img_after_path)
            payjson["img_before_path"] = upload_analysis_before_file_path
            payjson["img_after_path"] = upload_analysis_after_file_path
            # token_value = utils.get_ai_service_token(self.ai_service_url)
            return_result = utils.toggle_ai_service(self.change_detect_ai_service_url + "/vgis_change_detect", payjson)
            return_results.append(return_result)

        all_result = {}
        all_result["version"] = "1.0"
        all_result["success"] = True
        all_result["info"] = "执行完成"
        all_result["data"] = []
        index = 0
        for result in return_results:
            res={}
            if result["success"]:
                res["success"] = True
                res["info"] = "执行成功"
                obj = {}
                obj["count"] = result["count"]
                # 返回在AI服务器上返回的分析结果shp路径
                obj["shp_path"] = result["shp_path"]
                # 将shp做后处理并转换geojson
                payload = {}
                payload["input_shp_path"] = obj["shp_path"]
                payload["epsg_value"] = params["epsg_value"]
                geojson_res = utils.toggle_ai_service(self.common_ai_service_url + "/handle_shp_geojson", payload)
                if geojson_res["success"]:
                    obj["new_shp_path"] = geojson_res["new_shp_path"]
                    obj["new_cp_shp_path"] = geojson_res["new_cp_shp_path"]
                    obj["all_geojson_path"] = geojson_res["all_geojson_path"]
                    obj["all_geojson_url"] = geojson_res["all_geojson_url"]
                    obj["all_zip_path"] = geojson_res["all_zip_path"]
                    obj["all_zip_url"] = geojson_res["all_zip_url"]
                    payload = {}
                    # geoserver要发布的shp路径(拷贝到容器共享目录里的，宿主机geoserver才能访问到）
                    payload["input_shp_path"] = obj["new_cp_shp_path"]
                    # 发布shp服务
                    publish_res = utils.toggle_ai_service(self.common_ai_service_url + "/publish_shp_service", payload)
                    obj["topojson_vector_tiles_url"] = publish_res["topojson_vector_tiles_url"]
                    obj["geojson_vector_tiles_url"] = publish_res["geojson_vector_tiles_url"]
                    obj["utfgrid_vector_tiles_url"] = publish_res["utfgrid_vector_tiles_url"]
                    obj["mvt_vector_tiles_url"] = publish_res["mvt_vector_tiles_url"]
                else:
                    obj["info"]="转换shp失败，请检查AI算法结果"
                res["pairimageChangeInfer"] = obj
            else:
                res["success"] = False
                res["info"] = result["info"]
            all_result["data"].append(res)
        return all_result

    # 发布geojson服务
    def publish_geojson_service(self, geojson_datas, params):
        all = {}
        all["publish_results"] = []
        try:
            for geojson_data in geojson_datas:
                upload_analysis_file_path = utils.upload_file_service(self.common_ai_service_url + "/upload",
                                                                      geojson_data)
                payjson = {}
                payjson["epsg_value"] = params["epsg_value"]
                payjson["input_geojson_path"] = upload_analysis_file_path
                # 发布shp服务
                publish_res = utils.toggle_ai_service(self.common_ai_service_url + "/publish_geojson_service", payjson)
                obj = {}
                obj["success"] = publish_res["success"]
                if obj["success"]:
                    obj["topojson_vector_tiles_url"] = publish_res["topojson_vector_tiles_url"]
                    obj["geojson_vector_tiles_url"] = publish_res["geojson_vector_tiles_url"]
                    obj["utfgrid_vector_tiles_url"] = publish_res["utfgrid_vector_tiles_url"]
                    obj["mvt_vector_tiles_url"] = publish_res["mvt_vector_tiles_url"]
                    obj["thumb_url"] = publish_res["thumb_url"]
                else:
                    obj["info"] = publish_res["info"]
                all["success"] = True
                all["publish_results"].append(obj)
        except Exception as e:
            all["success"] = False
            all["info"] = str(e)
        return all

    # 发布shp服务
    def publish_shp_service(self,shp_datas,params):
        all={}
        all["publish_results"]=[]
        try:
            for shp_data  in shp_datas:
                # shp是压缩包，上传到容器
                upload_analysis_file_path = utils.upload_extract_filezip_and_get_file_by_extension_service(
                    self.common_ai_service_url + "/upload-and-extract", shp_data,
                    ".shp")
                payjson = {}
                payjson["epsg_value"] = params["epsg_value"]
                payjson["input_shp_path"]=upload_analysis_file_path
                # 发布shp服务
                publish_res = utils.toggle_ai_service(self.common_ai_service_url + "/publish_shp_service", payjson)
                obj={}
                obj["success"] = publish_res["success"]
                if obj["success"]:
                    obj["topojson_vector_tiles_url"] = publish_res["topojson_vector_tiles_url"]
                    obj["geojson_vector_tiles_url"] = publish_res["geojson_vector_tiles_url"]
                    obj["utfgrid_vector_tiles_url"] = publish_res["utfgrid_vector_tiles_url"]
                    obj["mvt_vector_tiles_url"] = publish_res["mvt_vector_tiles_url"]
                    obj["thumb_url"]=publish_res["thumb_url"]
                else:
                    obj["info"] = publish_res["info"]
                all["success"] = True
                all["publish_results"].append(obj)
        except Exception as e:
            all["success"] = False
            all["info"] = str(e)
        return all

    # 发布tif服务
    def publish_tif_service(self,tif_datas,params):
        all = {}
        all["publish_results"] = []
        try:
            for tif_data in tif_datas:
                upload_analysis_file_path = utils.upload_file_service(self.common_ai_service_url + "/upload",
                                                                      tif_data)
                payjson = {}
                payjson["epsg_value"] = params["epsg_value"]
                payjson["input_tif_path"] = upload_analysis_file_path
                # 发布shp服务
                publish_res = utils.toggle_ai_service(self.common_ai_service_url + "/publish_tif_service", payjson)
                obj = {}
                obj["success"] = publish_res["success"]
                if obj["success"]:
                    obj["raster_tiles_url"] = publish_res["raster_tiles_url"]
                    obj["thumb_url"] = publish_res["thumb_url"]
                else:
                    obj["info"] = publish_res["info"]
                all["success"] = True
                all["publish_results"].append(obj)
        except Exception as e:
            all["success"] = False
            all["info"] = str(e)
        return all

    # 发布jpg服务
    def publish_jpg_service(self, jpg_datas, params):
        all = {}
        all["publish_results"] = []
        try:
            for jpg_data in jpg_datas:
                # jpg是压缩包，上传到容器
                upload_analysis_file_path = utils.upload_extract_filezip_and_get_file_by_extension_service(
                    self.common_ai_service_url + "/upload-and-extract", jpg_data,
                    ".jpg")
                payjson = {}
                payjson["epsg_value"] = params["epsg_value"]
                payjson["input_jpg_path"] = upload_analysis_file_path
                # 发布jpg服务
                publish_res = utils.toggle_ai_service(self.common_ai_service_url + "/publish_jpg_service", payjson)
                obj = {}
                obj["success"] = publish_res["success"]
                if obj["success"]:
                    obj["raster_tiles_url"] = publish_res["raster_tiles_url"]
                    obj["thumb_url"] = publish_res["thumb_url"]
                else:
                    obj["info"] = publish_res["info"]
                all["success"] = True
                all["publish_results"].append(obj)
        except Exception as e:
            all["success"] = False
            all["info"] = str(e)
        return all

    # 地图瓦片下载服务
    def download_tiles_service(self, params):
        all = {}
        try:
            payjson = {}
            payjson["region_type"] = params["region_type"]
            payjson["region_points"] = params["region_points"]
            payjson["image_service_info"] = params["image_service_info"]
            payjson["is_multi_thread"] = params["is_multi_thread"]
            # 执行地图瓦片下载
            download_res = utils.toggle_ai_service(self.common_ai_service_url + "/download_tiles_service", payjson)
            all["success"] = download_res["success"]
            if all["success"]:
                all["tiles_pic_path"] = download_res["tiles_pic_path"]
            else:
                all["info"] = download_res["info"]
        except Exception as e:
            all["success"] = False
            all["info"] = str(e)
        return all

    # 模型训练
    def train_model_data(self,train_zip_data,params):
        all = {}
        try:
            upload_unzip_dir_path = utils.upload_extract_filezip_and_get_dir_service(
                self.common_ai_service_url + "/upload-and-extract", train_zip_data)
            payjson = {}
            payjson["train_params"] = params["train_params"]
            payjson["train_model"] = params["train_model"]
            payjson["train_type"] = params["train_type"]
            payjson["input_data_dir"] = upload_unzip_dir_path
            # 执行模型训练服务
            train_res = utils.toggle_ai_service(self.common_ai_service_url + "/train_model", payjson)
            all["success"] = train_res["success"]
            if all["success"]:
                all["train_metrics"] = train_res["train_metrics"]
                all["checkpoint_path"]=train_res["checkpoint_path"]
            else:
                all["info"] = train_res["info"]
        except Exception as e:
            all["success"] = False
            all["info"] = str(e)
        return all
# 视频预测器
class VGISVideoPredictor:
    # 初始化
    def __init__(self, common_ai_service_url, object_detect_ai_service_url, change_detect_ai_service_url):
        self.common_ai_service_url = common_ai_service_url
        self.object_detect_ai_service_url = object_detect_ai_service_url
        self.change_detect_ai_service_url = change_detect_ai_service_url

    # 对单个视频进行预测
    def predictor_video(self, video_data, params):
        # 请求AI服务
        payjson = {}
        payjson["input_path"] = video_data
        payjson["object_name"] = params["object_name"]
        payjson["alg_model"] = params["alg_model"]
        payjson["conf_value"] = params["conf_value"]
        payjson["iou_value"] = params["iou_value"]
        payjson["source_type"] = "video"
        payjson["alg_result"] = "{}_result.json".format(uuid.uuid4())

        if params["video_type"] == "base_64":
            payjson["video_type"] = "video_frame_pics"
            payjson["input_path"] = []
            frame_index = 0
            for image_data in video_data:
                image_path = os.path.join(os.getcwd(), uuid.uuid4().hex + ".jpg")
                image_path = utils.save_base64_image(image_data, image_path)
                if frame_index == 0:
                    video_width, video_height = utils.get_size_of_image(image_path)
                upload_file_path = utils.upload_file_service(self.common_ai_service_url + "/upload", image_path)
                payjson["input_path"].append(upload_file_path)
                os.remove(image_path)

        if params["video_type"] == "path" or params["video_type"] == "url" or params["video_type"] == "stream":
            if params["video_type"] == "stream":
                payjson["video_type"] = "video_stream"
            else:
                payjson["video_type"] = "video_file"
            payjson["input_path"] = []
            for video_file in video_data:
                video_info = utils.get_video_info(video_file)
                video_width = video_info["width"]
                video_height = video_info["height"]
                if params["video_type"] == "path":
                    upload_file_path = utils.upload_file_service(self.common_ai_service_url + "/upload", video_file)
                    payjson["input_path"].append(upload_file_path)
                else:
                    payjson["input_path"].append(video_file)
        # token_value = utils.get_ai_service_token(self.ai_service_url)
        return_results = utils.toggle_ai_service(self.object_detect_ai_service_url + "/vgis_object_detect", payjson)

        all = {}

        index = 0
        if return_results["success"]:
            all["success"] = True
            all["info"] = "执行成功"
            res = {}
            res["version"] = "1.0"
            res["videoInfers"] = []
            for result_box_list in return_results["yolo_results"]:
                res2 = {}
                res2["frameIndex"] = index
                res2["imageInferResults"] = []

                for result_box in result_box_list:
                    xmin = result_box["xmin"]
                    ymin = result_box["ymin"]
                    xmax = result_box["xmax"]
                    ymax = result_box["ymax"]
                    name = result_box["name"]
                    confidence = result_box["confidence"]
                    res2["imageInferResults"].append(
                        {"id": utils.snowflakeId(), "lable": name, "text": utils.get_predict_cname_by_ename(name),
                         "shapes": [
                             {"shape_type": "hbb", "points": [[xmin, ymin], [xmin, ymax], [xmax, ymax], [xmax, ymin]]}],
                         "conf": confidence})
                res["videoInfers"].append(res2)
                index += 1
            res["videoPath"] = video_data[0] if params["video_type"] != "base_64" else None
            res["videoData"] = None
            res["videoHeight"] = video_height
            res["videoWidth"] = video_width
            all["data"] = res
        else:
            all["success"] = False
            all["info"] = return_results["info"]
        return all
