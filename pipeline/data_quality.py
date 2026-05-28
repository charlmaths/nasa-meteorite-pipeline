import json

# Data quality script

# defining file path:
# Relative path:
# file_path = "data/nasa-json-api/meteor_data.json"

# absolute_path:
file_path = r"/Users/gat-x131/Documents/GitHub/DE_Project/nasa-meteorite-pipeline/data/nasa-json-api/meteor_data.json"

# Parser:
def json_parser(payload):
    '''Parser function:
    The idea is to parse the json file first'''
    pl = payload
    pl_list = []
    pl_dict = {}
    for item in pl:
        pl_list.append(item)
        # pl_dict[item]

    # print(pl_list)
    print(pl_list[0])
    # print(pl_dict.items())


# Using with open to use all the methods above, this will go into a main function later
with open(file_path, "r") as f:
    data = json.load(f)
    # print(type(data))
    json_parser(data)



with open(file_path) as file:
    json_parser(json.load(file))


# json_parser(file_path)

# Null check:


# Year check:


# Mass check:


# Coordinate check:


# Failed files to qurantine:

