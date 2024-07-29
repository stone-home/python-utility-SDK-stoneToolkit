import requests
import tarfile
import os
import pandas as pd
from urllib.parse import urljoin


class Alibaba2020TraceData:
    _instances = {}  # Dictionary to store the instance

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:  # If the instance doesn't exist, create it
            cls._instances[cls] = super(Alibaba2020TraceData, cls).__new__(cls)
        return cls._instances[cls]  # Return the instance

    def __init__(self, target_dir: str = None, cache_dir: str = None):
        self.target_dir = target_dir
        self.cache_dir = cache_dir or os.path.join(target_dir, "caches")
        self._init()
        self._data_name = {
            "job": "pai_job_table",
            "task": "pai_task_table",
            "instance": "pai_instance_table",
            "machine": "pai_machine_spec",
            "group": "pai_group_tag_table",
            "sensor": "pai_sensor_table",
            "metric": "pai_machine_metric",
        }
        self._cache = {}
        self._offset = 600

    @property
    def job_filename(self):
        return self._data_name["job"]

    @property
    def task_filename(self):
        return self._data_name["task"]

    @property
    def instance_filename(self):
        return self._data_name["instance"]

    @property
    def machine_filename(self):
        return self._data_name["machine"]

    @property
    def group_filename(self):
        return self._data_name["group"]

    @property
    def sensor_filename(self):
        return self._data_name["sensor"]

    @property
    def metric_filename(self):
        return self._data_name["metric"]

    def _init(self):
        if os.path.exists(self.target_dir):
            os.makedirs(self.target_dir, exist_ok=True)

    def _build_2020_trace_link(self, data_name: str):
        if data_name not in self._data_name.values():
            raise ValueError(f"Data name {data_name} is not valid.")
        _base_link = "https://aliopentrace.oss-cn-beijing.aliyuncs.com/v2020GPUTraces"
        return f"{_base_link}/{data_name}.tar.gz"

    def _build_2020_trace_header_link(self, data_name: str):
        if data_name not in self._data_name.values():
            raise ValueError(f"Data name {data_name} is not valid.")
        _base_link = "https://raw.githubusercontent.com/alibaba/clusterdata/master/cluster-trace-gpu-v2020/data"
        return f"{_base_link}/{data_name}.header"

    def _build_cache_file(self, data_type: str):
        file_name = f"{data_type}_cache.csv"
        dir_path = self.cache_dir
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        return os.path.join(dir_path, file_name)

    def _store_cache(self, data_type: str, data: pd.DataFrame, cache_file: bool = True):
        if cache_file:
            cache_file = self._build_cache_file(data_type)
            data.to_csv(cache_file, index=True)
            if os.path.isfile(cache_file):
                print(f"{data_type} cache file have been saved.")
            else:
                raise ValueError(f"Failed to save {data_type} cache file.")
        self._cache[data_type] = data

    def _get_cache(self, data_type: str):
        cache_file = self._build_cache_file(data_type)
        if data_type not in self._cache.keys() and os.path.isfile(cache_file):
            print(f"Loading {data_type} cache file...")
            _cache = pd.read_csv(cache_file, index_col=0)
        elif data_type in self._cache.keys():
            print(f"Loading {data_type} cache from memory...")
            _cache = self._cache[data_type]
        else:
            print(f"{data_type} cache not found.")
            _cache = None
        return _cache

    def download_single_trace_data(self, data_name: str, force=False):
        url = self._build_2020_trace_link(data_name)
        header_link = self._build_2020_trace_header_link(data_name)
        file_name = url.split("/")[-1]
        file_path = os.path.join(self.target_dir, file_name)
        if os.path.isfile(file_path) and not force:
            print(f"{file_name} have been downloaded.")
        else:
            print(f"Downloading {file_name}...")
            self.download(url, file_path)
        print(f"Extracting {file_name}...")
        self.extract(file_path, self.target_dir)
        header_file_name = file_name.replace(".tar.gz", ".header")
        header_url = urljoin(header_link, header_file_name)
        print(f"Downloading {header_file_name}...")
        self.download(header_url, os.path.join(self.target_dir, header_file_name))

    def download_all_trace_data(self):
        for data_name in self._data_name.values():
            self.download_single_trace_data(data_name)

    def download(self, url, targe_file, force=False):
        if os.path.isfile(targe_file) and not force:
            return
        response = requests.get(url)
        with open(targe_file, "wb") as file:
            file.write(response.content)

    def extract(self, tar_file, target_dir):
        with tarfile.open(tar_file) as tar:
            tar.extractall(target_dir)

    def get_df(self, data_type, force=False):
        data_name = None
        if data_type in self._data_name.keys():
            data_name = self._data_name[data_type]
            _func = self._get_df_from_csv
        elif data_type == "merged":
            _func = self._get_merged_df
        elif data_type == "modified_merged":
            _func = self._get_modified_merged_df
        elif data_type == "time_series":
            _func = self._get_time_series_data
        else:
            raise ValueError(f"Data type {data_type} is not valid. Only support {self._data_name.keys()} and 'merged' and 'modified_merged'.")

        _cache = self._get_cache(data_type)
        if force or _cache is None:
            print(f"Constructing {data_type} data...")
            if data_name is None:
                _cache = _func()
                self._store_cache(data_type, _cache, cache_file=True)
            else:
                _cache = _func(data_name)
                self._store_cache(data_type, _cache, cache_file=False)
        return self._get_cache(data_type)

    def _get_df_from_csv(self, data_name: str) -> pd.DataFrame:
        print(f"Loading {data_name} dataframes...")
        csv_file = os.path.join(self.target_dir, f"{data_name}.csv")
        header_file = os.path.join(self.target_dir, f"{data_name}.header")
        if not os.path.isfile(csv_file) or not os.path.isfile(header_file):
            self.download_single_trace_data(data_name)
        with open(header_file, "r") as f:
            header = f.read().replace("\n", "").split(",")
        df = pd.read_csv(csv_file, header=None, names=header)
        if data_name in [self._data_name["job"], self._data_name["task"], self._data_name["instance"]]:
            df["start_date"] = df["start_time"].apply(pd.Timestamp, unit='s', tz='Asia/Shanghai')
            df["end_date"] = df["end_time"].apply(pd.Timestamp, unit='s', tz='Asia/Shanghai')
        return df

    def _get_merged_df(self) -> pd.DataFrame:
        print("Loading dataframes and preprocessing Job....")
        job_df = self.get_df("job")
        print("Loading dataframes and preprocessing Task....")
        task_df = self.get_df("task")
        print("Loading dataframes and preprocessing Instance....")
        instance_df = self.get_df("instance")
        print("Loading dataframes and preprocessing Other....")
        machine_df = self.get_df("machine")
        sensor_df = self.get_df("sensor")
        group_df = self.get_df("group")

        print("Merging dataframes...")
        print("Merging job and task...")
        merged_df = job_df.merge(task_df, on='job_name', suffixes=('', '_task'))
        print("Merging job and task and instance...")
        merged_df = merged_df.merge(instance_df, on=["job_name", 'task_name'], suffixes=('', '_instance'))
        print("Merging job and task and instance and machine...")
        merged_df = merged_df.merge(machine_df, on='machine', how='left', suffixes=('', '_machine'))
        print("Merging job and task and instance and machine and sensor...")
        merged_df = merged_df.merge(sensor_df, on='worker_name', how='left', suffixes=('', '_sensor'))
        merged_df = merged_df.merge(group_df, on=['inst_id', "user"], how='left', suffixes=('', '_group'))
        merged_df.drop(
            columns=[
                'inst_id_instance',
                'gpu_type_machine',
                "job_name_sensor",
                "task_name_sensor",
                "inst_id_sensor",
                "machine_sensor",
            ],
            inplace=True
        )
        merged_df["run_time"] = merged_df["end_time"] - merged_df["start_time"]
        merged_df["wait_time"] = merged_df["start_time_instance"] - merged_df["start_time"]
        merged_df["hours"] = merged_df.start_date.apply(lambda d: d.dayofyear * 24 + d.hour)
        merged_df["end_hours"] = merged_df.end_date.apply(lambda d: d.dayofyear * 24 + d.hour)
        # imitate the author's method to filter the data
        # original data has tons of rubbishs before 600 hours
        merged_df = merged_df.query(f"hours >= {self._offset}")
        return merged_df

    def _get_modified_merged_df(self) -> pd.DataFrame:
        merged = self.get_df("merged").copy()
        # Fill the missing end_time and end_date when the status is "Running"
        print("Fill end_time and end_date when the status is 'Running'...")
        max_time = merged['end_time'].max()
        max_date = merged["end_date"].max()
        merged.loc[(merged.status == "Running") & (merged.status_task == "Running") & (merged.status_instance == "Running"), "end_time"] = max_time
        merged.loc[(merged.status == "Running") & (merged.status_task == "Running") & (merged.status_instance == "Running"), "end_date"] = max_date
        merged.loc[(merged.status == "Running") & (merged.status_task == "Running") & (merged.status_instance == "Running"), "end_date_task"] = max_date
        merged.loc[(merged.status == "Running") & (merged.status_task == "Running") & (merged.status_instance == "Running"), "end_time_task"] = max_time
        merged.loc[(merged.status == "Running") & (merged.status_task == "Running") & (merged.status_instance == "Running"), "end_date_instance"] = max_date
        merged.loc[(merged.status == "Running") & (merged.status_task == "Running") & (merged.status_instance == "Running"), "end_time_instance"] = max_time
        print("Fill missing values...")
        # Drop all rows which is in waiting status and the has a value in end_time
        # The end_time should be NaN when the status is "Waiting"
        merged = merged[~((merged.status == "Waiting") & pd.notna(merged.end_time))]
        # fill the missing end_time and end_date
        merged.loc[merged.end_date.isnull() & pd.notnull(merged.end_date_instance), "end_date"] = merged.loc[merged.end_date.isnull() & pd.notnull(merged.end_date_instance), "end_date_instance"]
        merged.loc[merged.end_date.isnull() & pd.notnull(merged.end_date_task), "end_date"] = merged.loc[merged.end_date.isnull() & pd.notnull(merged.end_date_task), "end_date_task"]
        merged.loc[merged.end_date.isnull() & pd.notnull(merged.start_date_instance), "end_date"] = merged.loc[merged.end_date.isnull() & pd.notnull(merged.start_date_instance), "start_date_instance"]
        merged.loc[merged.end_date.isnull() & pd.notnull(merged.start_date_task), "end_date"] = merged.loc[merged.end_date.isnull() & pd.notnull(merged.start_date_task), "start_date_task"]

        merged.loc[merged.end_date.isnull() & pd.notnull(merged.end_time_instance), "end_time"] = merged.loc[merged.end_date.isnull() & pd.notnull(merged.end_time_instance), "end_time_instance"]
        merged.loc[merged.end_date.isnull() & pd.notnull(merged.end_time_task), "end_time"] = merged.loc[merged.end_date.isnull() & pd.notnull(merged.end_time_task), "end_time_task"]
        merged.loc[merged.end_date.isnull() & pd.notnull(merged.start_time_instance), "end_time"] = merged.loc[merged.end_date.isnull() & pd.notnull(merged.start_time_instance), "start_time_instance"]
        merged.loc[merged.end_date.isnull() & pd.notnull(merged.start_time_task), "end_time"] = merged.loc[merged.end_date.isnull() & pd.notnull(merged.start_time_task), "start_time_task"]
        print("Calculating run time and wait time...")
        merged["run_time"] = merged["end_time"] - merged["start_time"]
        merged["wait_time"] = merged["start_time_instance"] - merged["start_time"]
        print("Recalculate wait time when the status is 'Interrupted'...")
        # Re-calculate the wait time when the status is "Interrupted"
        merged.loc[merged.status_instance == "Interrupted", "wait_time"] = merged.loc[merged.status_instance == "Interrupted", "start_time_task"] - merged.loc[merged.status_instance == "Interrupted", "start_time"]
        print("Fill missing values...")
        # Calculate the pure run time, which is the time that the job is actually running without waiting
        merged["pure_run_time"] = merged["run_time"] - merged["wait_time"]

        return merged

    def _get_time_series_data(self) -> pd.DataFrame:
        merged = self.get_df("modified_merged").copy()
        new_data = merged[
            [
                "start_date",
                "end_date",
                "start_date_task",
                "end_date_task",
                "start_date_instance",
                "end_date_instance",
                "status",
                "status_task",
                "status_instance",
                "run_time",
                "wait_time",
                "plan_gpu",
                "plan_cpu",
                "plan_mem",
                "gpu_name"
            ]
        ]
        # new_data = new_data[~(new_data.status == "Waiting")]
        # new_data = new_data[~(new_data.status_task == "Waiting")]
        # new_data = new_data[~(new_data.status_instance == "Waiting")]
        # time_range = pd.date_range(new_data["start_date"].min(), new_data["end_date"].max(), freq="h").strftime("%Y-%m-%d %H:00:00")
        # gpu_counts = pd.Series(0.0, index=time_range)
        # cpu_counts = pd.Series(0.0, index=time_range)
        # memory_counts = pd.Series(0.0, index=time_range)
        # queue = pd.Series(0.0, index=time_range)
        # for _, row in new_data.iterrows():
        #     if pd.isnull(row["start_date_instance"]):
        #         if pd.isnull(row["end_date_task"]):
        #             q_time_range = pd.date_range(row["start_date"], row["start_date_task"], freq="h").strftime("%Y-%m-%d %H:00:00")
        #         else:
        #             q_time_range = pd.date_range(row["start_date"], row["end_date_task"], freq="h").strftime("%Y-%m-%d %H:00:00")
        #     else:
        #         q_time_range = pd.date_range(row["start_date"], row["start_date_instance"], freq="h").strftime("%Y-%m-%d %H:00:00")
        #
        #     queue[q_time_range] += 1
        #
        #     if pd.notnull(row["start_date_instance"]):
        #         g_time_range = pd.date_range(row["start_date_instance"], row["end_date"], freq="h").strftime("%Y-%m-%d %H:00:00")
        #         if pd.notnull(row["plan_gpu"]) and pd.notnull(row["gpu_name"]):
        #             if pd.isnull(row["plan_gpu"]) and pd.notnull(row["gpu_name"]):
        #                 gpu_counts[g_time_range] += 1
        #             else:
        #                 if row["plan_gpu"] >= 100:
        #                     gpu_counts[g_time_range] += 1
        #                 else:
        #                     gpu_counts[g_time_range] += row["plan_gpu"]/100
        #
        #     if pd.notnull(row["start_date_instance"]):
        #         c_time_range = pd.date_range(row["start_date_instance"], row["end_date"], freq="h").strftime("%Y-%m-%d %H:00:00")
        #         if pd.notnull(row["plan_cpu"]):
        #             cpu_counts[c_time_range] += row["plan_cpu"]
        #
        #     if pd.notnull(row["start_date_instance"]):
        #         c_time_range = pd.date_range(row["start_date_instance"], row["end_date"], freq="h").strftime("%Y-%m-%d %H:00:00")
        #         if pd.notnull(row["plan_mem"]):
        #             memory_counts[c_time_range] += row["plan_mem"]
        #
        # gpu_counts_df = gpu_counts.reset_index(name="gpu_counts")
        # cpu_counts_df = cpu_counts.reset_index(name="cpu_counts")
        # memory_counts_df = memory_counts.reset_index(name="memory_counts")
        # queue_df = queue.reset_index(name="queue")
        #
        # merged_df = queue_df.merge(gpu_counts_df, on="index", how="left")
        # merged_df = merged_df.merge(cpu_counts_df, on="index", how="left")
        # merged_df = merged_df.merge(memory_counts_df, on="index", how="left")


        # Filter out all rows that are in waiting status
        new_data = new_data[~new_data["status"].isin(["Waiting", "status_task", "status_instance"])]

        # Set the time range
        time_range = pd.date_range(new_data["start_date"].min(), new_data["end_date"].max(), freq="h").strftime("%Y-%m-%d %H:00:00")
        index_df = pd.DataFrame(index=time_range)

        # 初始化计数列
        index_df["gpu_counts"] = 0.0
        index_df["cpu_counts"] = 0.0
        index_df["memory_counts"] = 0.0
        index_df["queue"] = 0.0
        index_df["running"] = 0.0

        # loop all rows, each row represents an instance
        for _, row in new_data.iterrows():
            start_date = row["start_date"]
            if pd.isnull(row["start_date_instance"]):
                if pd.isnull(row["end_date_task"]):
                    end_date = row["start_date_task"]
                else:
                    end_date = row["end_date_task"]
            else:
                end_date = row["start_date_instance"]
            if pd.isnull(end_date):
                end_date = row["end_date"]

            q_time_range = pd.date_range(start_date, end_date, freq="h").strftime("%Y-%m-%d %H:00:00")
            index_df.loc[q_time_range, "queue"] += 1

            if pd.notnull(row["start_date_instance"]):
                # The resources are only allocated when the instance is running
                g_time_range = pd.date_range(row["start_date_instance"], row["end_date"], freq="h").strftime("%Y-%m-%d %H:00:00")
                if pd.notnull(row["gpu_name"]):
                    if pd.isnull(row["plan_gpu"]):
                        gpu_increment = 100
                    else:
                        gpu_increment = 100 if row["plan_gpu"] >= 100 else row["plan_gpu"]
                else:
                    gpu_increment = 0
                index_df.loc[g_time_range, "gpu_counts"] += gpu_increment
                index_df.loc[g_time_range, "cpu_counts"] += row.get("plan_cpu", 0)
                index_df.loc[g_time_range, "memory_counts"] += row.get("plan_mem", 0)
                index_df.loc[g_time_range, "running"] += 1

        index_df = index_df.reset_index().rename(columns={'index': 'time'})
        index_df["time"] = pd.to_datetime(index_df["time"])
        return index_df




