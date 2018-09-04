#高德POI搜索爬取方法
##每次请求最多返回1000个POI信息
from urllib import request
import json
import pandas as pd
import numpy as np

#导入坐标系转换py脚本
import sys
sys.path.append(r"D:/Workspace/JupyterNotebook\ipynb")
import gcj02towgs84 as gw

def gdmap_poi_api(poi_url_dict,keep_info,csv_path):
    """
    高德POI搜索爬取
    
    Parameters
    -----------
    poi_url_dict：参考“高德地图POI搜索—>关键词搜索—>请求参数”的内容进行设置
    keep_info：POI搜索结果中要保留的字段，参考“高德地图POI搜索—>关键词搜索—>返回结果参数说明”的内容进行设置
    csv_path：搜索结果保存的csv路径及文件名
    
    
    Attributes
    -----------
    POI搜索结果直接保存为csv文件
    
    References
    ----------    
    高德地图POS搜索API文档：https://lbs.amap.com/api/webservice/guide/api/search
    
    Examples
    --------
    poi_url_dict = {"base_url" : "https://restapi.amap.com/v3/place/text?"
               ,"key" : "ad64478e9f517ad17c5876d84ef8b24a"              #请求高德服务权限标识
               ,"types" : "150500"                                      #查询POI类型，地铁站
               ,"city" : "440304"                                       #查询城市,深圳福田
               ,"citylimit" : "true"                                    #仅返回指定城市数据，可选true/false
               ,"output" : "json"                                       #返回数据格式类型，可选JSON、XML
               ,"extensions" : "all"
               }
    keep_info = ["name","type","typecode","biz_type","address","location","pcode","pname","citycode","cityname","adcode","adname"]
    csv_path = "D:\Workspace\JupyterNotebook\ipynb\pois.csv" 
    gdmap_poi_api(poi_url_dict,keep_info,csv_path)
    
    """
    #打印输入参数值
    print("\n1，输入参数值如下：")
    print("poi_url_dict: ")
    print(poi_url_dict)
    print("keep_info: ")
    print(keep_info)
    print("csv_path: ")
    print(csv_path)
    #拼接POI搜索的url
    print("\n2，拼接POI搜索的url")
    if "base_url" in poi_url_dict and poi_url_dict["base_url"] != "":
        poi_url = poi_url_dict["base_url"]
        print("base url:" + poi_url)
        poi_url_dict.pop("base_url")
        for i in poi_url_dict.keys():
            poi_url = poi_url + str(i) + "=" + str(poi_url_dict[i]) + "&"
        print(poi_url)
    
    #获取POI搜索结果（返回json）
    print("\n3，获取POI搜索结果")
    #from urllib import request
    req = request.urlopen(poi_url)
    content = req.read().decode("utf-8")
    #print(content)

    #json转化为dict
    #import json
    content_dict = json.loads(content)
    print("完成")
    
    #数据预处理
    #import pandas as pd
    ##抽取指定信息
    print("\n4，数据预处理及经纬度坐标轴转换")
    poi_raw_df = pd.DataFrame.from_dict(content_dict["pois"])
    poi_keep_df = poi_raw_df[keep_info].fillna("Null")
    ##将高德地图GCJ02坐标转换为WGS84坐标
    lon_lat_df = poi_keep_df["location"].str.split(",",expand=True).rename(columns={0:"longitude_gcj02",1:"latitude_gcj02"})
    wgs84_df = pd.DataFrame(gw.gcj02towgs84(pd.to_numeric(lon_lat_df["longitude_gcj02"]),pd.to_numeric(lon_lat_df["latitude_gcj02"])),index=["longitude_wgs84","latitude_wgs84"],dtype=np.float64).T
    poi_rst_df = pd.concat([poi_keep_df.drop("location",axis=1),lon_lat_df,wgs84_df],axis=1)
    poi_rst_df.head(5)
    del poi_raw_df,poi_keep_df,lon_lat_df,wgs84_df
    print("完成")
    
    #保存为csv
    poi_rst_df.to_csv(csv_path,sep=",",index=False,header=True,float_format='%.14f')
    print("\n5，搜索结果已保存至：" + csv_path)