import json
import time
from urllib.parse import urlparse
from lxml import etree
from http_content_parser.api_parser import ApiModelParser

api_parser = ApiModelParser()


def jmeter_test_plan(root_xml):
    JmeterTestPlan = root_xml
    JmeterTestPlan.set("version", "1.2")
    JmeterTestPlan.set("properties", "5.0")
    JmeterTestPlan.set("jmeter", "5.6")
    return etree.SubElement(JmeterTestPlan, "hashTree")


def test_plan(parent_xml, plan_name):
    """

    :param parent_xml:
    :param plan_name:
    :return: etree object
    """
    testPlan = etree.SubElement(parent_xml, "TestPlan")
    testPlan.set("guiclass", "TestPlanGui")
    testPlan.set("testclass", "TestPlan")
    testPlan.set("testname", plan_name)
    testPlan.set("enabled", "true")
    stringProp = etree.SubElement(testPlan, "stringProp")
    stringProp.set("name", "TestPlan.comments")
    stringProp.text = ""
    boolProp1 = etree.SubElement(testPlan, "boolProp")
    boolProp1.set("name", "TestPlan.functional_mode")
    boolProp1.text = "false"
    boolProp2 = etree.SubElement(testPlan, "boolProp")
    boolProp2.set("name", "TestPlan.tearDown_on_shutdown")
    boolProp2.text = "false"
    boolProp3 = etree.SubElement(testPlan, "boolProp")
    boolProp3.set("name", "TestPlan.serialize_threadgroups")
    boolProp3.text = "true"
    elementProp = etree.SubElement(testPlan, "elementProp")
    elementProp.set("name", "TestPlan.user_defined_variables")
    elementProp.set("elementType", "Arguments")
    elementProp.set("guiclass", "ArgumentsPanel")
    elementProp.set("testclass", "Arguments")
    elementProp.set("testname", "User Defined Variables")
    elementProp.set("enabled", "true")
    collectionProp = etree.SubElement(elementProp, "collectionProp")
    collectionProp.set("name", "Arguments.arguments")
    stringProp2 = etree.SubElement(testPlan, "stringProp")
    stringProp2.set("name", "TestPlan.user_define_classpath")
    stringProp2.text = ""
    return etree.SubElement(parent_xml, "hashTree")


def thread_group(parent_xml):
    """

    :param parent_xml:
    :return: etree object
    """
    theadGroup = etree.SubElement(parent_xml, "ThreadGroup")
    theadGroup.set("guiclass", "ThreadGroupGui")
    theadGroup.set("testclass", "ThreadGroup")
    theadGroup.set("testname", "Thread Group")
    theadGroup.set("enabled", "true")
    stringProp = etree.SubElement(theadGroup, "stringProp")
    stringProp.set("name", "ThreadGroup.on_sample_error")
    stringProp.text = "continue"
    elementProp = etree.SubElement(theadGroup, "elementProp")
    set_kv_to_xml(
        elementProp,
        {
            "name": "ThreadGroup.main_controller",
            "elementType": "LoopController",
            "guiclass": "LoopControlPanel",
            "testclass": "LoopController",
            "testname": "Loop Controller",
            "enabled": "true",
        },
    )
    # boolProp = etree.SubElement(elementProp, "boolProp")
    # boolProp.set("name", "LoopController.continue_forever")
    # boolProp.text = "false"
    stringProp = etree.SubElement(elementProp, "stringProp")
    stringProp.set("name", "LoopController.loops")
    stringProp.text = "-1"
    stringProp = etree.SubElement(theadGroup, "stringProp")
    stringProp.set("name", "ThreadGroup.num_threads")
    stringProp.text = "1"
    stringProp = etree.SubElement(theadGroup, "stringProp")
    stringProp.set("name", "ThreadGroup.ramp_time")
    stringProp.text = "1"
    boolProp = etree.SubElement(theadGroup, "boolProp")
    boolProp.set("name", "ThreadGroup.scheduler")
    boolProp.text = "true"
    stringProp = etree.SubElement(theadGroup, "stringProp")
    stringProp.set("name", "ThreadGroup.duration")
    stringProp.text = "60"
    stringProp = etree.SubElement(theadGroup, "stringProp")
    stringProp.set("name", "ThreadGroup.delay")
    stringProp.text = ""
    return etree.SubElement(parent_xml, "hashTree")


def open_model_thread_group(parent_xml, rate, total_time):
    # 创建 OpenModelThreadGroup 元素
    open_model_thread_group = etree.SubElement(parent_xml, "OpenModelThreadGroup")
    open_model_thread_group.set("guiclass", "OpenModelThreadGroupGui")
    open_model_thread_group.set("testclass", "OpenModelThreadGroup")
    open_model_thread_group.set("testname", "Open Model Thread Group")

    # 创建 elementProp 元素
    element_prop = etree.SubElement(open_model_thread_group, "elementProp")
    element_prop.set("name", "ThreadGroup.main_controller")
    element_prop.set("elementType", "OpenModelThreadGroupController")

    # 创建 stringProp 元素
    string_prop = etree.SubElement(
        open_model_thread_group, "stringProp", name="OpenModelThreadGroup.schedule"
    )
    # TODO 模型固定,后续需要传入动态模型
    string_prop.text = f"rate(0/s) random_arrivals(10 s) rate({rate}/s) random_arrivals({total_time} min) rate({rate}/s)"
    return etree.SubElement(parent_xml, "hashTree")


def arguments(parent_xml):
    """

    :param parent_xml:
    :return: etree object
    """
    Arguments = etree.SubElement(parent_xml, "ThreadGroup")
    Arguments.set("guiclass", "ArgumentsPanel")
    Arguments.set("testclass", "Arguments")
    Arguments.set("testname", "User defined variables")
    Arguments.set("enabled", "true")
    collectionProp = etree.SubElement(Arguments, "collectionProp")
    collectionProp.set("name", "Arguments.arguments")
    return etree.SubElement(parent_xml, "hashTree")


def header_manager(parent_xml, headers: dict):
    HeaderManager = etree.SubElement(parent_xml, "HeaderManager")
    set_kv_to_xml(
        HeaderManager,
        {
            "guiclass": "HeaderPanel",
            "testclass": "HeaderManager",
            "testname": "HTTP Header Manager",
        },
    )
    collectionProp = etree.SubElement(HeaderManager, "collectionProp")
    collectionProp.set("name", "HeaderManager.headers")
    if headers:
        for k, v in headers.items():
            elementProp = etree.SubElement(collectionProp, "elementProp")
            elementProp.set("name", "")
            elementProp.set("elementType", "Header")

            stringProp = etree.SubElement(elementProp, "stringProp")
            stringProp.set("name", "Header.name")
            stringProp.text = k

            stringProp = etree.SubElement(elementProp, "stringProp")
            stringProp.set("name", "Header.value")
            stringProp.text = str(v)

    return etree.SubElement(parent_xml, "hashTree")


def response_assertion(parent_xml):
    responseAssertion = etree.SubElement(parent_xml, "ResponseAssertion")
    set_kv_to_xml(
        responseAssertion,
        {
            "guiclass": "AssertionGui",
            "testclass": "ResponseAssertion",
            "testname": "Response Assertion",
        },
    )
    collectionProp = etree.SubElement(responseAssertion, "collectionProp")
    collectionProp.set("name", "Asserion.test_strings")
    stringProp = etree.SubElement(responseAssertion, "stringProp")
    stringProp.set("name", "Assertion.custom_message")
    stringProp.text = ""  # 这个属性必须要有值,空值也得加上
    stringProp = etree.SubElement(responseAssertion, "stringProp")
    stringProp.set("name", "Assertion.test_field")
    stringProp.text = "Assertion.response_data"
    boolProp = etree.SubElement(responseAssertion, "boolProp")
    boolProp.set("name", "Assertion.assume_success")
    boolProp.text = "false"
    intProp = etree.SubElement(responseAssertion, "intProp")
    intProp.set("name", "Assertion.test_type")
    intProp.text = "16"
    return etree.SubElement(parent_xml, "hashTree")


def json_path_assertion(parent_xml, json_path_assert):
    json_path = json_path_assert.split("=")[0]
    json_value = json_path_assert.split("=")[1]
    jsonAssertion = etree.SubElement(parent_xml, "JSONPathAssertion")
    set_kv_to_xml(
        jsonAssertion,
        {
            "guiclass": "JSONPathAssertionGui",
            "testclass": "JSONPathAssertion",
            "testname": "JSON Assertion",
        },
    )
    stringProp = etree.SubElement(jsonAssertion, "stringProp")
    stringProp.set("name", "JSON_PATH")
    stringProp.text = f"$.{json_path}"
    stringProp = etree.SubElement(jsonAssertion, "stringProp")
    stringProp.set("name", "EXPECTED_VALUE")
    stringProp.text = f"{json_value}"
    boolProp = etree.SubElement(jsonAssertion, "boolProp")
    boolProp.set("name", "JSONVALIDATION")
    boolProp.text = "true"
    boolProp = etree.SubElement(jsonAssertion, "boolProp")
    boolProp.set("name", "EXPECT_NULL")
    boolProp.text = "false"
    boolProp = etree.SubElement(jsonAssertion, "boolProp")
    boolProp.set("name", "INVERT")
    boolProp.text = "false"
    boolProp = etree.SubElement(jsonAssertion, "boolProp")
    boolProp.set("name", "ISREGEX")
    boolProp.text = "false"
    return etree.SubElement(parent_xml, "hashTree")


def http_sampler_proxy(parent_xml, payload: dict):
    # sample list
    HTTPSamplerProxy = etree.SubElement(parent_xml, "HTTPSamplerProxy")
    set_kv_to_xml(
        HTTPSamplerProxy,
        {
            "guiclass": "HttpTestSampleGui",
            "testclass": "HTTPSamplerProxy",
            "testname": payload.get("sampler_comments", "")
            + "-"
            + str(payload.get("path")).replace("//", "/"),
            "enabled": "true",
        },
    )
    # parameter
    if payload.get("params_type") == "parameters":
        elementProp = etree.SubElement(HTTPSamplerProxy, "elementProp")
        set_kv_to_xml(
            elementProp,
            {
                "name": "HTTPsampler.Arguments",
                "elementType": "Arguments",
                "guiclass": "HTTPArgumentsPanel",
                "testclass": "Arguments",
                "testname": "User Defined Variables",
            },
        )
        collectionProp = etree.SubElement(elementProp, "collectionProp")
        collectionProp.set("name", "Arguments.arguments")
        if payload.get("params"):
            params = payload.get("params", {})
            params = json.loads(params)
            for k, v in params.items():
                elementProp = etree.SubElement(collectionProp, "elementProp")
                set_kv_to_xml(
                    elementProp,
                    {
                        "name": "",
                        "elementType": "HTTPArgument",
                    },
                )
                stringProp = etree.SubElement(elementProp, "stringProp")
                stringProp.set("name", "Argument.metadata")
                stringProp.text = "="

                boolProp = etree.SubElement(elementProp, "boolProp")
                boolProp.set("name", "HTTPArgument.use_equals")
                boolProp.text = "true"

                stringProp = etree.SubElement(elementProp, "stringProp")
                stringProp.set("name", "Argument.name")
                stringProp.text = k

                stringProp = etree.SubElement(elementProp, "stringProp")
                stringProp.set("name", "Argument.value")
                if isinstance(v, list):
                    v = "".join(v)
                stringProp.text = str(v)

    # postBodyRaw
    elif payload.get("params_type") == "body_data":
        boolProp = etree.SubElement(HTTPSamplerProxy, "boolProp")
        boolProp.set("name", "HTTPSampler.postBodyRaw")
        boolProp.text = "true"
        elementProp = etree.SubElement(HTTPSamplerProxy, "elementProp")
        set_kv_to_xml(
            elementProp,
            {"name": "HTTPsampler.Arguments", "elementType": "Arguments"},
        )
        collectionProp = etree.SubElement(elementProp, "collectionProp")
        collectionProp.set("name", "Arguments.arguments")

        elementProp = etree.SubElement(collectionProp, "elementProp")
        elementProp.set("name", "")
        elementProp.set("elementType", "HTTPArgument")

        boolProp = etree.SubElement(elementProp, "boolProp")
        boolProp.set("name", "HTTPArgument.always_encode")
        boolProp.text = "false"
        # body_data
        stringProp = etree.SubElement(elementProp, "stringProp")
        stringProp.set("name", "Argument.value")
        stringProp.text = json.dumps(payload.get("params"))

        stringProp = etree.SubElement(elementProp, "stringProp")
        stringProp.set("name", "Argument.metadata")
        stringProp.text = "="
    else:
        raise Exception("params_type is error")
    # host
    stringProp = etree.SubElement(HTTPSamplerProxy, "stringProp")
    stringProp.set("name", "HTTPSampler.domain")
    stringProp.text = payload.get("host")

    # port
    stringProp = etree.SubElement(HTTPSamplerProxy, "stringProp")
    stringProp.set("name", "HTTPSampler.port")
    stringProp.text = payload.get("port")

    # protocol
    stringProp = etree.SubElement(HTTPSamplerProxy, "stringProp")
    stringProp.set("name", "HTTPSampler.protocol")
    stringProp.text = payload.get("http_type", "http")

    # encoding
    stringProp = etree.SubElement(HTTPSamplerProxy, "stringProp")
    stringProp.set("name", "HTTPSampler.contentEncoding")
    stringProp.text = "UTF-8"

    # path
    stringProp = etree.SubElement(HTTPSamplerProxy, "stringProp")
    stringProp.set("name", "HTTPSampler.path")
    stringProp.text = str(payload.get("path")).replace("//", "/").replace("/{", "/${")

    # method
    stringProp = etree.SubElement(HTTPSamplerProxy, "stringProp")
    stringProp.set("name", "HTTPSampler.method")
    stringProp.text = payload.get("method", "").upper()

    # follow redirects
    boolProp = etree.SubElement(HTTPSamplerProxy, "boolProp")
    boolProp.set("name", "HTTPSampler.follow_redirects")
    boolProp.text = "true"

    # use keepalive
    boolProp = etree.SubElement(HTTPSamplerProxy, "boolProp")
    boolProp.set("name", "HTTPSampler.use_keepalive")
    boolProp.text = "true"

    # embedded url re
    stringProp = etree.SubElement(HTTPSamplerProxy, "stringProp")
    stringProp.set("name", "HTTPSampler.embedded_url_re")
    stringProp.text = ""

    # connect timeout
    stringProp = etree.SubElement(HTTPSamplerProxy, "stringProp")
    stringProp.set("name", "HTTPSampler.connect_timeout")
    stringProp.text = ""

    # response timeout
    stringProp = etree.SubElement(HTTPSamplerProxy, "stringProp")
    stringProp.set("name", "HTTPSampler.response_timeout")
    stringProp.text = ""

    # comments
    stringProp = etree.SubElement(HTTPSamplerProxy, "stringProp")
    stringProp.set("name", "TestPlan.comments")
    stringProp.text = payload.get("sampler_comments")


def controller(parent_xml, payloads: list, json_path_assert: str):
    for payload in payloads:
        GenericController = etree.SubElement(parent_xml, "GenericController")
        GenericController.set("guiclass", "LogicControllerGui")
        GenericController.set("testclass", "GenericController")
        GenericController.set("testname", payload.get("controller_name"))
        GenericController.set("enabled", "true")
        stringProp = etree.SubElement(GenericController, "stringProp")
        stringProp.set("name", "TestPlan.comments")
        stringProp.text = payload.get("description")
        shashTree = etree.SubElement(parent_xml, "hashTree")
        header_manager(shashTree, headers=json.loads(payload["header"]))
        # http sampler
        http_sampler_proxy(shashTree, payload)
        # http response assert, hasTree 必须要当前树下,不能做为参数传下去
        responseAssertionTree = etree.SubElement(shashTree, "hashTree")
        json_path_assertion(responseAssertionTree, json_path_assert)


def view_result_tree(parent_xml):
    """default status is disable"""
    result_collector = etree.SubElement(parent_xml, "ResultCollector")
    set_kv_to_xml(
        result_collector,
        {
            "guiclass": "ViewResultsFullVisualizer",
            "testclass": "ResultCollector",
            "testname": "View Results Tree",
            "enabled": "false",
        },
    )
    # 创建 ResultCollector 的子元素
    bool_prop = etree.SubElement(
        result_collector, "boolProp", name="ResultCollector.error_logging"
    )
    bool_prop.text = "false"

    obj_prop = etree.SubElement(result_collector, "objProp")
    etree.SubElement(obj_prop, "name", value="saveConfig")
    save_config_value = etree.SubElement(
        obj_prop, "value", {"class": "SampleSaveConfiguration"}
    )

    # 创建 SampleSaveConfiguration 的子元素
    elements_to_save = [
        "time",
        "latency",
        "timestamp",
        "success",
        "label",
        "code",
        "message",
        "threadName",
        "dataType",
        "assertions",
        "subresults",
        "bytes",
        "sentBytes",
        "url",
        "threadCounts",
        "idleTime",
        "connectTime",
    ]
    for element in elements_to_save:
        sub_element = etree.SubElement(save_config_value, element)
        sub_element.text = "true"

    etree.SubElement(save_config_value, "encoding").text = "false"
    etree.SubElement(save_config_value, "responseData").text = "false"
    etree.SubElement(save_config_value, "samplerData").text = "false"
    etree.SubElement(save_config_value, "xml").text = "false"
    etree.SubElement(save_config_value, "fieldNames").text = "true"
    etree.SubElement(save_config_value, "responseHeaders").text = "false"
    etree.SubElement(save_config_value, "requestHeaders").text = "false"
    etree.SubElement(save_config_value, "responseDataOnError").text = "false"

    etree.SubElement(save_config_value, "saveAssertionResultsFailureMessage").text = (
        "true"
    )
    etree.SubElement(save_config_value, "assertionsResultsToSave").text = "0"

    # 创建 stringProp 元素
    string_prop = etree.SubElement(result_collector, "stringProp", name="filename")
    string_prop.text = ""
    return etree.SubElement(parent_xml, "hashTree")


def set_kv_to_xml(obj_xml, datas):
    """

    :param obj_xml:
    :param datas:
    :return:
    """
    for key, value in datas.items():
        obj_xml.set(key, value)


def write_to_jmx(payloads: list, json_path_assert: str, rate: str, total_time: str):
    jmeterTestPlan = etree.Element("jmeterTestPlan")
    hashTree = jmeter_test_plan(jmeterTestPlan)
    testPlan = test_plan(hashTree, "autotest")
    # threadGroup = thread_group(testPlan)
    threadGroup = open_model_thread_group(testPlan, rate, total_time)
    controller(threadGroup, payloads, json_path_assert)
    view_result_tree(threadGroup)
    etree.tostring(jmeterTestPlan, pretty_print=True)
    tree = etree.ElementTree(jmeterTestPlan)
    now_date = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    tree.write(
        f"jmeter-{now_date}.jmx",
        pretty_print=True,
        xml_declaration=True,
        encoding="utf-8",
    )


def _get_param_by_method(payload: dict):
    if payload["method"] == "get":
        return payload["query_param"]
    else:
        return payload["body"]


def _get_param_type_by_method(method):
    if method == "get":
        return "parameters"
    else:
        return "body_data"


def _split_url(url):
    if url:
        parsed = urlparse(url)
        # 输出：https, www.example.com
        l = (parsed.netloc).split(":")
        port = ""
        if len(l) > 1:
            port = l[1]
        return parsed.scheme, l[0], port
    else:
        return "", "", ""


def _reduce_url_path(path):
    if path[0] != "/":
        return "/" + path
    else:
        return path


def convert_payloads_of_curl_to_jmx_file(
    curl_file_path, json_path_assert, rate, total_time
):
    http_payloads = api_parser.get_api_list_for_curl(curl_file=curl_file_path)
    jmx_payloads = convert_payloads_to_jmx_model(http_payloads=http_payloads)
    write_to_jmx(
        payloads=jmx_payloads,
        json_path_assert=json_path_assert,
        rate=rate,
        total_time=total_time,
    )


def convert_payloads_to_jmx_model(http_payloads: list[dict]) -> list:
    i = 1
    jmx_payloads = []
    for http_payload in http_payloads:
        p = {}
        temp_url = http_payload["original_url"]
        url_split = _split_url(temp_url)
        p["http_type"] = url_split[0]
        p["host"] = url_split[1]
        p["port"] = url_split[2]
        p["path"] = _reduce_url_path(http_payload["path"])
        p["method"] = http_payload["method"]
        p["header"] = http_payload["header"]
        p["params"] = _get_param_by_method(http_payload)
        p["params_type"] = _get_param_type_by_method(http_payload["method"])
        p["sampler_comments"] = str(i) + "-"
        p["controller_name"] = "controller" + str(i)
        i += 1
        jmx_payloads.append(p)
    return jmx_payloads
