import csv
import os
import chardet
import codecs


def convert_to_utf8(origin_file, original_encoding):
    if "GB2312" in original_encoding:
        original_encoding = 'gbk'
    # 目标CSV文件路径和编码
    target_file = origin_file
    target_encoding = 'utf-8'

    data = []
    data_row_matched = False
    # 打开原始CSV文件并指定编码
    with codecs.open(origin_file, 'r', encoding=original_encoding) as file:
        # 使用csv.reader读取原始文件
        reader = csv.reader(file)
        # 读取原始文件中的数据
        for row in reader:
            cleaned_row = [field.strip() for field in row]
            if data_row_matched:
                data.append(cleaned_row)
            elif any(row) and row[0].startswith('交易时间'):  # 判断以'交易时间'开头的行作为表头
                data_row_matched = True
                data.append(cleaned_row)

    # 打开目标CSV文件并指定编码
    with codecs.open(target_file, 'w', encoding=target_encoding) as file:
        # 使用csv.writer写入目标文件
        writer = csv.writer(file)
        # 写入转换后的数据到目标文件
        writer.writerows(data)


def get_row(head, row):
    head_alias_dic = {
        "交易类型": ["交易分类"],
        "商品": ["商品说明"],
        "金额(元)": ["金额"],
        "支付方式": ["收/付款方式"],
        "交易状态": ["当前状态"],
        "交易单号": ["交易订单号"],
        "商户单号": ["商家订单号"],
    }
    if head in row:
        return row[head]

    if head in head_alias_dic:
        for alias in head_alias_dic[head]:
            return get_row(alias, row)

    return ""


# 读取所有 csv 文件
csv_files = [file for file in os.listdir('.') if
             file.endswith('.csv') and "processed" not in file and "merged" not in file]

for file in csv_files:
    with open(file, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        convert_to_utf8(file, encoding)

# 合并为一个 csv 文件
output_file = 'merged.csv'
header_row = ['交易时间', '交易类型', '交易对方', '商品', '收/支', '金额(元)', '支付方式', '交易状态', '交易单号',
              '商户单号', '备注']
with open(output_file, 'w', newline='', encoding='utf-8') as out_file:
    writer = csv.writer(out_file)
    writer.writerow(header_row)
    # 遍历所有 csv 文件
    for file in csv_files:
        with open(file, 'r', encoding='utf-8') as in_file:
            reader = csv.DictReader(in_file)
            for row in reader:
                row_processed = []
                for head in header_row:
                    row_processed.append(get_row(head, row))
                writer.writerow(row_processed)

print(f"Merged CSV file saved as {output_file}")
