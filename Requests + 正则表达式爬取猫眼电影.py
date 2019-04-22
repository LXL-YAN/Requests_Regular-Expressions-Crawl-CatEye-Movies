import requests
from requests.exceptions import RequestException
import re
import json
from multiprocessing import Pool

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'}


# 提取单页内容，用try，except方便找bug
def get_one_page(url):
    try:
        response = requests.get(url, headers=headers)  # 传入headers参数
        if response.status_code == 200:
            return response.text
        return response.status_code
    except RequestException:  # 捕获这个类型的异常
        return Nonetemplates


def parse_one_page(html):  # 定义一个函数用来解析html代码
    # 生成一个正则表达式对象
    pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name"><a'  # 此处换行
                         + '.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p>'
                         + '.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)
    items = re.findall(pattern, html)
    # items是一个list,其中的每个内容都是一个元组
    # 将杂乱的信息提取并格式化，变成一个字典形式
    for item in items:
        yield {  # 构造一个字典
            'index': item[0],
            # 'image': item[1],
            'title': item[2],
            'actor': item[3].strip()[3:],  # 做一个切片，去掉“主演：”这3个字符
            'time': item[4].strip()[5:],  # 做一个切片，去掉“上映时间：”这5个字符
            'score': item[5] + item[6]  # 将小数点前后的数字拼接起来
        }


def write_to_file(content):
    with open('result.txt', 'a', encoding='utf-8') as f:
        # a表示模式是“追加”；采用utf-8编码可以正常写入汉字
        f.write(json.dumps(content, ensure_ascii=False) + '\n')  # 不允许写入ascii码
        # content是一个字典，我们需要转换成字符串形式，注意导入json库
        f.close()


def main(offset):
    url = 'http://maoyan.com/board/4?offset=' + str(offset)  # 把offset参数以字符串形式添加到url中
    html = get_one_page(url)
    for item in parse_one_page(html):  # item是一个生成器
        print(item)
        write_to_file(item)


if __name__ == '__main__':
    pool = Pool()  # 创建一个进程池
    pool.map(main, [i * 10 for i in range(10)])  # map方法创建进程（不同参数的main），并放到进程池中
