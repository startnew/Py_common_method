import requests

host = "http://your_url/{}"
token = "token your_token"
headers = {"Authorization": token, "Content-Type": "application/json"}
import os
import json
from tqdm import tqdm
from pprint import pprint


class labelStudioApi():
    def __init__(self, host):
        self.host = host
        self.project_url = host.format("api/projects/")
        self.import_url = host.format("api/projects/{}/import")
        self.del_task_url = host.format("api/tasks/{}/")
        self.get_task_url = host.format("api/tasks/{}/")
        self.list_project_tasks_url = host.format("api/projects/{}/tasks/")
        self.create_ann_url = host.format("api/tasks/{}/annotations")
        self.update_ann_url = host.format("api/annotations/{}/")
        self.update_predict_url = host.format("api/predictions/{}/")

    def get_project(self):
        print(self.project_url)
        result = requests.get(self.project_url, headers=headers)
        return json.loads(result.text)

    def del_tasks(self, task_id):
        """删除标注任务:param"""
        print(self.del_task_url.format(task_id))
        result = requests.delete(self.del_task_url.format(task_id), headers=headers)
        print(result.text)

    def get_task(self, task_id):
        print(self.get_task_url.format(task_id))
        result = requests.get(self.get_task_url.format(task_id), headers=headers)
        return json.loads(result.text)

    def get_list_project_tasks(self, project_id, page=1):
        """
        获取 指定 项目的 所有标注任务
        :param"""
        url = self.list_project_tasks_url.format(project_id) + "?page={}".format(page)
        print(url)
        result = requests.get(url,
                              headers=headers, )
        return json.loads(result.text)

    def update_task(self, task_id, data):
        url = self.get_task_url.format(task_id)
        result = requests.patch(url, data=data, headers=headers)
        return json.loads(result.text)

    def import_data(self, file_dir, project_id):
        """导入数据:param"""
        files = [os.path.join(file_dir, x) for x in os.listdir(file_dir)]
        for file in files:
            data = {
                'file_upload': (os.path.basename(file), open(file, 'rb')),
                'Content-Type': 'image/jpeg',
                # 'Content-Length': l
            }
            # files = {'image': open(file, 'rb')}
            print(self.import_url.format(project_id))
            r = requests.post(self.import_url.format(project_id), headers=headers, data=[data])
            print(r.text)
            break

    def create_ann(self, task_id, data):
        '''
        建立标注
        :param'''
        url = self.create_ann_url.format(task_id)
        print(url)
        result = requests.post(url, data=data, headers=headers)
        return result

    def update_ann(self, ann_id, data):
        '''
        更新标注
        :param'''
        url = self.update_ann_url.format(ann_id)
        result = requests.patch(url, data=data, headers=headers)
        return result

    def del_ann(self, ann_id):
        '''
        删除标注
        :param'''
        url = self.update_ann_url.format(ann_id)
        result = requests.delete(url, headers=headers)
        return result

    def del_pred(self, pred_id):
        """删除识别的结果:param"""
        url = self.update_predict_url.format(pred_id)
        result = requests.delete(url, headers=headers)
        return result


class LabelConvert():

    def __init__(self, label_paths):
        self.label_paths = label_paths
        self.label_info = []
        for label_path in label_paths:
            print(label_path)
            label_info = json.load(open(label_path, "r", encoding="utf-8"))
            print(label_info[0].keys())
            print(label_info[0])
            self.label_info += label_info

    def get_select_ann(self, img_name):
        select_data = [x for x in self.label_info if img_name == x["filename"]]
        if select_data:
            select = select_data[0]
            return select

        else:
            print("没找到标注对应的数据", img_name)
            return {}

    def ann2annStu(self, img_name, ori_dict):
        data = self.get_select_ann(img_name)
        anns = data.get("regions", [])
        ori_dict
        w, h = data.get("width"), data.get("height")
        ori_dict["annotations"] = []

        result = []
        for ann in anns:
            value_p = {}

            k = ann["shape_attributes"]
            polygonlabels = [k["name"]]
            points = [[x / w * 100, k["all_points_y"][i] / h * 100] for i, x in enumerate(k["all_points_x"])]
            if len(points) == 4:
                # 方形标注
                xs = [x[0] for x in points]
                ys = [x[1] for x in points]
                min_x, max_x, min_y, max_y = min(xs), max(xs), min(ys), max(ys)
                points = [[min_x, min_y], [min_x, max_y], [max_x, max_y], [max_x, min_y]]

            original_width = w
            original_height = h
            image_rotation = 0
            from_name = "label"
            to_name = "image"
            type_ = "polygonlabels"

            value_p["original_width"] = original_width
            value_p["original_height"] = original_height
            value_p["image_rotation"] = image_rotation
            value_p["from_name"] = from_name
            value_p["to_name"] = to_name
            value_p["origin"] = "manual"
            value_p["type"] = type_
            value = {}
            value["points"] = points
            value["polygonlabels"] = polygonlabels
            value_p["value"] = value  # {"value": value}
            result.append(value_p)
        inf = {"result": result}
        ori_dict["annotations"].append(inf)
        return inf


if __name__ == '__main__':
    worker = labelStudioApi(host)
    projects = worker.get_project()
    print(projects)
    project_id = projects["results"][0]["id"]
    print("project", projects["results"][0]["id"])
    # worker.import_data("file...","1")
    # for i in tqdm(range(23588)):
    #     worker.del_tasks(i+2)
    #
    # 获取所有标注任务

    # 删除识别的结果
    # for i in range(10):
    #     worker.del_pred(i)
    task_ids = []
    page = 1
    while True:
        try:
            tasks = worker.get_list_project_tasks(project_id, page)
        except :
            break
        sign_break = False
        page += 1
        for task in tasks:
            if task["id"] not in task_ids:
                task_ids.append(task["id"])
            else:
                sign_break = True
        print(page, sign_break)
        if sign_break:
            break

    print("标注任务总个数:{}".format(len(task_ids)))
    print(task_ids)
    print(tasks[0])
    # 获取单个标注任务
    task_id = 42177
    for task_id in tqdm(task_ids):
        print("批量导入标注 ")
        info = worker.get_task(task_id)
        Label_worker = LabelConvert(["/via_regin_data.json",
                                     "/val_union/via_regin_data.json"])
        del_ = False
        cover = False
        for k, v in info["data"].items():
            file_name = os.path.basename(v)
            print(file_name)
            print(info)
            if len(info["annotations"]) == 0:
                result = Label_worker.ann2annStu(file_name, {})
                print(result)
                create_info = worker.create_ann(task_id=task_id, data=json.dumps(result))
                print(create_info)
            else:
                if cover:
                    # worker.del_ann()
                    print("update annotations")
                    ann_id = info["annotations"][0]["id"]
                    result = Label_worker.ann2annStu(file_name, {})
                    print(result)
                    if del_:
                        print("删除：ann_id:{}".format(ann_id))
                        worker.del_ann(ann_id)

                        create_info = worker.create_ann(task_id=task_id, data=json.dumps(
                            result))  # worker.update_ann(ann_id=ann_id, data=json.dumps(result))
                    else:
                        print("更新：ann_id:{}".format(ann_id))
                        create_info = worker.update_ann(ann_id=ann_id, data=json.dumps(result))
                    inf_ = worker.get_task(task_id)
                    print(inf_)
