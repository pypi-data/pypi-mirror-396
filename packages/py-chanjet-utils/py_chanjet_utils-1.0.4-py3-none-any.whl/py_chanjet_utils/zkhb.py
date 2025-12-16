#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
=================================================
作者：[郭磊]
手机：[15210720528]
Email：[174000902@qq.com]
Gitee：https://gitee.com/guolei19850528/py_chanjet_utils.git
=================================================
"""

from types import NoneType

import httpx
import xmltodict
from addict import Dict
from bs4 import BeautifulSoup


class WebService(object):
    def __init__(self, base_url: str = ""):
        """
        chanjet u8+ 中科华博 WebService Class
        """
        self.base_url = base_url[:-1] if base_url.endswith("/") else base_url

    def op_get_data_set(self, sql: str = None, **kwargs):
        kwargs = kwargs if isinstance(kwargs, dict) else dict()
        kwargs.setdefault("method", "POST")
        kwargs.setdefault("url", f"{self.base_url}/estate/webService/ForcelandEstateService.asmx?op=GetDataSet")
        headers = kwargs.get("headers", dict())
        headers.setdefault("Content-Type", "text/xml; charset=utf-8")
        kwargs["headers"] = headers
        data = xmltodict.unparse(
            {
                "soap:Envelope": {
                    "@xmlns:soap": "http://schemas.xmlsoap.org/soap/envelope/",
                    "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                    "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                    "soap:Body": {
                        "GetDataSet": {
                            "@xmlns": "http://zkhb.com.cn/",
                            "sql": f"{sql}",
                        }
                    }
                }
            }
        )
        kwargs["data"] = data
        response = httpx.request(**kwargs)
        xml_doc = BeautifulSoup(response.text, features="xml")
        if isinstance(xml_doc, NoneType):
            return False, [], response
        results = Dict(
            xmltodict.parse(
                xml_doc.find("NewDataSet").encode(
                    "utf-8"))
        ).NewDataSet.Table
        if isinstance(results, list):
            return True, results, response
        if isinstance(results, dict) and len(results.keys()):
            return True, [results], response
        return None, None, response

    def query_actual_charge_bill_item_list(
            self,
            column_str: str = "",
            condition_str: str = "",
            order_by_str: str = "order by cfi.ChargeFeeItemID desc",
            **kwargs
    ):
        """
        按条件查询实际收费列表
        :param column_str: column str
        :param condition_str: condition str
        :param order_by_str: order by str
        :param kwargs: self.op_get_data_set(**kwargs)
        :return:
        """
        kwargs = kwargs if isinstance(kwargs, dict) else dict()
        sql = f"select {column_str} {','.join([
            'cml.ChargeMListID',
            'cml.ChargeMListNo',
            'cml.ChargeTime',
            'cml.PayerName',
            'cml.ChargePersonName',
            'cml.ActualPayMoney',
            'cml.EstateID',
            'cml.ItemNames',
            'ed.Caption as EstateName',
            'cfi.ChargeFeeItemID',
            'cfi.ActualAmount',
            'cfi.SDate',
            'cfi.EDate',
            'cfi.RmId',
            'rd.RmNo',
            'cml.CreateTime',
            'cml.LastUpdateTime',
            'cbi.ItemName',
            'cbi.IsPayFull',
        ])} {''.join([
            ' from chargeMasterList as cml',
            ' left join EstateDetail as ed on cml.EstateID=ed.EstateID',
            ' left join ChargeFeeItem as cfi on cml.ChargeMListID=cfi.ChargeMListID',
            ' left join RoomDetail as rd on cfi.RmId=rd.RmId',
            ' left join ChargeBillItem as cbi on cfi.CBillItemID=cbi.CBillItemID',
        ])} where 1=1 {condition_str} {order_by_str};";
        kwargs["sql"] = sql
        return self.op_get_data_set(**kwargs)
