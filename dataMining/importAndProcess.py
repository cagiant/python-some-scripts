import csv

transaction_status_text = "交易状态"
transaction_time_text = "交易时间"
transaction_type_text = "交易类型"
transaction_name_text = "支付方式"
transaction_to_text = "交易对方"
transaction_desc_text = "商品"
transaction_total_text = "金额(元)"
input_type_text = "收/支"


def get_transaction_classification(transaction_note):
    life_keywords = ["燃气费", "水费", "箭牌洗手盆", "沙宣护发素", "佳帮手", "宝家洁", "健身", "SafeX快递刀",
                     "润本蚊香液", "收钱码收款",
                     "抗原检测", "华为手环", "短袜", "邮费", "中央空调", "乐高超级英雄蜘蛛侠人偶", "丰巢", "二维码收款", "手机充值",
                     "泳衣女", "携程", "物种起园", "党徽", "洗菜盆", "气垫梳", "台历", "手脱皮", "华润万家",
                     "唯品会", "快团团", "沃玛超市", "员工福利商品", "成为简·奥斯汀", "考拉海购", "抖音小店",
                     "开元森泊", "银泰西选", "安吉中南", "电水壶", "谜尚红气垫", "君品烫染", "拼多多", "杰士邦", "雪欣商店",
                     "鸿佳超市", "小天才电话手表", "手机壳"]
    eat_keywords = ["餐饮", "LAWSON", "FamilyMart", "饿了么", "麦当劳", "洪兴烧腊", "稻状元", "兰州手工牛肉面",
                    "旺昌门", "冷饮经营部",
                    '福满家', "群收款", "早餐", "商户消费-秘府", "薛记食品", "雅苑综合超市",
                    "上铁互联信息技术江苏有限公司", "泸溪河", "杭州十足", "留夫鸭", "一鸣",
                    "水果店", "食品店", "钱大妈", "知味观", "可莎蜜兒", "一日三餐", "味阔家", "点心", "桃酥",
                    "生煎", "冰糖葫芦", "唐春花", "烧仙草", "陈何梅", "陈钰", "鲍师傅", "肯德基", "LAWSON",
                    "饿了么", "军儿面馆", "贪吃丛林"]
    classification_dict = {
        "保险费": ["保险"],
        "盒马": ["盒马"],
        "山姆": ["山姆会员", "山姆自助购"],
        "亲情卡": ["亲情卡", "亲属卡"],
        "皮皮": ["猫粮", "猫砂"],
        "娱乐": ["三国杀", "一元解锁"],
        "交通费": ["停车", "打车", "加油", "车位租金", "骑行卡", "滴滴出行", "地铁", "公共交通", "中国石化", "公交",
                 "杭州客运", "车位", "12306", "上铁实业", "杭州通", "补票"],
        "技能提升": ["App Store & Apple Music", "Github Copilot", "java", "极客时间", "midjourney", "剪ying映", "AA全球代发", "浙江省财政厅-统一公共支付平台3300010533300014515RRWCUU2301", "培训课程"],
        "东新园": ["东新园", "东新苑"],
        "医疗": ["医疗"],
        "日常吃喝": eat_keywords,
        "宝宝": ["世喜", "宝宝", "女孩玩具", "婴儿", "孩子王", "贝迪游乐", "cutezoo", "美团平台商户", "京东商城平台商户",
                 "宝贝王"],
        "红包": ["支付宝红包", "微信转账", "转账-汤圆妈妈", "群红包", "微信红包"],
        "生活": life_keywords,
    }

    for classification, keywords in classification_dict.items():
        if any(keyword in transaction_note for keyword in keywords):
            return classification
    return ""


def ignore(row):
    # 金额为 0 的不统计
    transaction_total = float(row[transaction_total_text].replace("¥", ""))
    if transaction_total == 0:
        return True
    transaction_note = f"{row[transaction_type_text]}-{row[transaction_to_text]}-{row[transaction_desc_text]}"
    ignored_keywords = ["交通银行信用卡还款", "转入零钱通-来自零钱", "转账-俊俊哥", "投资理财-广发基金管理有限公司"]
    # 包含忽略关键词的不统计
    for keyword in ignored_keywords:
        if keyword in transaction_note:
            return True

    return False


input_file = 'merged.csv'
output_file = '/Users/cagiant/Desktop/processed.csv'
transaction_success_set = {
    "等待确认收货",
    "交易成功",
    "已转账",
    "支付成功",
    "对方已收钱",
    "已存入零钱",
}

with open(input_file, 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    data_rows = list(reader)

# 打印交易状态集合
transaction_status_set = {row[transaction_status_text] for row in data_rows}
print(transaction_status_set)

transaction_name_set = {row[transaction_name_text] for row in data_rows}
print(transaction_name_set)
is_cl = False
gkq_transaction_name_set = set()
for transaction_name in transaction_name_set:
    if "郭凯强" in transaction_name:
        is_cl = True
    if "亲属" in transaction_name or "亲情" in transaction_name:
        gkq_transaction_name_set.add(transaction_name)

print(is_cl)
print(gkq_transaction_name_set)

# 处理交易状态为"等待确认收货"和"交易成功"的数据
filtered_rows = [row for row in data_rows if row[transaction_status_text] in transaction_success_set]
if is_cl:
    filtered_rows = [row for row in filtered_rows if row[transaction_name_text] in gkq_transaction_name_set]

# 按照交易时间正序排列
sorted_rows = sorted(filtered_rows, key=lambda x: x[transaction_time_text])

new_header_row = ["备注", "日期", "金额", "收支", "分类"]
new_data_row = []

for row in sorted_rows:
    if ignore(row):
        continue

    new_row = []
    transaction_note = f"{row[transaction_type_text]}-{row[transaction_to_text]}-{row[transaction_desc_text]}"
    transaction_classfication = get_transaction_classification(transaction_note)
    skip = False
    for header in new_header_row:
        if header == "备注":
            new_row.append(transaction_note)
        elif header == "日期":
            new_row.append(row[transaction_time_text])
        elif header == "金额":
            new_row.append(row[transaction_total_text])
        elif header == "收支":
            if row[input_type_text] not in {"收入", "支出"} and is_cl:
                row[input_type_text] = "支出"
            elif row[input_type_text] not in {"收入", "支出"}:
                skip = True
            new_row.append(row[input_type_text])
        elif header == "分类":
            new_row.append(transaction_classfication)
    if skip:
        continue
    new_data_row.append(new_row)

with open(output_file, 'w', newline='', encoding='utf-8') as out_file:
    writer = csv.writer(out_file)
    writer.writerow(new_header_row)
    writer.writerows(new_data_row)

new_sorted_rows = sorted(new_data_row, key=lambda x: x[4])
for row in new_sorted_rows:
    print(row)

print("processd CSV saved as {output_file}.")
