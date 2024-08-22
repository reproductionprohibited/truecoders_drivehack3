from pathlib import Path
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

    def get_data(self, src_to_data):
        count = 0
        with open(fr"{src_to_data}/BoardsFinal.json") as f:
            data = json.load(f)
            res = {}
            for el in data:
                size = el['Size']
                num = el['Num']
                screenshots_src = fr"{src_to_data}/RealTime/{num}/RealTime"
                if os.path.isdir(screenshots_src):
                    content_data_src = []
                    for id_content in el['Content']['activeContent']:
                        path_to_content = fr"{src_to_data}/AsiuddContent/{id_content['id']}/"
                        if os.path.isdir(path_to_content):
                            p = Path(path_to_content)
                            for content_path in p.rglob("*"):
                                content_filename = str(content_path).split('/')[-1]
                                if content_filename.split('.')[0][-3:] == size:
                                    content_data_src.append(str(content_path))

                    res[str(screenshots_src)] = [content_data_src, num]
                    count += 1 
                    if count == 2:
                        break

        return res 
    
    def get_needed_texts(self, path_to_img):
        result = self.reader.readtext(path_to_img, batch_size=64)
        text = ' '.join([result[i][-2] for i in range(len(result))])
        # print(text)
        return text 


    def preprocess(self, img):
        norm_img = np.zeros((img.shape[0], img.shape[1]))
        img = cv2.normalize(img, norm_img, 0, 255, cv2.NORM_MINMAX) # normalizing

        img = img[:img.shape[0] - 20,] # cropping

        img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 15) # removing noise

        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # get_grayscale
        
        return img

    def run_processing(self, data):
        result = []
        for board_imgs, true_content in data.items():
            texts = []
            count_mismatch = 0
            num = true_content[1]
            for img_content in true_content[0]: 
                texts.append(self.get_needed_texts(img_content))
            path_to_screens = Path(board_imgs)
            current = []
            for board_img in path_to_screens.rglob("*"):
                img = self.preprocess(cv2.imread(board_img))
                board_text = self.reader.readtext(img)
                board_text = ' '.join([board_text[i][-2] for i in range(len(board_text))])
                flag = False 
                for text in texts:
                    if fuzz.ratio(text, board_text) > 70:
                        flag = True 
                        break
                if not flag:
                    count_mismatch += 1
                    current.append(board_img)
            result.append({
                'num':num,
                'display': current,
                'mismatch_percentage': count_mismatch / len(board_imgs)
                })
        return result
            


if __name__ == "__main__":
    start = time.time()
    pr = Preprocesser()
    data = pr.get_data('../../data/')
    # print(len(data))
    
    res = pr.run_processing(data)
    for el in res:
        print(el)
    print(time.time() - start)