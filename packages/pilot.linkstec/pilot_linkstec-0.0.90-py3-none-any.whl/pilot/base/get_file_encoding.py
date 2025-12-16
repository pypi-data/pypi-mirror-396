import chardet

def get_file_encoding(filename):
    # 读取文件，返回文件编码
    with open(filename, 'rb') as f1:
        data = f1.read()
        result = chardet.detect(data)
        encoding = result['encoding']

        if encoding and encoding.lower() != 'utf-8':
            encoding = 'sjis'
        elif not encoding:
            encoding = 'sjis'
    return encoding