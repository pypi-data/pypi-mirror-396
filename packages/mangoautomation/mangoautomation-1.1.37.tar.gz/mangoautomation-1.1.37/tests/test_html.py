from bs4 import BeautifulSoup


def get_optimized_page_html(html_content) -> str:
    soup = BeautifulSoup(html_content, 'html.parser')

    # 配置化的清理规则
    cleanup_rules = {
        # 直接删除的标签
        'remove_tags': [
            'script', 'style', 'link', 'noscript', 'path',
            'svg', 'head', 'symbol', 'doubao-ai-csui', 'template'
        ],

        # 按class删除的元素
        'remove_by_class': [
            'watermark-box'
        ],

        # 按属性删除的元素
        'remove_by_attrs': {
            # 'tag_name': {'attr': 'value'}
        },

        # 清空内容但保留标签的条件
        'empty_content_conditions': [
            {
                'tag': 'textarea',
                'condition': lambda el: el.get('style') and 'display:none' in el.get('style')
            }
        ],

        # 要删除的属性
        'remove_attributes': [
            'style',
            'ssr'
        ],

        # 要删除的属性前缀（包含该前缀的属性都会被删除）
        'remove_attribute_prefixes': [
            'data-v-',
            'data-testid'
        ]
    }

    # 执行清理规则
    # 1. 删除指定标签
    for tag_name in cleanup_rules['remove_tags']:
        for element in soup.find_all(tag_name):
            element.decompose()

    # 2. 按class删除元素
    for class_name in cleanup_rules['remove_by_class']:
        for element in soup.find_all(class_=class_name):
            element.decompose()

    # 3. 按属性删除元素
    for tag_name, attrs in cleanup_rules['remove_by_attrs'].items():
        for element in soup.find_all(tag_name, attrs=attrs):
            element.decompose()

    # 4. 清空特定元素内容
    for condition_config in cleanup_rules['empty_content_conditions']:
        tag = condition_config['tag']
        condition_func = condition_config['condition']
        for element in soup.find_all(tag):
            if condition_func(element):
                element.string = ''

    # 5. 删除属性和属性前缀
    for element in soup.find_all():
        # 删除指定属性
        for attr in cleanup_rules['remove_attributes']:
            if element.has_attr(attr):
                del element[attr]

        # 删除包含特定前缀的属性
        for attr_prefix in cleanup_rules['remove_attribute_prefixes']:
            for attr in list(element.attrs.keys()):
                if attr.startswith(attr_prefix):
                    del element[attr]

    # 将BeautifulSoup对象转换为字符串
    html_content_str = str(soup)
    return html_content_str


with open('element.txt', 'r', encoding='utf-8') as f:
    file_content = f.read()
    optimize = get_optimized_page_html(file_content)
    print(f'原始的html大小：{len(file_content)}')
    print(f'优化之后的html大小：{len(optimize)}')
    with open('optimized.html', 'w', encoding='utf-8') as f:
        f.write(optimize)
