#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础使用示例 - never_primp
演示基本的 HTTP 请求方法和参数
"""

import sys
from never_primp import Client



client = Client(impersonate='chrome_142',proxy='http://127.0.0.1:9000',verify=False)
r = client.get('https://tls.browserleaks.com').text
client.get('https://tls.browserleaks.com',http1_only=True).text



