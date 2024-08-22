from pathlib import Path
import os 
import json 

def get_data(src_to_data):
    with open(fr"{src_to_data}/BoardsFinal.json") as f:
        data = json.load(f)
        res = {}
        for el in data:
            screenshots_src = fr"{src_to_data}/RealTime/{el['Num']}/RealTime"
            if os.path.isdir(screenshots_src):
                path_screens = Path(fr"{src_to_data}/RealTime/{el['Num']}/RealTime")
                size = el['Size']
                for screen_path in path_screens.rglob('*'):
                    content_data_src = []
                    for id_content in el['Content']['activeContent']:
                        if os.path.isdir(fr"{src_to_data}data/AsiuddContent/{id_content['id']}/"):
                            p = Path(fr"{src_to_data}data/AsiuddContent/{id_content['id']}/")
                            for content_path in p.rglob("*"):
                                content_filename = str(content_path).split('/')[-1]
                                if content_filename.split('.')[0][-3:] == size:
                                    content_data_src.append(str(content_path))
                    res[str(screen_path)] = content_data_src

        return res 

if __name__ == "__main__":
    data = get_data('../../data/')
    print(data)
    