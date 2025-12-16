# 简介

gtc(generate test case) 是一个把http请求转换为测试代码的cli工具

## 功能

- [x] 支持解析curl命令
- [x] 支持解析postman文件
- [x] 支持解析swagger2文件
- [x] 支持解析openapi文件
- [x] 支持生成笛卡尔积测试脚本
- [x] 支持解析curl文件并生成Jmeter性能脚本
- [x] 支持解析curl文件并生成Locust性能脚本

## 安装

```bash
pip3 install gentccode
gtc version
```

## 使用

1. 执行下面命令,会在当前目录生成api文件(`api.yaml`)和测试代码的脚本文件(`test_case.py`)

    ```bash
    gtc curl curl.txt -a res.code=0
    gtc postman postman.json
    gtc swagger2 swagger.json
    ```

2. 根据笛卡尔积算法生成用例脚本

    ```bash
    # 对请求中的body进行操作
    gtc cp -n . -p body curl.txt
    gtc cp -n filter. -p body curl.txt

    # 对请求中的query param进行操作
    gtc cp -n . -p query curl.txt
    ```

3. 执行下面命令,会生成对应的压测脚本

    ```bash
    # jsonassert 是对response的断言, rate 是tps, time 是 5min
    gtc jmeter curl.txt --jsonassert code=0 --rate 10 --time 5
    # locust脚本 
    gtc locust curl.txt
    ```

## 已知问题

- 若postman文件中有变量,则不会生成相对应的代码块.