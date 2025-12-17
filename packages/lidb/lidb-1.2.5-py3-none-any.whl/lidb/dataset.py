# Copyright (c) ZhangYundi.
# Licensed under the MIT License. 
# Created on 2025/10/27 14:13
# Description:

from __future__ import annotations

from collections import defaultdict
from enum import Enum
from functools import partial
from typing import Callable, Literal

import logair
import polars as pl
import polars.selectors as cs
import xcals
import ygo

from .database import put, tb_path, scan, DB_PATH
from .parse import parse_hive_partition_structure
from .qdf import QDF, from_polars


class InstrumentType(Enum):
    STOCK = "Stock"  # 股票
    ETF = "ETF"  #
    CB = "ConvertibleBond"  # 可转债


def complete_data(fn, date, save_path, partitions):
    logger = logair.get_logger(__name__)
    try:
        data = fn(date=date)
        if data is None:
            # 保存数据的逻辑在fn中实现了
            return
        # 剔除以 `_` 开头的列
        data = data.select(~cs.starts_with("_"))
        if not isinstance(data, (pl.DataFrame, pl.LazyFrame)):
            logger.error(f"{save_path}: Result of dataset.fn must be polars.DataFrame or polars.LazyFrame.")
            return
        if isinstance(data, pl.LazyFrame):
            data = data.collect()
        cols = data.columns
        if "date" not in cols:
            data = data.with_columns(pl.lit(date).alias("date")).select("date", *cols)

        put(data, save_path, partitions=partitions)
    except Exception as e:
        logger.error(f"{save_path}: Error when complete data for {date}")
        logger.warning(e)


class Dataset:

    def __init__(self,
                 fn: Callable[..., pl.DataFrame],
                 tb: str,
                 update_time: str = "",
                 partitions: list[str] = None,
                 by_asset: bool = True,
                 by_time: bool = False):
        """

        Parameters
        ----------
        fn: str
            数据集计算函数
        tb: str
            数据集保存表格
        update_time: str
            更新时间: 默认没有-实时更新，也就是可以取到当天值
        partitions: list[str]
            分区
        by_asset: bool
            是否按照标的进行分区，默认 True
        by_time: bool
            是否按照标的进行分区，默认 False
        """
        self._name = ""
        self.fn = fn
        self.fn_params_sig = ygo.fn_signature_params(fn)
        self._by_asset = by_asset
        self._by_time = by_time
        self._append_partitions = ["asset", "date"] if by_asset else ["date", ]
        if by_time:
            self._append_partitions.append("time")
        if partitions is not None:
            partitions = [k for k in partitions if k not in self._append_partitions]
            partitions = [*partitions, *self._append_partitions]
        else:
            partitions = self._append_partitions
        self.partitions = partitions
        self._type_asset = "asset" in self.fn_params_sig
        self.update_time = update_time

        self.tb = tb
        self.save_path = tb_path(tb)
        fn_params = ygo.fn_params(self.fn)
        self.fn_params = {k: v for (k, v) in fn_params}
        self.constraints = dict()
        for k in self.partitions[:-len(self._append_partitions)]:
            if k in self.fn_params:
                v = self.fn_params[k]
                if isinstance(v, (list, tuple)) and not isinstance(v, str):
                    v = sorted(v)
                self.constraints[k] = v
                self.save_path = self.save_path / f"{k}={v}"

    def is_empty(self, path) -> bool:
        return not any(path.rglob("*.parquet"))

    def __call__(self, *fn_args, **fn_kwargs):
        # self.fn =
        fn = partial(self.fn, *fn_args, **fn_kwargs)
        ds = Dataset(fn=fn,
                     tb=self.tb,
                     partitions=self.partitions,
                     by_asset=self._by_asset,
                     by_time=self._by_time,
                     update_time=self.update_time)
        return ds

    def alias(self, new_name: str):
        self._name = new_name

    def get_value(self, date, eager: bool = True, **constraints):
        """
        取值: 不保证未来数据
        Parameters
        ----------
        date: str
            取值日期
        eager: bool
        constraints: dict
            取值的过滤条件

        Returns
        -------

        """
        _constraints = {k: v for k, v in constraints.items() if k in self.partitions}
        _limits = {k: v for k, v in constraints.items() if k not in self.partitions}
        search_path = self.save_path
        for k, v in _constraints.items():
            if isinstance(v, (list, tuple)) and not isinstance(v, str):
                v = sorted(v)
            search_path = search_path / f"{k}={v}"
        search_path = search_path / f"date={date}"

        if not self.is_empty(search_path):
            lf = scan(search_path).cast({"date": pl.Utf8})
            schema = lf.collect_schema()
            _limits = {k: v for k, v in constraints.items() if schema.get(k) is not None}
            lf = lf.filter(date=date, **_limits)
            if not eager:
                return lf
            data = lf.collect()
            if not data.is_empty():
                return data
        fn = self.fn
        save_path = self.save_path

        if self._type_asset:
            if "asset" in _constraints:
                fn = ygo.delay(self.fn)(asset=_constraints["asset"])
        if len(self.constraints) < len(self.partitions) - len(self._append_partitions):
            # 如果分区指定的字段没有在Dataset定义中指定，需要在get_value中指定
            params = dict()
            for k in self.partitions[:-len(self._append_partitions)]:
                if k not in self.constraints:
                    v = constraints[k]
                    params[k] = v
                    save_path = save_path / f"{k}={v}"
            fn = ygo.delay(self.fn)(**params)
        logger = logair.get_logger(__name__)

        today = xcals.today()
        now = xcals.now()
        if (date > today) or (date == today and now < self.update_time):
            logger.warning(f"{self.tb}: {date} is not ready, waiting for {self.update_time}")
            return
        complete_data(fn, date, save_path, self._append_partitions)

        lf = scan(search_path).cast({"date": pl.Utf8})
        schema = lf.collect_schema()
        _limits = {k: v for k, v in constraints.items() if schema.get(k) is not None}
        lf = lf.filter(date=date, **_limits)
        if not eager:
            return lf
        return lf.collect()

    def get_pit(self, date: str, query_time: str, eager: bool = True, **contraints):
        """取值：如果取值时间早于更新时间，则返回上一天的值"""
        if not self.update_time:
            return self.get_value(date, **contraints)
        val_date = date
        if query_time < self.update_time:
            val_date = xcals.shift_tradeday(date, -1)
        return self.get_value(val_date, eager=eager, **contraints).with_columns(date=pl.lit(date), )

    def get_history(self,
                    dateList: list[str],
                    n_jobs: int = 5,
                    backend: Literal["threading", "multiprocessing", "loky"] = "loky",
                    eager: bool = True,
                    rep_asset: str = "000001",  # 默认 000001
                    **constraints):
        """获取历史值: 不保证未来数据"""
        _constraints = {k: v for k, v in constraints.items() if k in self.partitions}
        search_path = self.save_path
        for k, v in _constraints.items():
            if isinstance(v, (list, tuple)) and not isinstance(v, str):
                v = sorted(v)
            search_path = search_path / f"{k}={v}"
        if self.is_empty(search_path):
            # 需要补全全部数据
            missing_dates = dateList
        else:
            if not self._type_asset:
                _search_path = self.save_path
                for k, v in _constraints.items():
                    if k != "asset":
                        _search_path = _search_path / f"{k}={v}"
                    else:
                        _search_path = _search_path / f"asset={rep_asset}"
                hive_info = parse_hive_partition_structure(_search_path)
            else:
                hive_info = parse_hive_partition_structure(search_path)
            exist_dates = hive_info["date"].to_list()
            missing_dates = set(dateList).difference(set(exist_dates))
            missing_dates = sorted(list(missing_dates))
        if missing_dates:
            fn = self.fn
            save_path = self.save_path

            if self._type_asset:
                if "asset" in _constraints:
                    fn = ygo.delay(self.fn)(asset=_constraints["asset"])

            if len(self.constraints) < len(self.partitions) - len(self._append_partitions):
                params = dict()
                for k in self.partitions[:-len(self._append_partitions)]:
                    if k not in self.constraints:
                        v = constraints[k]
                        params[k] = v
                        save_path = save_path / f"{k}={v}"
                fn = ygo.delay(self.fn)(**params)

            with ygo.pool(n_jobs=n_jobs, backend=backend) as go:
                info_path = self.save_path
                try:
                    info_path = info_path.relative_to(DB_PATH)
                except:
                    pass
                for date in missing_dates:
                    go.submit(complete_data,
                              job_name=f"Completing",
                              postfix=info_path,
                              leave=False)(fn=fn,
                                           date=date,
                                           save_path=save_path,
                                           partitions=self._append_partitions,)
                go.do()
        data = scan(search_path, ).cast({"date": pl.Utf8}).filter(pl.col("date").is_in(dateList), **constraints)
        data = data.sort("date")
        if eager:
            return data.collect()
        return data


def loader(data_name: str,
           ds: Dataset,
           date_list: list[str],
           prev_date_list: list[str],
           prev_date_mapping: dict[str, str],
           time: str,
           **constraints) -> pl.LazyFrame:
    if time < ds.update_time:
        if len(prev_date_list) > 1:
            lf = ds.get_history(prev_date_list, eager=False, **constraints)
        else:
            lf = ds.get_value(prev_date_list[0], eager=False, **constraints)
    else:
        if len(date_list) > 1:
            lf = ds.get_history(date_list, eager=False, **constraints)
        else:
            lf = ds.get_value(date_list[0], eager=False, **constraints)
    schema = lf.collect_schema()
    include_time = schema.get("time") is not None
    if include_time:
        lf = lf.filter(time=time)
    else:
        lf = lf.with_columns(time=pl.lit(time))
    if time < ds.update_time:
        lf = lf.with_columns(date=pl.col("date").replace(prev_date_mapping))
    keep = {"date", "time", "asset"}
    if ds._name:
        columns = lf.collect_schema().names()
        rename_cols = set(columns).difference(keep)
        if len(rename_cols) > 1:
            lf = lf.rename({k: f"{ds._name}.{k}" for k in rename_cols})
        else:
            lf = lf.rename({k: ds._name for k in rename_cols})
    return data_name, lf


def load_ds(ds_conf: dict[str, list[Dataset]],
            beg_date: str,
            end_date: str,
            times: list[str],
            n_jobs: int = 7,
            backend: Literal["threading", "multiprocessing", "loky"] = "threading",
            eager: bool = False,
            **constraints) -> dict[str, pl.DataFrame | pl.LazyFrame]:
    """
    加载数据集
    Parameters
    ----------
    ds_conf: dict[str, list[Dataset]]
        数据集配置: key-data_name, value-list[Dataset]
    beg_date: str
        开始日期
    end_date: str
        结束日期
    times: list[str]
        取值时间
    n_jobs: int
        并发数量
    backend: str
    eager: bool
        是否返回 DataFrame
        - True: 返回DataFrame
        - False: 返回LazyFrame
    constraints
        限制条件，比如 asset='000001'
    Returns
    -------
    dict[str, polars.DataFrame | polars.LazyFrame]
        - key: data_name
        - value: polars.DataFrame

    """
    if beg_date > end_date:
        raise ValueError("beg_date must be less than end_date")
    date_list = xcals.get_tradingdays(beg_date, end_date)
    beg_date, end_date = date_list[0], date_list[-1]
    prev_date_list = xcals.get_tradingdays(xcals.shift_tradeday(beg_date, -1), xcals.shift_tradeday(end_date, -1))
    prev_date_mapping = {prev_date: date_list[i] for i, prev_date in enumerate(prev_date_list)}
    results = defaultdict(list)
    index = ("date", "time", "asset")
    with ygo.pool(n_jobs=n_jobs, backend=backend) as go:
        for data_name, ds_list in ds_conf.items():
            for ds in ds_list:
                for time in times:
                    go.submit(loader,
                              job_name="Loading",
                              postfix=data_name)(data_name=data_name,
                                                 ds=ds,
                                                 date_list=date_list,
                                                 prev_date_list=prev_date_list,
                                                 prev_date_mapping=prev_date_mapping,
                                                 time=time,
                                                 **constraints)
        for name, lf in go.do():
            results[name].append(lf)
    LFs = {
        name: (pl.concat(lfList, how="align")
               .sort(index)
               .select(*index,
                       cs.exclude(index))
               )
        for name, lfList in results.items()}
    if not eager:
        return LFs
    return {
        name: lf.collect()
        for name, lf in LFs.items()
    }


class DataLoader:

    def __init__(self, name: str):
        self._name = name
        self._index: tuple[str] = ("date", "time", "asset")
        self._db: QDF = None

    def get(self,
            ds_list: list[Dataset],
            beg_date: str,
            end_date: str,
            times: list[str],
            n_jobs: int = 11,
            backend: Literal["threading", "multiprocessing", "loky"] = "threading",
            **constraints):
        """
        添加数据集
        Parameters
        ----------
        ds_list: list[Dataset]
        beg_date: str
        end_date: str
        times: list[str]
            加载的时间列表
        n_jobs: int
        backend: str
        constraints

        Returns
        -------

        """
        lf = load_ds(ds_conf={self._name: ds_list},
                     beg_date=beg_date,
                     end_date=end_date,
                     n_jobs=n_jobs,
                     backend=backend,
                     times=times,
                     eager=False,
                     **constraints)
        self._db = from_polars(lf[self._name], self._index, align=True)

    @property
    def name(self) -> str:
        return self._name

    @property
    def data(self) -> pl.DataFrame | None:
        if self._db is not None:
            return self._db.data
        return

    def sql(self, *exprs: str) -> pl.DataFrame:
        return self._db.sql(*exprs)

class Zoo:

    """用于研究alpha因子的数据管理部分"""

    def __init__(self):
        self._factor_dls = DataLoader("factor")
        self._mount_dls = DataLoader("mount")
        self._filter_dls = DataLoader("filter")
        self._loader_params = dict()
        self._factors: pl.DataFrame = None
        self._mounted: pl.DataFrame = None

    def load(self,
             beg_date: str,
             end_date: str,
             times: list[str],
             ds_list: list[Dataset],
             n_jobs: int = 11,
             backend: Literal["threading", "multiprocessing", "loky"] = "threading",
             **constraints) -> Zoo:
        self._loader_params = dict(beg_date=beg_date,
                                   end_date=end_date,
                                   times=times,
                                   n_jobs=n_jobs,
                                   backend=backend,
                                   **constraints)
        self._factor_dls.get(ds_list=ds_list, **self._loader_params)
        return self

    def mount(self, ds_list: list[Dataset] = None) -> Zoo:
        """挂载数据: 比如alphalens需要的行业(group)/收益数据..."""
        if ds_list:
            self._mount_dls.get(ds_list=ds_list, **self._loader_params)
        return self

    def filter(self, ds_list: list[Dataset] = None) -> Zoo:
        if ds_list:
            index = ("date", "time", "asset")
            self._filter_dls.get(ds_list=ds_list, **self._loader_params)
            target_index = self.filters.select(*index)
            self._factors = target_index.join(self._factor_dls.data, on=index, how="left")
            self._mounted = target_index.join(self._factor_dls.data, on=index, how="left")
        else:
            self._filter_dls = DataLoader("filter")
        return self

    @property
    def factors(self) -> pl.DataFrame | None:
        """过滤后的因子数据"""
        if self.filters is None:
            return self._factor_dls.data
        return self._factors

    @property
    def mounted(self) -> pl.DataFrame:
        if self.filters is None:
            return self._mount_dls.data
        return self._mounted

    @property
    def filters(self) -> pl.DataFrame | None:
        return self._filter_dls.data

zoo = Zoo()
