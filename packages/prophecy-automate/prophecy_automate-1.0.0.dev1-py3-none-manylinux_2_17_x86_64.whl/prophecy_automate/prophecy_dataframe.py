from __future__ import annotations
import json
import logging
import os
import errno
import platform
from typing import List, Optional, Callable, Any
import pyarrow as pa
import pandas as pd
import mmap

from pyspark.sql.dataframe import DataFrame
from pyspark.sql.group import GroupedData
import pyspark

from .lib_wrapper import load_lib, ProphecyLibError
from .utils import _get_caller_name, get_spark


def _is_dataframe(obj) -> bool:
    try:
        from pyspark.sql.connect.dataframe import DataFrame as SparkConnectDataFrame
        return isinstance(obj, (pyspark.sql.dataframe.DataFrame, SparkConnectDataFrame))
    except ImportError:
        return isinstance(obj, pyspark.sql.dataframe.DataFrame)


def _is_grouped_data(obj) -> bool:
    try:
        from pyspark.sql.connect.group import GroupedData as SparkConnectGroupedData
        return isinstance(obj, (pyspark.sql.group.GroupedData, SparkConnectGroupedData))
    except ImportError:
        return isinstance(obj, pyspark.sql.group.GroupedData)

_lib_instance = None

def _get_lib():
    global _lib_instance
    if _lib_instance is None:
        _lib_instance = load_lib()
    return _lib_instance

def _wrap_pyspark_method(target: Any, gem_name: str) -> Callable[..., Any]:
    
    if not callable(target):
        raise Exception(f"Not a callable from pyspark: {type(target)}")
        
    def wrapper(*args, **kwargs):
        
        processed_args = []
        for arg in args:
            if isinstance(arg, ProphecyDataFrame):
                if arg.df is None:
                    arg.df = arg.populate_pyspark_df()
                processed_args.append(arg.df)
            else:
                processed_args.append(arg)
        
        processed_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, ProphecyDataFrame):
                if value.df is None:
                    value.df = value.populate_pyspark_df()
                processed_kwargs[key] = value.df
            else:
                processed_kwargs[key] = value
        
        out = target(*processed_args, **processed_kwargs)
        
        if _is_dataframe(out):
            from .common import wf
            pdf = wf.create_pdf(gem_name)
            pdf.df = out
            # Required when we want to persist output of each pyspark gem
            # pdf.df.persist()
            # pdf.df.count()
            pdf.is_pyspark_gem = True
            return pdf
        elif _is_grouped_data(out):
            # GroupBy() / pivot() returns GroupedData
            return ProphecyGroupedData(out, gem_name)
        elif out is None:
            # show(), write() returns None
            return None
        else:
            raise Exception(f"Got unexpected output from pyspark : {type(out)}")
    return wrapper


class ProphecyGroupedData:
    
    def __init__(self, grouped_data: GroupedData, gem_name: str):
        self._grouped_data = grouped_data
        self._gem_name = gem_name
    
    def __getattr__(self, name: str) -> Callable[..., Any]:
        target = getattr(self._grouped_data, name)
        return _wrap_pyspark_method(target, self._gem_name)


class ProphecyDataFrame:

    def __init__(
        self,
        data_client_handle: int,
        gem_name: str,
        is_pyspark_gem: bool = False
    ):

        self.gem_name = gem_name
        self.data_client_handle = data_client_handle
        self.is_pyspark_gem = is_pyspark_gem
        
        self.df: Optional[DataFrame] = None
        self.memfd: Optional[int] = None
        self.is_write_handle_populated: bool = False
        
        self.reader_handles: List[int] = []
        lib = _get_lib()
        self.writer_handle = lib.get_writer_handle(data_client_handle)

        consumer_count = lib.get_consumer_count(data_client_handle)
        for i in range(consumer_count):
            reader_handle = lib.get_reader_handle(data_client_handle, i)
            self.reader_handles.append(reader_handle)
        

    def add_new_reader(self) -> int:
        add_at_idx = len(self.reader_handles)
        new_reader_handle = _get_lib().add_reader_to_data_client(self.data_client_handle, add_at_idx)
        self.reader_handles.append(new_reader_handle)
        return add_at_idx

    @classmethod
    def create(
        cls,
        gem_name: str,
        consumer_count: int = 1,
        is_pyspark_gem: bool = False
    ) -> "ProphecyDataFrame":
        
        data_client_handle = _get_lib().create_data_client(gem_name, consumer_count)
        return cls(data_client_handle, gem_name, is_pyspark_gem)

    def __getattr__(self, name: str) -> Callable[..., Any]:
        
        df = self.__dict__.get("df", None)
        if df is None:         
            self.df = self.populate_pyspark_df()

        target = getattr(self.df, name)

        gem_name = _get_caller_name(2)
        
        return _wrap_pyspark_method(target, gem_name)


    def _read_from_fd(self, fd: int) -> tuple[pa.Table, Optional[mmap]]:
        dup = os.dup(fd)
        try:
            size = os.fstat(dup).st_size
            if size <= 0:
                raise ValueError("memfd has zero size; nothing to map")
            
            ro = os.open(f"/proc/self/fd/{fd}", os.O_RDONLY)
            dup_ro = os.dup(ro)
            mm = mmap.mmap(dup_ro, length=size, access=mmap.ACCESS_READ)
            os.close(dup_ro)
            os.close(ro)  # CRITICAL: Close the original FD to prevent leak
            os.close(dup)
            
            buf = pa.py_buffer(mm)
    
            reader = pa.ipc.open_stream(pa.BufferReader(buf))
            
            try:
                table = reader.read_all()
            finally:
                reader.close()
                
            return table, mm
    
        except (PermissionError, OSError) as mmap_err:
            print(f"mmap failed ({mmap_err}), falling back to regular file read")
            logging.error(
                f"mmap failed ({mmap_err}), falling back to regular file read"
            )
            os.lseek(dup, 0, os.SEEK_SET)
            data = os.read(dup, size)
            os.close(dup)
            dup = None
            buf = pa.py_buffer(data)
            reader = pa.ipc.open_stream(pa.BufferReader(buf))
            try:
                table = reader.read_all()
            finally:
                reader.close()

            print("mmap did not work, falling back to data-copy approach")

            # Return None for mmap since we used regular read
            return table, None
        except Exception as ex:    
            try:
                os.close(dup)
            except Exception as e:
                logging.error(f"Unable to close fd {dup}. Exception1 : {e}")
                pass
            raise Exception(f"Encountered exception in _read_from_fd : {ex}")
    
    def _write_to_fd_darwin(self, table: pa.Table) -> int:
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.arrow') as tmp:
            tmp_path = tmp.name
        try:
            with pa.OSFile(tmp_path, 'wb') as sink:
                with pa.ipc.new_stream(sink, table.schema) as writer:
                    writer.write_table(table)
    
            f = open(tmp_path, 'rb')
            fd = f.fileno()
            dup_fd = os.dup(fd)
            f.close()
            os.unlink(tmp_path)
    
            return dup_fd
        
        except Exception as e:
            try:
                os.unlink(tmp_path)
            except:
                pass
            raise e

    def _write_to_memfd_linux(self, pa_table: pa.Table) -> int:

        import os
        import fcntl
        import pyarrow as pa
        
        fd = os.memfd_create("arrow_table", flags=os.MFD_CLOEXEC)
        logging.error(f"Created FD={fd} inside _write_to_memfd_linux")
    
        try:
            f = os.fdopen(fd, "wb", closefd=False)

            with pa.output_stream(f) as sink:
                with pa.ipc.new_stream(sink, pa_table.schema) as writer:
                    writer.write_table(pa_table)
    
            os.fsync(fd)
            os.lseek(fd, 0, os.SEEK_SET)

    
            return fd
    
        except Exception:
            try:
                os.close(fd)
            except Exception as e:
                logging.error(f"Unable to close fd {fd}. Exception2 : {e}")
            raise
    
    
    def populate_pyspark_df(self):
        
        if self.df is not None:
            return self.df
        
        reader_handle = self.reader_handles[0]

        if self.memfd is None:
            self.memfd = _get_lib().create_memfd_from_reader(reader_handle)
        else:
            logging.info(f"Re-using the existing memfd for {self.gem_name}")

        try:
            spark = get_spark()           
            arrow_table, mmaped = self._read_from_fd(self.memfd)

            def create_df_from_arrow(spark: pyspark.sql.SparkSession, pa_table):
                spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
                major = int(pyspark.__version__.split('.', 1)[0])
                
                logging.info(f"PySpark major version is : {major}")

                if major >= 4:
                    return spark.createDataFrame(pa_table)
                else:
                    # .combine_chunks() - but created a copy of data
                    # types_mapper=pd.ArrowDtype
                    return spark.createDataFrame(pa_table.to_pandas())

            self.df = create_df_from_arrow(spark, arrow_table)
            
            del arrow_table
            if mmaped is not None:
                mmaped.close()

        except Exception:
            raise Exception(f"Error in populate_pyspark_df")

        return self.df

    def populate_data_handle(self) -> None:
    
        pandas_df = self.df.toPandas()
        table = pa.Table.from_pandas(pandas_df)
        
        if platform.system() == "Linux":
            self.memfd = self._write_to_memfd_linux(table)
        else:
            self.memfd = self._write_to_fd_darwin(table)
    
        _get_lib().populate_writer_from_memfd(self.writer_handle, self.memfd)
        
        del pandas_df
        del table
        os.close(self.memfd)
        self.memfd = None

    def close_fd(self) -> None:
        if self.memfd is None:
            return
            
        try:
            os.close(self.memfd)
            logging.info(f"Successfully closed mem FD={self.memfd} for {self.gem_name}")
            self.memfd = None 
        except OSError as e:
            if e.errno == errno.EBADF:
                logging.warning(f"FD {self.memfd} for {self.gem_name} was already closed.")
                self.memfd = None
            else:
                logging.error(f"Unexpected error closing FD {self.memfd} for {self.gem_name}: {e}")
                self.memfd = None
                raise e

    def close_data_client(self) -> None:
        try:
            _get_lib().close_data_client(self.data_client_handle)
            logging.info(f"Closed data client for {self.gem_name}")
        except ProphecyLibError as e:
            logging.error(f"Failed to close data client for {self.gem_name}: {e}")
            raise e

    def close(self) -> None:
        # commenting since we are eagerly closing
        # self.close_data_client()
        # self.close_fd()
        try:
            self.df.unpersist(blocking=True)
            logging.info(f"Unpersisted DataFrame for {self.gem_name}")
        except Exception as e:
            logging.warning(f"Failed to unpersist DataFrame for {self.gem_name}: {e}")
                    

