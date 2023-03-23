import json, os
from PIL import Image, ImageDraw

class UtilLabelMe:

    def format_data(self):
        """
        Transforms the data from the custom JSON format (obtained from the original XML files) to a LabelMe compatible
        format.
        The JSON files in the old format are overwritten with the new data.
        """

        path = os.path.join(os.path.curdir, "All-Dataset")
        #print(path)
        for dataset in os.listdir(path):
            dataset_path = os.path.join(path, dataset)
            #print(os.path.isdir(dataset_path))
            if os.path.isdir(dataset_path):
                dataset_path = os.path.join(path, dataset, "Annotations")
                #print(dataset_path)
                for filename in os.listdir(dataset_path):
                    #print(filename)
                    file_path = os.path.join(dataset_path, filename)
                    #print(file_path)
                    if os.path.isfile(file_path) and ('json') in file_path and not ('coco') in file_path:
                        #print(filename)
                        json_data = self.__read_data(file_path)
                        formatted_data = {"version": "5.0.1",
                                        "flags": {},
                                        "shapes": [],
                                        "imagePath": json_data["filename"],
                                        "imageData": None,
                                        "imageHeight": int(json_data["height"]),
                                        "imageWidth": int(json_data["width"])
                        }
                        for object in json_data["labels"]:
                            #print(json_data)
                            #print(file_path)
                            label = {
                                  "label": object["category"].lower(),
                                  "points": self.transform_points(object["bbox"]),
                                  "group_id": None,
                                  "shape_type": "rectangle",
                                  "flags": {}
                                }
                            formatted_data["shapes"].append(label)
                        altered_file = open(file_path, 'w', encoding='utf-8')
                        json.dump(formatted_data, altered_file, ensure_ascii=False, indent=4)
                        altered_file.close()


    def check_labels(self, labelname):
        """
        Checks all datasets available for a specific label and prints: the names of the images that cointain it,
        the amount of images that contain it and the amount of labels found.
        :param labelname: the name of the label to check
        """

        path = os.path.join(os.path.curdir, "All-Dataset")
        #print(path)
        label_counter = {}
        names = []
        for dataset in os.listdir(path):
            dataset_path = os.path.join(path, dataset)
            #print(os.path.isdir(dataset_path))
            if os.path.isdir(dataset_path):
                labels_path = os.path.join(path, dataset, "Annotations")
                for filename in os.listdir(labels_path):
                    file_path = os.path.join(labels_path, filename)
                    if os.path.isfile(file_path) and ('json') in file_path and not ('coco') in file_path:
                        #print(filename)
                        json_data = self.__read_data(file_path)
                        for label in json_data["shapes"]:
                            if label["label"].lower() in label_counter:
                                # incerementing the count by 1
                                label_counter[label["label"].lower()] += 1
                            else:
                                # setting the count to 1
                                label_counter[label["label"].lower()] = 1
                            if label["label"].lower() == labelname:
                                if filename not in names:
                                    names.append(filename)
        print('------')
        for key, value in label_counter.items():
            print(f"{key}: {value}")
        print("List of images:")
        print(names)
        print('Images: ' + str(len(names)))
        print('Labels: ' + str(label_counter[labelname]))

    def image_processing(self, dataset, name):
        """
        Opens a .jpg image from the specified dataset and draws the bounding boxes of each label.
        :param dataset: name of the dataset (folder name) the image is from
        :param name: filename of the image
        """
        path = os.path.join(os.path.join(os.path.curdir, "All-Dataset"), dataset)
        image_path = os.path.join(path, "JPEGImages") + '\\' + name + '.jpg'
        data_path = os.path.join(path, "Annotations") + '\\' + name + '.json'
        img = Image.open(image_path)
        imgRec = ImageDraw.Draw(img)
        data = self.__read_data(data_path)
        for label in data["shapes"]:
            bbox = self.__detransform_points(label["points"])
            imgRec.rectangle(bbox, outline="red")
            imgRec.text((float(bbox[0]), float(bbox[1] - 10)), label["label"], fill="red")
        img.show()


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

    def __transform_points(self, bbox):
        """
        Private method to transform the bounding box from the custom JSON format (obtained from the original XML files)
        to a LabelMe compatible format.
        :param bbox: the bounding box from the custom format
        :return list[list[float]]
        """
        return [[float(bbox[0]), float(bbox[1])], [float(bbox[2]), float(bbox[3])]]

    def __detransform_points(self, t_bbox):
        """
        Private method to transform the bounding box from the labelMe compatible format to the custom JSON format
        (obtained from the original XML files)
        :param t_bbox: the transformed bounding box.
        :return list[float]
        """
        return [t_bbox[0][0], t_bbox[0][1], t_bbox[1][0], t_bbox[1][1]]