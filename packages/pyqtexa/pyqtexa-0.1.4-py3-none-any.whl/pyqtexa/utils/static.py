import sys, inspect
from pathlib import Path
from .property import classproperty


class AppStatic:
    __is_executable: bool = getattr(sys, 'frozen', False)
    __base_path: Path = None
    __assets_path: Path = None
    __data_path: Path = None
    
    @classmethod
    def init(
        cls, *,
        datapath: bool | str = False,
        assets_folder: str = "assets",
        _pick_step: int = 0,
    ):
        assert cls.__base_path is None, "Action allowed only once!"
        assert _pick_step in range(0, 5), "Not too more"
        
        if cls.is_executable:
            cls.__base_path = Path(sys.executable).absolute().parent
            cls.__assets_path = Path(sys._MEIPASS, assets_folder).absolute()
        else:
            stack = inspect.stack()
            cls.__base_path = Path(str(stack[_pick_step+1][1])).absolute().parent
            cls.__assets_path = cls.__base_path / assets_folder

        if datapath:
            cls.__data_path = cls.__base_path / (datapath if isinstance(datapath, str) else "_data")
            if not cls.__data_path.exists():
                cls.__data_path.mkdir(parents=True, exist_ok=True)

    def __init__(self) -> None:
        raise Exception("Not supported, use 'init'")
    
    @classproperty
    def is_executable(cls):
        return cls.__is_executable

    @classproperty
    def base_path(cls):
        return cls.__base_path
    
    @classproperty
    def assets_path(cls):
        return cls.__assets_path
    
    @classproperty
    def data_path(cls):
        assert cls.__data_path, "Data directory not ininitialized!"
        return cls.__data_path
