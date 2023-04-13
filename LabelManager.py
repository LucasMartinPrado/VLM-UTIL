import json, os, math, xmltodict, shutil

class LabelManager:

    def __bounds(self, boundingbox):
        """
        Private method to reformat the bounding boxes from the XML files to the custom JSON format.
        :param boundingbox: the bounding box from the xml files.
        :return list[int]
        """
        bounds = [math.floor(float(boundingbox['xmin'])), math.floor(float(boundingbox['ymin'])), math.floor(float(boundingbox['xmax'])), math.floor(float(boundingbox['ymax']))]
        return bounds


    def __area(self, boundingbox):
        """
        Private method to calculate area of the bounding box.
        :param boundingbox: the bounding box.
        :return int
        """
        area = math.floor((float(boundingbox["xmax"]) - float(boundingbox["xmin"])) * (float(boundingbox["ymax"]) - float(boundingbox["ymin"])))
        return area


    def __image_name(self, filename):
        """
        Private method to split the name of the file
        :param filename: name of the file
        """
        name = filename.split(".")[0]
        return name + '.jpg'


    def xml_to_customJSON(self):
        """
        Obtains the data from the XML files and transforms it into a new custom JSON format.
        New .json files are generated and saved in the same folder of the original XML files.
        """
        path = os.path.join(os.path.curdir, "All-Dataset")
        print(path)
        for dataset in os.listdir(path):
            dataset_path = os.path.join(path, dataset)
            print(os.path.isdir(dataset_path))
            if os.path.isdir(dataset_path):
                dataset_path = os.path.join(path, dataset, "Annotations")
                print(dataset_path)
                for filename in os.listdir(dataset_path):
                    print(filename)
                    file_path = os.path.join(dataset_path, filename)
                    print(file_path)
                    if os.path.isfile(file_path) and ('xml') in file_path:
                        with open(file_path, 'r') as f:
                            data = f.read()
                            parsed_dictionary = xmltodict.parse(data)['annotation']
                            object_list = parsed_dictionary['object']
                            labels = []
                            for obj in object_list:
                                component = {
                                    "category": obj["name"],
                                    "bbox": self.__bounds(obj["bndbox"]),
                                    "area": self.__area(obj["bndbox"])
                                }
                                print(component)
                                labels.append(component)
                            refined_data = {
                                "filename": self.__image_name(filename),
                                "width": parsed_dictionary['size']['width'],
                                "height": parsed_dictionary['size']['height'],
                                "labels": labels}
                            print(refined_data)
                            print(file_path)
                            json_path = '.' + file_path.split(".")[1] + ".json"
                            refined_file = open(json_path, 'w', encoding='utf-8')
                            json.dump(refined_data, refined_file, ensure_ascii=False, indent=4)
                            refined_file.close()

    def alter_labels(self):
        """
        Changes the .json files in order to represent the new criteria of labels.
        Old files are overwritten with the new data.
        """
        path = os.path.join(os.path.curdir, "All-Dataset")
        print(path)
        for dataset in os.listdir(path):
            dataset_path = os.path.join(path, dataset)
            print(os.path.isdir(dataset_path))
            if os.path.isdir(dataset_path):
                labels_path = os.path.join(path, dataset, "Annotations")
                for filename in os.listdir(labels_path):
                    file_path = os.path.join(labels_path, filename)
                    if os.path.isfile(file_path) and ('json') in file_path and not ('coco') in file_path:
                        print(filename)
                        json_data = self.__read_data(file_path)
                        ######MODIFIES########
                        for object in json_data["labels"]:
                            if object["category"].lower() in ['card', 'modal', 'drawer']:
                                object["category"] = 'Panel'
                            if object["category"].lower() in ['inputfield', 'edittext']:
                                object["category"] = 'Input'
                            if object["category"].lower() in ['bottom_navigation', 'remember', 'slidingmenu', 'popupwindow']:
                                json_data["labels"].remove(object)
                        ####################
                        altered_file = open(file_path, 'w', encoding='utf-8')
                        json.dump(json_data, altered_file, ensure_ascii=False, indent=4)
                        altered_file.close()


    def __read_data(self, filename):
        """
        Private method to open JSON files and load them.
        :param filename: Name of the file
        :return dictionary
        """
        FILE = open(filename, encoding="utf-8")
        data = json.load(FILE)
        FILE.close()
        return data

