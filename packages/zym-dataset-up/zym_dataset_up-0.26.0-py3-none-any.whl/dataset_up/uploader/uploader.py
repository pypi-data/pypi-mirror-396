import os
import time
import sys
import threading
from typing import List
from tqdm import tqdm
from threading import Thread
from dataset_up.client import Client
from dataset_up.uploader.uploaded_file import UploadingFile
from dataset_up.utils.system_utils import caculate_upload_worker_num 
from dataset_up.utils.file import list_files_in_folder
from dataset_up.uploader.upload_context import parse_filelist_to_tasklist,upload_files
from dataset_up.utils.concurrent_utils import error_event,interrupt_event,can_quit_event
from dataset_up.uploader.upload_context import update_lock
from dataset_up.client.AuthClient import auth_client
from dataset_up.utils.sliding_window_speed_calculator import SlidingWindowSpeedCalculator
from dataset_up.log.logger import get_logger
from dataset_up.update.update_check import update_check


logger = get_logger(__name__)

class   Uploader(object):
    def __init__(self, client: Client,dataset_id: str, version: str,worker_num: int = None,calc_sha256: bool = False,enable_inner_network: bool = False):
        self.client = client
        self.task_id = None
        self.dataset_id = dataset_id
        self.version = version
        self.worker_num = caculate_upload_worker_num() if worker_num is None else worker_num   
        self.calc_sha256 = calc_sha256
        self.enable_inner_network = enable_inner_network
        self.speed_calculator = SlidingWindowSpeedCalculator()
        
        
    def upload_file(self, source_path: str, destination_path: str):
        
        source_path = os.path.realpath(os.path.expanduser(source_path))
        
        # 检查源文件是否存在
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"source path not exist: {source_path}")
        if not os.path.isfile(source_path):
            raise IsADirectoryError(f"source path is not a file: {source_path}")
        
        if not destination_path:
            destination_path = "/"

        if not destination_path.endswith("/"):
            destination_path = destination_path + "/"
            
        self.create_task(is_dir=False)
        refresh_token_periodically()
        
        rel_path = os.path.basename(source_path)
        target_path = os.path.join(destination_path, rel_path)
        
        file = UploadingFile(client=self.client,
                                 abs_path=source_path,
                                 rel_path=rel_path,
                                 target_path=target_path,
                                 dataset_id=self.dataset_id,
                                 version=self.version,
                                 calc_sha256=self.calc_sha256,
                                 enable_inner_network=self.enable_inner_network)
        
        file_list = [file]
        task_list = []
        
        total_list_size = len(file_list)
        total_size = sum([file.size for file in file_list])
            
        with tqdm(total=total_list_size, ncols=100, desc="preparing...", unit_scale=True,position=0) as progress:
            task_list = parse_filelist_to_tasklist(file_list,task_list ,self.dataset_id, self.version, progress, self.worker_num)
        
        begin_time = time.time()
        
        uploaded_size = total_size - sum([task[2] for task in task_list])
        with tqdm(total=total_size,initial=uploaded_size, ncols=100, desc="uploading...", unit_scale=True,mininterval=0.5,position=1,disable=True) as progress:
            self.asyc_report(self.task_id,self.dataset_id,self.version,destination_path=target_path ,operate_type="UPLOAD",
                             exec_state="UPLOADING",is_dir=False,begin_time=begin_time,progress=progress)
            upload_files(task_list, progress, self.worker_num)
            
        if not error_event.is_set() and not interrupt_event.is_set():
            self.report(self.task_id,self.dataset_id,self.version,operate_type="UPLOAD", exec_state="UPLOAD_COMPLETE", progress=1.0,file_size=progress.total,begin_time=begin_time,
                                        remaining_time=0,destination_path=target_path,is_dir=False,end_time=time.time())
            print(f"\nupload {source_path} success!\n")
            logger.info(f"upload {source_path} success")
        else:
            print(f"\nupload {source_path} failed, please retry!\n")
            logger.error(f"upload {source_path} failed, please retry!")

        
    def upload_folder(self, source_path: str, destination_path: str):
        """
        上传指定的本地文件夹到目标路径。

        参数:
            source_path (str): 本地文件夹路径，支持 ~ 和相对路径。
            destination_path (str): 目标路径，若为空则使用根路径 '/'。
        """
        
        source_path = os.path.realpath(os.path.expanduser(source_path))
        
        # 检查源路径是否存在
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"source path not exist: {source_path}")
        if not os.path.isdir(source_path):
            raise NotADirectoryError(f"source path is not a directory: {source_path}")
        
    
        if not destination_path:
            destination_path = "/"

        if not destination_path.endswith("/"):
            destination_path = destination_path + "/"
            
        self.create_task(is_dir=True)
        refresh_token_periodically()
            
        file_list = []
        task_list = []
        
        file_list.extend(self.get_files_to_upload(source_path,destination_path))
        # 倒序遍历删除（避免索引问题）
        for i in range(len(file_list) - 1, -1, -1):
            if file_list[i].size == 0:
                print("file size is 0, skip: " + file_list[i].abs_path)
                del file_list[i]
        
        total_size = sum([file.size for file in file_list])
        
        total_list_size = len(file_list)
            
        with tqdm(total=total_list_size, ncols=100, desc="preparing...", unit='files', unit_scale=False,position=0,leave=True) as progress:
            task_list = parse_filelist_to_tasklist(file_list,task_list ,self.dataset_id, self.version, progress, self.worker_num)
        
        begin_time = time.time()
        uploaded_size = total_size - sum([task[2] for task in task_list])
        with tqdm(total=total_size,initial=uploaded_size, ncols=100, desc="total progress...", unit_scale=True,mininterval=2,position=3,leave=True) as progress:
            self.asyc_report(self.task_id,self.dataset_id,self.version,destination_path=destination_path ,operate_type="UPLOAD",
                             exec_state="UPLOADING",is_dir=True,begin_time=begin_time,progress=progress)
            upload_files(task_list, progress, self.worker_num)
        if not error_event.is_set() and not interrupt_event.is_set():
            self.report(self.task_id,self.dataset_id,self.version,operate_type="UPLOAD", exec_state="UPLOAD_COMPLETE", progress=1.0,file_size=progress.total,begin_time=begin_time,
                                        remaining_time=0,destination_path=destination_path,is_dir=True,end_time=time.time())
            progress.close()
            print(f"\nupload dir {source_path} success!\n")
            logger.info(f"upload dir {source_path} success!")
        else:
            print(f"\nupload dir {source_path} failed,please retry!\n")
            logger.error(f"upload dir {source_path} failed,please retry!")
    
    
    def get_files_to_upload(self,source_path,destination_path) -> List[UploadingFile]:
        import concurrent.futures
        from dataset_up.utils.system_utils import get_physical_cores_count
        worker_num = max(get_physical_cores_count()//4,6)
        
        file_list = []
        file_paths = list_files_in_folder(source_path)
        def create_uploading_file(file_path):
            rel_path = os.path.relpath(file_path, source_path).replace("\\", "/")
            target_path = os.path.join(destination_path, rel_path)
            return UploadingFile(client=self.client,
                            abs_path=file_path,
                            rel_path=rel_path,
                            target_path=target_path,
                            dataset_id=self.dataset_id,
                            version=self.version,
                            calc_sha256=self.calc_sha256,
                            enable_inner_network=self.enable_inner_network)

        # 使用线程池并发处理文件
        with concurrent.futures.ThreadPoolExecutor(max_workers=worker_num) as executor:
            # 提交所有任务
            future_to_file = {executor.submit(create_uploading_file, file_path): file_path 
                            for file_path in file_paths}
            
            # 收集结果
            for future in concurrent.futures.as_completed(future_to_file):
                try:
                    file = future.result()
                    file_list.append(file)
                except Exception as e:
                    file_path = future_to_file[future]
                    logger.critical(f"error happend when processing {file_path}: {e}")
                    raise e
        
        return file_list
    

    def report(self,task_id,dataset_id,version,operate_type,exec_state,progress,file_size,begin_time,remaining_time,destination_path,is_dir,end_time = None):
        req = {
            "taskId": task_id,
            "datasetId": dataset_id,
            "version": version,
            "filePath": destination_path,
            "operateType": operate_type,
            "execState": exec_state,
            "progress": progress,
            "fileSize": file_size,
            "beginTime": begin_time,
            "endTime" : end_time,
            "remainingTime": remaining_time,
            "isDir": is_dir
        }
        self.client.report(req)
        
    def asyc_report(self,task_id,dataset_id,version,destination_path,operate_type,exec_state,is_dir,begin_time,progress: tqdm):
        def report_progress():
                
                progress_ratio = 0
                remaining_time = 0
                
                while not error_event.is_set() and not interrupt_event.is_set():
                    if progress.n < progress.total:
                        
                        with update_lock:
                                current_time = time.time()
                                processed_bytes = progress.n
                                self.speed_calculator.add_record(current_time, processed_bytes)
                                speed = self.speed_calculator.get_speed(current_time)
                                if speed > 0:
                                    remaining_time = self.speed_calculator.get_remaining_time(progress.total, current_time)
                                else:
                                    remaining_time = 99999 * 60.0
                                progress_ratio = processed_bytes / progress.total
                        
                        try:
                            self.report(task_id,dataset_id,version,operate_type=operate_type, exec_state=exec_state, progress=progress_ratio,file_size=progress.total,begin_time=begin_time,
                                remaining_time=remaining_time,destination_path=destination_path,is_dir=is_dir,end_time=None)
                        except Exception as e:
                            logger.error(f"Error occurred while reporting progress: {e}")
                        
                    else:
                        break
                    time.sleep(5)  # 每隔 5 秒汇报一次
                if error_event.is_set():
                    try:
                        self.report(task_id,dataset_id,version,operate_type=operate_type, exec_state="UPLOAD_FAILED", progress=progress_ratio,file_size=progress.total,begin_time=begin_time,
                                remaining_time=remaining_time,destination_path=destination_path,is_dir=is_dir,end_time=time.time())
                    except Exception as e:
                        logger.error(f"failed to report when error_event is set,error:{e}")
                    
                if interrupt_event.is_set():
                    try:
                        self.report(task_id,dataset_id,version,operate_type=operate_type, exec_state="UPLOAD_CANCELED", progress=progress_ratio,file_size=progress.total,begin_time=begin_time,
                                remaining_time=remaining_time,destination_path=destination_path,is_dir=is_dir,end_time=time.time())
                    except Exception as e:
                        logger.error(f"failed to report when interrupt_event is set,error:{e}")
                can_quit_event.set()    
        reporter_thread = Thread(target=report_progress, daemon=True)
        reporter_thread.setDaemon(True)
        reporter_thread.start()
    
    
    def list(self,dir ="/"):
        if dir == "":
            dir = "/"
        req = {
            "datasetId": self.dataset_id,
            "version": self.version,
            "filePath": dir
        }
        ret = self.client.list(req)
        objects = ret["objects"]
        return objects
        
    
    def mkdir(self,dir):
        if dir is None or str(dir).strip() == "":
            raise Exception("dir cannot be empty")
        req = {
            "datasetId": self.dataset_id,
            "version": self.version,
            "dir": dir
        }
        ret = self.client.mkdir(req)
        dir_key = ret["dirKey"]
        result = ret["result"]
        message = ret["message"]
        if result:
            print(f"Create directory {dir} successfully")
        else:
            print(f"Failed to create directory {dir}, message: {message}")
            
    def deleteDir(self,dir):
        if dir is None or str(dir).strip() == "":
            raise Exception("dir cannot be empty")
        req = {
            "datasetId": self.dataset_id,
            "version": self.version,
            "dir": dir
        }
        ret = self.client.deleteDir(req)
        dir = ret["dir"]
        result = ret["result"]
        message = ret["message"]
        if result:
            print(f"Delete directory {dir} successfully")
        else:
            print(f"Failed to delete directory {dir}, message: {message}")
        
    
    def deleteFile(self,file):
        if file is None or str(file).strip() == "":
            raise Exception("file cannot be empty")
        req = {
            "datasetId": self.dataset_id,
            "version": self.version,
            "filePath": file
        }
        ret = self.client.deleteFile(req)
        key = ret["key"]
        result = ret["result"]
        dataset_id = ret["datasetId"]
        version = ret["version"]
        if result:
            print(f"Delete file {file} successfully")
        else:
            print(f"Failed to delete file {file}")
            
    def create_task(self,is_dir: bool):
        if is_dir is None:
            raise Exception("is_dir is required")
        req = {
            "datasetId": self.dataset_id,
            "version": self.version,
            "isDir": is_dir
        }
        ret = self.client.create_task(req)
        success = ret["success"]
        if not success:
            message = ret["message"]
            raise Exception(f"create upload task failed , message:{message}")                
        self.task_id = ret["taskId"]
        if self.task_id != None and self.task_id != "":
            print("create task success,taskId: %s" % self.task_id)
        else:
            raise Exception("create task failed")
        
        


def login(ak: str, sk: str): 
    try:
        auth_client.login(ak, sk)
        update_check()
        print("login success")
    except Exception as e:
        print(f"login failed: {e}")
        raise e      
        
        
def upload_file(dataset_id: str, source_path: str, target_path: str = "/", version: str = 'master',calc_sha256: bool = False,enable_inner_network: bool = False):
    from dataset_up.utils.interrupt_utils import register_signal_handler
    from dataset_up.client.Client import api_client
    try:
        register_signal_handler()
        uploader = Uploader(api_client, dataset_id, version,calc_sha256=calc_sha256,enable_inner_network=enable_inner_network)
        uploader.upload_file(source_path, target_path)
    except Exception as e:
        logger.error(f"error occurred while uploading file: {e}")
        raise e 


def upload_folder(dataset_id: str, source_path: str, target_path: str = "/", version: str = 'master',calc_sha256: bool = False,enable_inner_network: bool = False):
    from dataset_up.utils.interrupt_utils import register_signal_handler
    from dataset_up.client.Client import api_client
    try:
        register_signal_handler()
        uploader = Uploader(api_client, dataset_id, version,calc_sha256=calc_sha256,enable_inner_network=enable_inner_network)
        uploader.upload_folder(source_path, target_path)
    except Exception as e:
        logger.error(f"error occurred while uploading folder: {e}")
        raise e 


def mkdir(dataset_id: str, version: str, dir: str):
    from dataset_up.client.Client import api_client
    try:
        uploader = Uploader(api_client, dataset_id, version)
        uploader.mkdir(dir)
    except Exception as e:
        print(f"create dir {dir} failed: {e}")
        raise e

def delete_file(dataset_id: str, version: str, file: str):
    from dataset_up.client.Client import api_client
    try:
        uploader = Uploader(api_client, dataset_id, version)
        uploader.deleteFile(file)
    except Exception as e:
        print(f"delete file {file} failed: {e}")
        raise e 


def delete_dir(dataset_id: str, version: str, dir: str):
    from dataset_up.client.Client import api_client
    try:
        uploader = Uploader(api_client, dataset_id, version)
        uploader.deleteDir(dir)
    except Exception as e:
        print(f"delete dir {dir} failed: {e}")
        raise e


def list(dataset_id: str, version: str, dir: str):
    from dataset_up.client.Client import api_client
    from dataset_up.utils.output_format import print_file_list
    try:
        uploader = Uploader(api_client, dataset_id, version)
        files = uploader.list(dir)
        print_file_list(files)
    except Exception as e:
        print(f"list dir {dir} failed: {e}")
        raise e
    
def refresh_token_periodically():
    """
    每隔1小时调用一次auth_client.get_token_from_remote()方法
    """
    def refresh_loop():
        while True:
            try:
                time.sleep(3600)  # 间隔1小时（3600秒）
                auth_client.get_token_from_remote()
            except Exception as e:
                print(f"Token refresh failed: {e}")
                time.sleep(3600)  # 即使出错也继续下一次尝试
    
    # 创建并启动后台线程
    refresh_thread = threading.Thread(target=refresh_loop, daemon=True)
    refresh_thread.start()