import ctypes
import os
import sys
from pathlib import Path
from typing import Optional

class ProphecyLibError(Exception):
    pass

def _find_library() -> Path:
    """
    Find the libprophecy_1.so library in the following order:
    1. PROPHECY_LIB_PATH environment variable (for development/override)
    2. Package directory (for installed package)
    3. System library paths
    """
    # First, check environment variable (for development/override)
    env_path = os.environ.get("PROPHECY_LIB_PATH")
    if env_path:
        lib_path = Path(env_path)
        if lib_path.exists():
            return lib_path
    
    # Second, check in the package directory (for installed package)
    package_dir = Path(__file__).parent
    lib_name = "libprophecy_1.so"
    
    lib_path = package_dir / lib_name
    if lib_path.exists():
        return lib_path
    
    # Third, check in common system locations
    system_paths = [
        Path("/usr/local/lib") / lib_name,
        Path("/usr/lib") / lib_name,
    ]
    
    for lib_path in system_paths:
        if lib_path.exists():
            return lib_path
    
    # If nothing found, raise an error with helpful information
    raise Exception(
        f"Could not find prophecy library '{lib_name}'. Searched:\n"
        f"  - PROPHECY_LIB_PATH environment variable: {env_path or 'not set'}\n"
        f"  - Package directory: {package_dir}\n"
        f"  - System paths: /usr/local/lib, /usr/lib\n"
        f"Please set PROPHECY_LIB_PATH or ensure the library is bundled with the package."
    )


class ProphecyLib:
    
    def __init__(self, lib_path: Optional[Path] = None):
        
        if lib_path is None:
            lib_path = _find_library()

        self.lib_path = lib_path
        
        # Preload Tableau dependencies (DuckDB is static)
        package_dir = lib_path.parent
        
        # Set LD_LIBRARY_PATH to package directory
        if sys.platform.startswith('linux'):
            ld_path = os.environ.get('LD_LIBRARY_PATH', '')
            os.environ['LD_LIBRARY_PATH'] = f"{package_dir}:{ld_path}" if ld_path else str(package_dir)
        
        # Preload Tableau dependencies
        dependencies = [
            "libtableauhyperapi.so",    # Tableau Hyper API  
            "libTableauCppLibrary.so",  # Tableau C++ library
        ]
        
        for dep_name in dependencies:
            dep_lib = package_dir / dep_name
            if dep_lib.exists():
                try:
                    ctypes.CDLL(str(dep_lib))
                except Exception as e:
                    import warnings
                    warnings.warn(f"Failed to preload {dep_name}: {e}")
        
        # Load main library using dlopen with RTLD_LAZY to avoid TLS errors
        # RTLD_LAZY: Don't resolve all symbols immediately (avoids TLS block allocation)
        if sys.platform.startswith('linux'):
            # On Linux, use os.RTLD_LAZY flag (not ctypes.RTLD_LAZY)
            self._lib = ctypes.CDLL(str(lib_path), mode=os.RTLD_LAZY)
        else:
            # On other platforms, use default
            self._lib = ctypes.CDLL(str(lib_path))
        self._setup_functions()

    def _setup_functions(self):

        self._lib.FreeString.argtypes = [ctypes.c_char_p]
        self._lib.FreeString.restype = None

        self._lib.CreateDataClient.argtypes = [
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_char_p)
        ]
        self._lib.CreateDataClient.restype = ctypes.c_longlong

        self._lib.GetReaderHandle.argtypes = [
            ctypes.c_longlong,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_char_p)
        ]
        self._lib.GetReaderHandle.restype = ctypes.c_longlong

        self._lib.GetWriterHandle.argtypes = [
            ctypes.c_longlong,
            ctypes.POINTER(ctypes.c_char_p)
        ]
        self._lib.GetWriterHandle.restype = ctypes.c_longlong

        self._lib.GetConsumerCount.argtypes = [
            ctypes.c_longlong,
            ctypes.POINTER(ctypes.c_char_p)
        ]
        self._lib.GetConsumerCount.restype = ctypes.c_int

        self._lib.ProphecyRead.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_longlong,
            ctypes.POINTER(ctypes.c_char_p)
        ]
        self._lib.ProphecyRead.restype = ctypes.c_int

        self._lib.ProphecyWrite.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_longlong,
            ctypes.POINTER(ctypes.c_char_p)
        ]
        self._lib.ProphecyWrite.restype = ctypes.c_int

        self._lib.ProphecyTransform.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_longlong,
            ctypes.c_longlong,
            ctypes.POINTER(ctypes.c_char_p)
        ]
        self._lib.ProphecyTransform.restype = ctypes.c_int

        self._lib.CreateMemfdFromReader.argtypes = [
            ctypes.c_longlong,
            ctypes.POINTER(ctypes.c_char_p)
        ]
        self._lib.CreateMemfdFromReader.restype = ctypes.c_int

        self._lib.PopulateWriterFromMemfd.argtypes = [
            ctypes.c_longlong,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_char_p)
        ]
        self._lib.PopulateWriterFromMemfd.restype = ctypes.c_int

        self._lib.CloseDataClient.argtypes = [
            ctypes.c_longlong,
            ctypes.POINTER(ctypes.c_char_p)
        ]
        self._lib.CloseDataClient.restype = ctypes.c_int

        self._lib.GetDataClientInfo.argtypes = [
            ctypes.c_longlong,
            ctypes.POINTER(ctypes.c_char_p)
        ]
        self._lib.GetDataClientInfo.restype = ctypes.c_char_p

        self._lib.AddReaderToDataClient.argtypes = [
            ctypes.c_longlong,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_char_p)
        ]
        self._lib.AddReaderToDataClient.restype = ctypes.c_longlong

        self._lib.GetProphecySecret.argtypes = [
            ctypes.c_char_p,  # scope
            ctypes.c_char_p,  # name
            ctypes.POINTER(ctypes.c_char_p)  # error
        ]
        self._lib.GetProphecySecret.restype = ctypes.c_char_p

    def _check_error(self, error_ptr: ctypes.c_char_p) -> None:
        if error_ptr:
            error_bytes = error_ptr.value if hasattr(error_ptr, 'value') else error_ptr
            if error_bytes:
                error_msg = error_bytes.decode('utf-8') if isinstance(error_bytes, bytes) else str(error_bytes)
                self._lib.FreeString(error_ptr)
                raise ProphecyLibError(error_msg)

    def create_data_client(self, process_id: str, consumer_count: int) -> int:
        error = ctypes.c_char_p()
        handle = self._lib.CreateDataClient(
            process_id.encode('utf-8'),
            consumer_count,
            ctypes.byref(error)
        )
        self._check_error(error)
        if handle < 0:
            raise ProphecyLibError("Failed to create data client")
        return handle

    def get_reader_handle(self, data_client_handle: int, reader_index: int) -> int:
        error = ctypes.c_char_p()
        handle = self._lib.GetReaderHandle(
            data_client_handle,
            reader_index,
            ctypes.byref(error)
        )
        self._check_error(error)
        if handle < 0:
            raise ProphecyLibError(f"Failed to get reader handle at index {reader_index}")
        return handle

    def get_writer_handle(self, data_client_handle: int) -> int:
        error = ctypes.c_char_p()
        handle = self._lib.GetWriterHandle(
            data_client_handle,
            ctypes.byref(error)
        )
        self._check_error(error)
        if handle < 0:
            raise ProphecyLibError("Failed to get writer handle")
        return handle

    def get_consumer_count(self, data_client_handle: int) -> int:
        error = ctypes.c_char_p()
        count = self._lib.GetConsumerCount(
            data_client_handle,
            ctypes.byref(error)
        )
        self._check_error(error)
        if count < 0:
            raise ProphecyLibError("Failed to get consumer count")
        return count


    def prophecy_read(self, gem_type: str, config_json: str, data_client_handle: int) -> None:
        error = ctypes.c_char_p()
        result = self._lib.ProphecyRead(
            gem_type.encode('utf-8'),
            config_json.encode('utf-8'),
            data_client_handle,
            ctypes.byref(error)
        )
        self._check_error(error)
        if result != 0:
            raise ProphecyLibError(f"Read operation failed for gem: {gem_type}")

    def prophecy_write(self, gem_type: str, config_json: str, reader_handle: int) -> None:
        error = ctypes.c_char_p()
        result = self._lib.ProphecyWrite(
            gem_type.encode('utf-8'),
            config_json.encode('utf-8'),
            reader_handle,
            ctypes.byref(error)
        )
        self._check_error(error)
        if result != 0:
            raise ProphecyLibError(f"Write operation failed for gem: {gem_type}")

    def prophecy_transform(self, gem_type: str, config_json: str, reader_handle: int, data_client_handle: int) -> None:
        error = ctypes.c_char_p()
        result = self._lib.ProphecyTransform(
            gem_type.encode('utf-8'),
            config_json.encode('utf-8'),
            reader_handle,
            data_client_handle,
            ctypes.byref(error)
        )
        self._check_error(error)
        if result != 0:
            raise ProphecyLibError(f"Transform operation failed for gem: {gem_type}")

    def create_memfd_from_reader(self, reader_handle: int) -> int:
        error = ctypes.c_char_p()
        fd = self._lib.CreateMemfdFromReader(
            reader_handle,
            ctypes.byref(error)
        )
        self._check_error(error)
        if fd < 0:
            raise ProphecyLibError("Failed to create memfd from reader")
        return fd

    def populate_writer_from_memfd(self, writer_handle: int, fd: int) -> None:
        error = ctypes.c_char_p()
        result = self._lib.PopulateWriterFromMemfd(
            writer_handle,
            fd,
            ctypes.byref(error)
        )
        self._check_error(error)
        if result != 0:
            raise ProphecyLibError("Failed to populate writer from memfd")

    def close_data_client(self, data_client_handle: int) -> None:
        error = ctypes.c_char_p()
        result = self._lib.CloseDataClient(
            data_client_handle,
            ctypes.byref(error)
        )
        self._check_error(error)
        if result != 0:
            raise ProphecyLibError("Failed to close data client")

    def get_data_client_info(self, data_client_handle: int) -> str:
        error = ctypes.c_char_p()
        info_ptr = self._lib.GetDataClientInfo(
            data_client_handle,
            ctypes.byref(error)
        )
        self._check_error(error)
        if not info_ptr:
            raise ProphecyLibError("Failed to get data client info")
        
        info_str = info_ptr.decode('utf-8')
        self._lib.FreeString(info_ptr)
        return info_str

    def add_reader_to_data_client(self, data_client_handle: int, reader_index: int) -> int:
        error = ctypes.c_char_p()
        handle = self._lib.AddReaderToDataClient(
            data_client_handle,
            reader_index,
            ctypes.byref(error)
        )
        self._check_error(error)
        if handle < 0:
            raise ProphecyLibError(f"Failed to add reader at index {reader_index}")
        return handle

    def get_prophecy_secret(self, scope: str, name: str) -> str:
        """Fetch a prophecy secret from the Go secret vault"""
        error = ctypes.c_char_p()
        result = self._lib.GetProphecySecret(
            scope.encode('utf-8'),
            name.encode('utf-8'),
            ctypes.byref(error)
        )
        self._check_error(error)
        if not result:
            raise ProphecyLibError(f"Failed to get prophecy secret: scope={scope}, name={name}")
        
        # Decode and free the string
        secret_value = result.decode('utf-8')
        self._lib.FreeString(result)
        return secret_value

_lib_instance: Optional[ProphecyLib] = None

def load_lib() -> ProphecyLib:
    global _lib_instance
    if _lib_instance is None:
        _lib_instance = ProphecyLib()
    return _lib_instance

