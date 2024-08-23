from typing import Dict, List
from pathlib import Path
from pprint import pprint
import os 
import json
import time

import numpy as np
from fuzzywuzzy import fuzz
import easyocr 
import cv2 


class Preprocesser:
    def __init__(self) -> None:
        self.reader = easyocr.Reader(['ru'], gpu=False)

    def get_data(self, filepath: str = ''):
        count = 0
        with open('/'.join([filepath, 'BoardsFinal.json'])) as f:
            data = json.load(f)
            res = {}
            pprint(data, stream=open('debug.txt', mode='w'))
            for element in data:
                size = element['Size']
                num = element['Num']
                screenshots_src = fr"{filepath}/RealTime/{num}/RealTime"
                if os.path.isdir(screenshots_src):
                    content_data_src = []
                    for id_content in element['Content']['activeContent']:
                        path_to_content = fr"{filepath}/AsiuddContent/{id_content['id']}/"
                        if os.path.isdir(path_to_content):
                            p = Path(path_to_content)
                            for content_path in p.rglob("*"):
                                content_filename = str(content_path).split('/')[-1]
                                if content_filename.split('.')[0][-3:] == size:
                                    content_data_src.append(str(content_path))

                    res[str(screenshots_src)] = [content_data_src, num]
                    count += 1 
                    if count == 15:
                        break

        return res 
    
    def get_needed_texts(self, path_to_img):
        result = self.reader.readtext(path_to_img, batch_size=128)
        text = ' '.join([result[i][-2] for i in range(len(result))])
        return text 


    def preprocess(self, img):
        norm_img = np.zeros((img.shape[0], img.shape[1]))
        img = cv2.normalize(img, norm_img, 0, 255, cv2.NORM_MINMAX)
        img = img[20:img.shape[0] - 20,]
        img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 15)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img

    def run_processing(self, data):
        alf = 'йцукенгшщзфывапролдячсмитьбю'
        result = []
        for board_imgs, true_content in data.items():
            texts = []
            num = true_content[1]
            # if num != '10':
            #     continue
            for img_content in true_content[0]: 
                texts.append(self.get_needed_texts(img_content))
            path_to_screens = Path(board_imgs)
            current = []
            count = 0
            for board_img in path_to_screens.rglob("*"):
                count += 1
                img = self.preprocess(cv2.imread(board_img))
                board_text = self.reader.readtext(img)
                board_text = ' '.join([board_text[i][-2] for i in range(len(board_text))]).lower()
                new_board_text = ''
                for sym in board_text:
                    if sym in alf or sym == ' ':
                        new_board_text += sym
                flag = False 
                for text in texts:
                    if fuzz.ratio(text.lower().strip(), new_board_text.strip()) >= 48:
                        flag = True 
                        break
                    # print(f'{new_board_text.lower().strip()};;;{text.lower().strip()};;;{fuzz.ratio(text.lower().strip(), board_text.lower().strip())}')

                if not flag:
                    current.append('/'.join(str(board_img).split('/')[1:]))
            result.append({
                'num': num,
                'display': current,
                'mismatch_percentage': round(len(current) / count, 2),
                'content':true_content[0]
                })
            print(len(result))
        return result


def run_image_processing(filepath: str) -> List[Dict]:
    pr = Preprocesser()
    data = pr.get_data('/'.join([filepath, 'hackaton']))
    res = pr.run_processing(data)
    return res


if __name__ == "__main__":
    # print()
    # print(run_image_processing('../media/1724336905174315'))
    # start = time.time()
    pr = Preprocesser()
    data = pr.get_data('../media/1724336905174315/hackaton')
    
    res = pr.run_processing(data)
    for el in res:
        print(el)
