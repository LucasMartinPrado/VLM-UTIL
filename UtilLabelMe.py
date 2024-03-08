import json, os
from PIL import Image, ImageDraw
import click
import labelme2coco

class UtilLabelMe:

    DEFAULT_PATH = os.path.join(os.path.curdir, "All-Dataset")
    def format_data(self):
        """
        Transforms the data from the custom JSON format (obtained from the original XML files) to a LabelMe compatible
        format.
        The JSON files in the old format are overwritten with the new data.
        """

        path = self.DEFAULT_PATH
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

    def check_labels(self, labelname=None, path=DEFAULT_PATH):
        """
        Checks all datasets available and obtains a dictionary with all label names and frequency of said labels.
        :return dict: keys:labelname, value: frequency
        """

        label_counter = {}
        names=[]
        with click.progressbar(os.listdir(path)) as listdir:
            for dataset in listdir:
                dataset_path = os.path.join(path, dataset)
                # print(os.path.isdir(dataset_path))
                if os.path.isdir(dataset_path):
                    labels_path = os.path.join(path, dataset, "Annotations")
                    for filename in os.listdir(labels_path):
                        file_path = os.path.join(labels_path, filename)
                        if os.path.isfile(file_path) and ('json') in file_path and not ('coco') in file_path:
                            # print(filename)
                            json_data = self.__read_data(file_path)
                            for label in json_data["shapes"]:
                                if label["label"].lower() in label_counter:
                                    # incerementing the count by 1
                                    label_counter[label["label"].lower()] += 1
                                else:
                                    # setting the count to 1
                                    label_counter[label["label"].lower()] = 1
                                if labelname is not None:
                                    if label["label"].lower() == labelname:
                                        if filename not in names:
                                            names.append(filename)
            return label_counter, names
    def search_label(self, labelname, path=DEFAULT_PATH):
        """
        Checks all datasets available for a specific label and finds: the names of the images that cointain it,
        the amount of images that contain it and the amount of labels found.
        :param labelname: the name of the label to check
        :param path: Path to the 'All-dataset' folder
        :return list[str]: list of filenames of images that contain the label.
        :return int: amount of times that the label appears in all datasets
        """
        label_counter, names = self.check_labels(labelname,path)
        if labelname in label_counter.keys():
             return names, label_counter[labelname]
        else:
            return names, 0

    def image_processing(self, dataset, name, path=DEFAULT_PATH, labeling=True):
        """
        Opens a .jpg image from the specified dataset and draws the bounding boxes of each label.
        :param dataset: name of the dataset (folder name) the image is from
        :param name: filename of the image
        :param path: Path to 'All-Dataset' folder
        :param labeling: Enables the bounding boxes of each label.
        """
        path = os.path.join(path, dataset)
        image_path = os.path.join(path, "JPEGImages") + '\\' + name + '.jpg'
        data_path = os.path.join(path, "Annotations") + '\\' + name + '.json'
        img = Image.open(image_path)
        if labeling:
            imgRec = ImageDraw.Draw(img)
            data = self.__read_data(data_path)
            for label in data["shapes"]:
                bbox = self.__arrange_points(label["points"])
                imgRec.rectangle(bbox, outline="red")
                imgRec.text((float(bbox[0]), float(bbox[1] - 10)), label["label"], fill="red")
        img.show()

    def convert(self, dataset, path=DEFAULT_PATH):
        path = os.path.join(os.path.curdir, "Dataset-STest")

        # set directory that contains labelme annotations and image files
        # labelme_folder = "tests/data/labelme_annot"
        labelme_folder = os.path.join(path, dataset, "Annotations")

        # set export dir
        export_dir = labelme_folder = os.path.join(path, dataset, "Tests")

        # set train split rate
        train_split_rate = 0.85

        # convert labelme annotations to coco
        labelme2coco.convert(labelme_folder, export_dir, train_split_rate)

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
        (obtained from the original XML files). Shuffles the x and y coordinates so x0<x1 and y0<y1
        :param t_bbox: the transformed bounding box.
        :return list[float]
        """
        return [t_bbox[0][0], t_bbox[0][1], t_bbox[1][0], t_bbox[1][1]]

    def __arrange_points(self, points):
        """
        Private method to transform the bounding box from the labelMe compatible format to the custom JSON format
        (obtained from the original XML files). Shuffles the x and y coordinates so x0<x1 and y0<y1
        :param points: the points list from the LabelMe compatible format.
        :return list[float]
        """
        p1, p2 = points
        x0, x1 = [p1[0], p2[0]] if p1[0] < p2[0] else [p2[0], p1[0]]
        y0, y1 = [p1[1], p2[1]] if p1[1] < p2[1] else [p2[1], p1[1]]
        return [x0, y0, x1, y1]

    def alter_label(self, targetLabel, newName, path=DEFAULT_PATH):
        """
        Replaces the name of a label in all instances of the dataset.
       :param targetLabel: original name of the label to replace
       :param newName: name to replace the label with
       :param path: Path to 'All-Dataset' folder
       """
        for dataset in os.listdir(path):
            dataset_path = os.path.join(path, dataset)
            if os.path.isdir(dataset_path):
                labels_path = os.path.join(path, dataset, "Annotations")
                for filename in os.listdir(labels_path):
                    file_path = os.path.join(labels_path, filename)
                    if os.path.isfile(file_path) and ('json') in file_path and not ('coco') in file_path:
                        json_data = self.__read_data(file_path)
                        ######MODIFIES########
                        for object in json_data["shapes"]:
                            if object["label"].lower() in [targetLabel]:
                                object["label"] = newName
                        ####################
                        altered_file = open(file_path, 'w', encoding='utf-8')
                        json.dump(json_data, altered_file, ensure_ascii=False, indent=4)
                        altered_file.close()