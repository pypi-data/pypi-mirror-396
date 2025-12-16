from typing import Unpack, Callable, Iterable, Generic, TypeVar
from ..widgets.table import table as tableWidget, tableRow, TableWidgetKwargs
from ..widgets import button as buttonWidget
from enum import Enum
from decimal import Decimal


T = TypeVar('T')
class TableProxy(Generic[T]):
    
    STORED_ACTIONS = {
        "remove": lambda helper, obj: helper.remove(obj)
    }
    
    def __init__(
        self,
        pk: str,
        field_mapping: dict[str, str], *,
        actions: dict[str, Callable[['TableProxy', T], None] | str] = None,
        initial: Iterable[T] = None,
        handle_remove: Callable[[T], None] = None,
        **kwargs: Unpack[TableWidgetKwargs]
    ) -> None:
        self.__pk: int = pk
        self.__pk_stack = []
        self.__mapping = field_mapping
        self.__actions = actions
        self.__on_remove = handle_remove
        columns = list(field_mapping.values())
        if actions:
            for name, handler in actions.items():
                if isinstance(handler, str):
                    actions[name] = self.STORED_ACTIONS[handler]
                columns.append("")
                
        self.__widget = tableWidget(**kwargs, horizontalHeaderLabels=columns)
        if initial:
            self.extend(initial)

    @property
    def widget(self):
        return self.__widget
    
    def __validate_pk(self, obj: T):
        if not hasattr(obj, self.__pk):
            raise ValueError(f"Object '{obj.__class__.__name__}' has no pk attribute '{self.__pk}'")
        
        pk = getattr(obj, self.__pk)
        if not isinstance(pk, (int, float, str)):
            raise ValueError(f"Object '{obj.__class__.__name__}' pk attribute '{self.__pk}' bad type")
        return pk
    
    def extend(self, objs: Iterable[T]):
        for obj in objs:
            self.add(obj)
    
    def add(self, obj: T):
        pk = self.__validate_pk(obj)
        if pk in self.__pk_stack:
            return obj

        cells = []
        for name in self.__mapping.keys():
            if not hasattr(obj, name):
                raise ValueError(f"Object '{obj.__class__.__name__}' has no attribute '{name}'")
            value = getattr(obj, name)
            if isinstance(value, (int, float, Decimal, bool)):
                value = str(value)
            elif isinstance(value, Enum):
                if isinstance(value, str):
                    value = value.value
                else:
                    value = value.name
            
            cells.append(value if isinstance(value, str) else None)
        
        if self.__actions:
            for name, handler in self.__actions.items():
                cells.append(buttonWidget(text=name, onClicked=lambda _: handler(self, obj)))
        
        tableRow(self.__widget, *cells)
        self.__pk_stack.append(pk)
        return obj
    
    def remove(self, obj: T):
        pk = self.__validate_pk(obj)
        index = self.__pk_stack.index(pk)
        self.__widget.removeRow(index)
        self.__pk_stack.pop(index)
        if self.__on_remove:
            self.__on_remove(obj)
        return obj

    def clear(self):
        self.__widget.clear()
        self.__pk_stack.clear()
