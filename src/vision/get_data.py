import json 

def get_data():
    with open(r"..\..\data\boards.json") as f:
        data = json.load(f)
        res = {}
        for el in data:
            screenshots_src = fr"../../data/RealTime/{el['num']}/RealTime"
            content_data_src = []
            for id_content in el['content']['activeContent']:
                content_data_src.append(fr"../../data/AsiuddContent/{id_content['id']}/RealTime")
            res[screenshots_src] = content_data_src

        return res 

if __name__ == "__main__":
    data = get_data()