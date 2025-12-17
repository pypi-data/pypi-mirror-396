#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author chentongming
# @date 2025/05/19

from tmutils.base.lark.larkConfig import larkConfig
import json
import lark_oapi as lark
from lark_oapi.api.wiki.v2 import *
from lark_oapi.api.bitable.v1 import *
import requests
from tmutils.base.download import fetch_url_with_retries

class larkOps(object):
    def __new__(cls, *args, **kwargs):
        # 调用父类的（object）的new方法，返回一个Ansible实例，这个实例传递给init的self参数
        return object.__new__(cls)

    def __init__(self,config:larkConfig,token,*args, **kwargs) -> None:
        self.config = config
        self.App_ID=self.config.App_ID
        self.App_Secret=self.config.App_Secret
        self.token=token
        # 创建client
        self.client = lark.Client.builder() \
            .app_id(self.App_ID) \
            .app_secret(self.App_Secret) \
            .log_level(lark.LogLevel.INFO) \
            .build()
    def __del__(self) -> None:...

    def get_knowledge_space_node_info(self,obj_type="wiki",*args, **kwargs):
        """
            获取知识空间节点信息
        """
        # 构造请求对象
        request: GetNodeSpaceRequest = GetNodeSpaceRequest.builder() \
            .token(self.token) \
            .obj_type(obj_type) \
            .build()
        # 发起请求
        response: GetNodeSpaceResponse = self.client.wiki.v2.space.get_node(request)
        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.wiki.v2.space.get_node failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            exit(127)
        # data=lark.JSON.marshal(response.data)
        # lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        return response.data

    def build_search_request(self, app_token, table_id, view_id, field_names, page_size, page_token=None, automatic_fields=False, filter_info=None):
        # 统一请求构建逻辑
        request_body = SearchAppTableRecordRequestBody.builder() \
            .view_id(view_id) \
            .field_names(field_names) \
            .automatic_fields(automatic_fields)
        
        # 如果有过滤条件
        if filter_info:
            request_body = request_body.filter(filter_info)
        
        # 构建请求
        request_builder = SearchAppTableRecordRequest.builder() \
            .app_token(app_token) \
            .table_id(table_id) \
            .page_size(page_size) \
            .request_body(request_body.build())
        
        # 添加page_token
        if page_token:
            request_builder = request_builder.page_token(page_token)

        return request_builder.build()

    def multidimensional_table_query_records(self, table_id, view_id, page_size=20, field_names=[], automatic_fields=False, page_token=None, isFilter=False, filter_field_name="合作进度", filter_operator="is", filter_value=["已发布"], *args, **kwargs):
        app_token = self.get_knowledge_space_node_info().node.obj_token
        
        # 构建过滤条件
        filter_info = None
        if isFilter:
            filter_info = FilterInfo.builder() \
                .conjunction("and") \
                .conditions([Condition.builder()
                            .field_name(filter_field_name)
                            .operator(filter_operator)
                            .value(filter_value)
                            .build()
                            ]) \
                .build()

        # 构建请求
        request = self.build_search_request(app_token, table_id, view_id, field_names, page_size, page_token, automatic_fields, filter_info)

        # 发起请求
        response: SearchAppTableRecordResponse = self.client.bitable.v1.app_table_record.search(request)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.bitable.v1.app_table_record.search failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            exit(127)
        
        # 返回处理后的数据
        # lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        return response.data

    def sheets_spreadsheets(self, range) -> dict:
        """
            如果知识库就是节点信息中的obj_token,云空间就是url中的token
            range设置为sheet_id
            默认就是获取所有数据
            后台需要开通：
            查看、评论、编辑和管理云空间中所有文件
            查看、评论和下载云空间中所有文件
            查看、评论、编辑和管理电子表格
            查看、评论和导出电子表格
        """
        doc_token = self.token

        # 构造请求对象
        request: lark.BaseRequest = lark.BaseRequest.builder() \
            .http_method(lark.HttpMethod.GET) \
            .uri("/open-apis/sheets/v2/spreadsheets/{}/values/{}".format(doc_token,range)) \
            .token_types({lark.AccessTokenType.TENANT}) \
            .build()

        # 发起请求
        response: lark.BaseResponse = self.client.request(request)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.request failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")

        # 处理业务结果
        # lark.logger.info(str(response.raw.content, lark.UTF_8))
        str_data=str(response.raw.content, lark.UTF_8)
        data=json.loads(str_data)
        return data


class tenant_access_token(object):
    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self,config:larkConfig,*args, **kwargs) -> None:
        self.App_ID=self.config.App_ID
        self.App_Secret=self.config.App_Secret
        self.get_token()
        self.headers = {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json; charset=utf-8"
        }

    def __del__(self) -> None:...

    def get_token(self):
        url = f"https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers={
            "Content-Type":"application/json; charset=utf-8"
        }
        body = {
            "app_id": self.App_ID,
            "app_secret": self.App_Secret
    }
        response = fetch_url_with_retries(method="POST",url=url, headers=headers, data=json.dumps(body))
        # print(response.json())
        self.tenant_access_token=response.json().get("tenant_access_token")

    def sheets_prepend_values(self,spreadsheet_token: str, sheet_range: str, values: list[list]) -> dict:
        """
        写入飞书表格
        :param token: 飞书 tenant 或 user access token（形如 t-xxxx）
        :param spreadsheet_token: 表格 token（非 URL）
        :param sheet_range: 写入范围，如 'Sheet1!A1:F5'
        :param values: 二维数组，每个元素是一行数据，例如 [["a", 1, "url", 12], ["b", 2, 3, "email"]]
        :return: 返回接口响应（字典）
        """
        url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values_prepend"


        body = {
            "valueRange": {
                "range": sheet_range,
                "values": values
            }
        }

        response = fetch_url_with_retries(method="POST",url=url, headers=self.headers, data=json.dumps(body))
        try:
            return response.json()
        except Exception as e:
            return {"error": str(e), "status_code": response.status_code}
        
    def sheets_get_info(self, spreadsheet_token: str):
        """
            https://open.feishu.cn/document/server-docs/docs/sheets-v3/spreadsheet-sheet/get
        """
        url = f"https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query"

        response = fetch_url_with_retries(url=url, headers=self.headers)
        try:
            return response.json()
        except Exception as e:
            return {"error": str(e), "status_code": response.status_code}

    def sheets_get_sheet_info(self, spreadsheet_token: str, sheet_id: str):
        """
            https://open.feishu.cn/document/server-docs/docs/sheets-v3/spreadsheet-sheet/get
        """
        url = f"https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/{sheet_id}"

        response = fetch_url_with_retries(url=url, headers=self.headers)
        try:
            return response.json()
        except Exception as e:
            return {"error": str(e), "status_code": response.status_code}

    def sheets_clear_sheet(self, spreadsheet_token: str, sheet_id: str,batch_size: int = 4000) -> None:
        """
            https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/prepend-data
            一次最多删除4999个需要从1开始而且必须保留一行
        """
        url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/dimension_range"

        if batch_size > 4999:
            batch_size = 4999

        while(True):
            time.sleep(3)
            info_data=self.sheets_get_sheet_info(spreadsheet_token=spreadsheet_token,sheet_id=sheet_id)
            # json_print(info_data)
            try:
                row_count=int(info_data['data']['sheet']['grid_properties']['row_count'])
            except Exception as e:
                row_count=0
            if(row_count==1):break
            if(batch_size>row_count):
                body = {
                    "dimension":{
                        "sheetId":sheet_id,
                        "majorDimension":"ROWS",
                        "startIndex":2,
                        "endIndex":row_count
                    }
                }
                response = fetch_url_with_retries(method="DELETE",retries=3,url=url, headers=self.headers, data=json.dumps(body))
                if(response==None):
                    print("文档有异常请检查,睡眠10秒钟")
                    time.sleep(10)
                # print(response.text)
            else:
                body = {
                    "dimension":{
                        "sheetId":sheet_id,
                        "majorDimension":"ROWS",
                        "startIndex":2,
                        "endIndex":batch_size
                    }
                }
                response = fetch_url_with_retries(method="DELETE",retries=3,url=url, headers=self.headers, data=json.dumps(body))
                # print(response.text)
                if(response==None):
                    print("文档有异常请检查,睡眠10秒钟")
                    time.sleep(10)

    def sheets_clear_first_row(self, spreadsheet_token: str, sheet_id: str) -> dict:
        """
        清空飞书多维表格第一行的所有值
        """
        url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/dimension_range"
        body = {
                "dimension":{
                    "sheetId":sheet_id,
                    "majorDimension":"ROWS",
                    "startIndex":1,
                    "endIndex":1
                }
            }
        fetch_url_with_retries(method="DELETE",retries=3,url=url, headers=self.headers, data=json.dumps(body))

    def sheets_write_first_row(self, spreadsheet_token: str, sheet_name: str, values: list[list]) -> dict:

        url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values"

        body = {
            "valueRange":{
                "range": sheet_name+"!A1:Z1",
                "values": values
            }
        }

        write_response = fetch_url_with_retries(
            method="PUT",
            url=url,
            headers=self.headers,
            data=json.dumps(body)
        )

        try:
            return write_response.json()
        except Exception as e:
            return {"error": str(e), "status_code": write_response.status_code}


    def base_batch_write_record(self,app_token,table_id,data):
        """
        base 飞书多维表格
        批量数据写入
        在多维表格数据表中新增多条记录，单次调用最多新增 1,000 条记录。
        """
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create"
        # data = {
        #     "records": [
        #         {"fields": {"GID": "张三", "获取时间": "内容1", "邮箱": "内容1", "标签": "内容1", "是否认证": "内容1"}},
        #         {"fields": {"GID": "张", "获取时间": "内容121", "邮箱": "内123容1", "标签": "内sda容1", "是否认证": "内容asd1"}},
        #     ]
        # }
        fetch_url_with_retries(method="POST",url=url,data=json.dumps(data),headers=self.headers)
