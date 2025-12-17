from .http import request
import json
import xml.etree.ElementTree as ET
import re
import logging
logger = logging.getLogger(__name__)


def lesbRequest(ip: str, serviceName: str, operationName: str, params: dict):
    """
    <?xml version="1.0" encoding="GBK"?> <p><s sfzhm="ABC" /><s rsxtid="EFG" /></p>
    """

    p = ET.Element("p")

    for key, value in params.items():
        s = ET.SubElement(p, "s")
        s.set(key, value)

    xmlPara = f"""<?xml version="1.0" encoding="GBK"?>
{ET.tostring(p, encoding='unicode')}"""

    reqParams = {
        'serviceName': serviceName,
        'operationName': operationName,
        'xmlPara': xmlPara
    }

    response = request(
        f"{ip}/hsu/dwlesbservlet/serviceproxy/invokeService", reqParams)

    raw_content = response.content
    text = raw_content.decode('gbk')

    logger.info(text)

    return lesb2json(text)


def lesb2json(xml_content: str) -> dict:
    """将XML转换为指定格式的JSON对象

    参数:
        xml_content: XML格式的字符串

    返回:
        包含四个关键字段的字典
    """
    # 统一处理XML声明编码（GBK转UTF-8）
    xml_normalized = re.sub(
        r'<\?xml.*encoding\s*=\s*["\']GBK["\'].*\?>',
        '<?xml version="1.0" encoding="UTF-8"?>',
        xml_content,
        flags=re.IGNORECASE
    )

    # 解析XML并提取关键字段
    root = ET.fromstring(xml_normalized)
    result: dict = {
        "_lesb__errcode_": "",
        "errflag": "",
        "errtext": "",
        "perinfo": ""
    }

    # 遍历所有<s>标签提取属性
    for s_tag in root.findall('.//s'):
        attrs = s_tag.attrib
        for key in result.keys():
            if key in attrs:
                result[key] = attrs[key]

    logger.info(result)

    return result
