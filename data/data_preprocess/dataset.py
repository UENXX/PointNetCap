import os
from case import *

pattern_1 = r'^\*(\d+)+\s(.*)'
net_name = []
net_numbers = []

with open("fs_1.txt", 'r', encoding='utf-8') as file:
    for line in file:
        for match in re.finditer(pattern_1, line):
            num = match.group(1)  
            name = match.group(2)  
            net_numbers.append(num)
            net_name.append(name)

pattern_2 = r'\*D_NET \*\d+ .*?(\d+(?:\.\d+)?)(?=\s*\*END)'
net_capacitance = []

with open("fs_1.txt", 'r', encoding='utf-8') as file:
    content = file.read()
    blocks = re.finditer(pattern_2, content, re.DOTALL)
    for block in blocks:
        net_cap = block.group(1)  
        net_capacitance.append(net_cap)

file_path = "case1.txt"
file_content = read_txt_file(file_path)
pattern = r'- (.*?)\n;'
matches = re.findall(pattern, file_content, re.DOTALL)
all_name = []
all_value = []
for section in matches:
    pattern1 = r'(.*?)\n\n\t'
    name = re.findall(pattern1, section, re.MULTILINE)
    value = []
    pattern2 = r'\+\s*(.*?)$'
    rew = re.findall(pattern2, section, re.DOTALL)
    split_items = rew[0].split('\n\t')
    for data in split_items:
        result = process(data)
        value.append(result)
    all_value.append(value)    
    all_name.append(name)     

folder_name = "dataset"
current_directory = os.getcwd()
target_directory = os.path.join(current_directory, folder_name)

if not os.path.exists(target_directory):
    os.makedirs(target_directory)

for cap, name in zip(net_capacitance, net_name):
    file_name = '{capacitance}.txt'.format(capacitance=cap)
    file_path = os.path.join(target_directory, file_name)
    for sublist in all_name:
        for i in sublist:
            if i == name:
                with open(file_path, "w", encoding="utf-8") as file:
                    # file.write("The name of this net is {i_name}\n".format(i_name=name))
                    index = all_name.index(sublist)
                    content = all_value[index]
                    for row in content:
                        for item in row:
                            file.write(str(item) + ',')
                        file.write('\n')