import json

# Data quality script

# defining file path:
# Relative path:
# file_path = "data/nasa-json-api/meteor_data.json"

# absolute_path:
file_path = r"/Users/gat-x131/Documents/GitHub/DE_Project/nasa-meteorite-pipeline/data/nasa-json-api/meteor_data.json"


# Null check:
def null_check(payload):
    ''' Simple null check -
    using for loop approach, it is much cleaner and we don't have to worry about iterating [i]

    using a while loop, this method goes through each element and the item inside that element.
    if conditions are met, the item is the result is appended into a list. Null checks each field.

    '''

    id_null_list = []

    ###### for loop approach: #####
    for record in payload:
        if record["id"] is None or record["id"].strip() == "":
            id_null_list.append(record["name"])


    ###### while loop approach: #####

    # i = 0
    # id_null_list = []

    # while i < len(payload):

        # test_list.append(payload[i]["name"]) # Brings i element, and the value for "name" key
        # test_list.append(payload[i]["recclass"]) # Brings i element, and the value for "reclass" key
        # test_list.append(payload[i]["id"]) # Brings i element, and the value for "id" key
        # if payload[i]["nametype"] is None or payload[i]["nametype"] == "":
        #     test_list.append(payload[i])


        # if payload[i]["id"] is None or payload[i]["id"].strip() == "":
        #     id_null_list.append(payload[i]["name"])
            # return f"No id found for meteor: {payload[i]["name"]}"
            # return f"No id found for meteor: {id_null_list}"

            # test_list.append(payload[i])

        # if payload[i]["recclass"].strip() is None or payload[i]["recclass"].strip() == "":
            # recclass_null_list.append(payload[i]["name"])
            # return f"No recclass founds for meteor: {payload[i]["name"]}"

        # i += 1
    # print(test_list)

    return f"No id found on meteors: {id_null_list}"


# Year check:
def year_check(payload):
    '''
    - This method checks if year key exist, if it doesn't,
    parses it and saves into a list

    - It also adds meteors that have year > 1800 into a separate list

    '''
    # print(type(payload))
    # Check if year key exist:


    no_year_list = []
    year_1800_2026 = []
    year_list = []

    for record in payload:
        if "year" not in record.keys():
            no_year_list.append(record['name'])
        elif int(record['year'][:4]) > 1800:
            year_1800_2026.append(record['name'])
        else:
            year_list.append(record['year'])

    # for years in year_list:
    #     if int(years[:4]) > 1800:
    #         year_1800_2026.append(years[:4])
            # print(years[:4])


    return f"Meteors without years: {no_year_list}\n\n Meteors recorded from >1800 \n\n{year_1800_2026}\n\n"



# Using 'with open' to use all the methods above, this will go into a main function later

with open(file_path, "r") as f:
    data = json.load(f)
    # print(data[0]["year"])

    # print(data[0]["id"]) # Accessing the list first [] then dictionary keys ["keys"]
    # print(type(data))

    # method calls

    # print(null_check(data))
    print(year_check(data))






# # Mass check:
# def mass_check(payload):
#     pass

# # Coordinate check:
# def coord_check(payload):
#     pass

# # Failed files to qurantine:
# def quarantine_check(payload):




