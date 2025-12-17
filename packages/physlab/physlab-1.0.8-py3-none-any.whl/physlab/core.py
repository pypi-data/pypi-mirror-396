import numpy as np
import math
import re
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from typing import Union, List, Tuple, Any, Callable
from enum import Enum

class DataType(Enum):
    SCALAR = "scalar"
    VECTOR = "vector"

class DataWrapper:
    """Универсальная обертка для данных разных типов"""
    
    def __init__(self, data: Any):
        self.original = data
        self.type = self._classify_data(data)
        self.values, self.errors = self._normalize_data(data)
    
    def _classify_data(self, data: Any) -> DataType:
        if isinstance(data, phys):
            if data._is_array():
                return DataType.VECTOR
            else:
                return DataType.SCALAR
        elif isinstance(data, (list, tuple, np.ndarray)):
            if len(data) == 0:
                return DataType.SCALAR
                
            # Если это список phys-объектов, проверяем что все скаляры
            if isinstance(data[0], phys):
                if all(not item._is_array() for item in data):
                    # Список phys-скаляров -> создаем phys-вектор
                    return DataType.VECTOR
                else:
                    # Нашли phys-вектор в списке - это не поддерживается в операциях
                    raise ValueError(
                        "Операции с массивами векторов не поддерживаются в классе phys. "
                        "Используйте LabProcessor или graph для работы с массивами векторов."
                    )
            else:
                # Обычный массив чисел
                try:
                    float(data[0])
                    return DataType.VECTOR
                except (TypeError, ValueError):
                    raise ValueError("Неподдерживаемый тип данных для операций phys")
        else:
            try:
                float(data)
                return DataType.SCALAR
            except (TypeError, ValueError):
                raise ValueError(f"Неподдерживаемый тип данных: {type(data)}")
    
    def _normalize_data(self, data: Any) -> Tuple[np.ndarray, np.ndarray]:
        if isinstance(data, phys):
            if data._is_array():
                return data._value.copy(), data._abs_err.copy()
            else:
                return np.array([data._value]), np.array([data._abs_err])
        elif isinstance(data, (list, tuple, np.ndarray)):
            if len(data) == 0:
                return np.array([]), np.array([])
                
            if isinstance(data[0], phys):
                # Список phys-скаляров -> создаем вектор
                values = np.array([item._value for item in data])
                errors = np.array([item._abs_err for item in data])
                return values, errors
            else:
                # Обычный массив чисел
                return np.array(data), np.zeros_like(data)
        else:
            # Скаляр
            return np.array([float(data)]), np.array([0.0])
    
    def to_phys(self) -> 'phys':
        """Преобразует обратно в phys объект"""
        if self.type == DataType.SCALAR:
            return phys(self.values[0], self.errors[0])
        else:  # VECTOR
            return phys(self.values, self.errors)

class OperationDispatcher:
    """Диспетчер для обработки операций с разными типами данных"""
    
    @staticmethod
    def dispatch_operation(operation_func: Callable, *args) -> 'phys':
        """
        Универсальный диспетчер операций
        
        Parameters:
        -----------
        operation_func : Callable
            Функция операции, принимающая values и errors и возвращающая (new_values, new_errors)
        *args : Any
            Аргументы для операции (phys объекты, числа, массивы)
            
        Returns:
        --------
        phys
            Результат операции как phys объект
        """
        wrappers = [DataWrapper(arg) for arg in args]
        result_type = OperationDispatcher._determine_result_type(wrappers)
        
        if result_type == DataType.SCALAR:
            return OperationDispatcher._process_scalar_operation(operation_func, wrappers)
        else:  # VECTOR
            return OperationDispatcher._process_vector_operation(operation_func, wrappers)
    
    @staticmethod
    def _determine_result_type(wrappers: List[DataWrapper]) -> DataType:
        """Определяет тип результата - если есть хотя бы один вектор, результат вектор"""
        for wrapper in wrappers:
            if wrapper.type == DataType.VECTOR:
                return DataType.VECTOR
        return DataType.SCALAR
    
    @staticmethod
    def _process_scalar_operation(operation_func: Callable, wrappers: List[DataWrapper]) -> 'phys':
        """Обработка скалярных операций"""
        values = [w.values[0] for w in wrappers]
        errors = [w.errors[0] for w in wrappers]
        new_value, new_error = operation_func(values, errors)
        return phys(new_value, new_error)
    
    @staticmethod
    def _process_vector_operation(operation_func: Callable, wrappers: List[DataWrapper]) -> 'phys':
        """Обработка векторных операций с broadcast"""
        # Находим максимальную длину с учетом broadcast
        lengths = []
        for wrapper in wrappers:
            if wrapper.type == DataType.SCALAR:
                lengths.append(1)
            else:
                lengths.append(len(wrapper.values))
        
        max_len = max(lengths) if lengths else 1
        
        # Подготавливаем данные с broadcast
        prepared_values = []
        prepared_errors = []
        
        for wrapper in wrappers:
            if wrapper.type == DataType.SCALAR:
                # Скаляр -> повторяем до max_len
                prepared_values.append(np.full(max_len, wrapper.values[0]))
                prepared_errors.append(np.full(max_len, wrapper.errors[0]))
            else:
                current_len = len(wrapper.values)
                if current_len == 1:
                    # Вектор длины 1 -> повторяем до max_len
                    prepared_values.append(np.full(max_len, wrapper.values[0]))
                    prepared_errors.append(np.full(max_len, wrapper.errors[0]))
                elif current_len == max_len:
                    # Вектор подходящей длины
                    prepared_values.append(wrapper.values)
                    prepared_errors.append(wrapper.errors)
                else:
                    raise ValueError(f"Несовместимые размеры массивов: {current_len} != {max_len}")
        
        # Выполняем операции поэлементно
        result_values = []
        result_errors = []
        
        for i in range(max_len):
            elem_values = [arr[i] for arr in prepared_values]
            elem_errors = [arr[i] for arr in prepared_errors]
            
            new_val, new_err = operation_func(elem_values, elem_errors)
            result_values.append(new_val)
            result_errors.append(new_err)
        
        return phys(np.array(result_values), np.array(result_errors))
        
class phys:
    """
    Класс для работы с физическими величинами и их погрешностями.
    Поддерживает как скаляры, так и массивы NumPy.
    """
    
    def __init__(self, value, abs_err=0.0):
        # Преобразуем в numpy array если передан список/массив
        if isinstance(value, (list, tuple, np.ndarray)):
            self._value = np.array(value, dtype=float)
            # Если abs_err - число, создаём массив такой же длины
            if isinstance(abs_err, (int, float)):
                self._abs_err = np.full_like(self._value, float(abs_err))
            else:
                self._abs_err = np.array(abs_err, dtype=float)
        else:
            self._value = float(value)
            self._abs_err = float(abs_err)
        
        self._dispatcher = OperationDispatcher()
    
    # ==================== УНИВЕРСАЛЬНЫЕ ОПЕРАЦИИ ====================
    
    def _universal_operation(self, other, value_func, error_func):
        """Универсальный метод для бинарных операций с улучшенной обработкой ошибок"""
        def operation_func(values, errors):
            try:
                new_value = value_func(values[0], values[1])
                
                # Обработка специальных случаев для погрешностей
                with np.errstate(divide='ignore', invalid='ignore'):
                    new_error = error_func(errors[0], errors[1], values[0], values[1])
                
                # Замена inf и nan на разумные значения
                if np.isscalar(new_error):
                    if np.isinf(new_error) or np.isnan(new_error):
                        # Для проблемных случаев используем консервативную оценку
                        new_error = abs(new_value) * 0.1  # 10% по умолчанию
                else:
                    new_error = np.where(np.isinf(new_error) | np.isnan(new_error), 
                                       abs(new_value) * 0.1, new_error)
                
                return new_value, new_error
            except Exception as e:
                # Резервная стратегия при ошибках
                new_value = value_func(values[0], values[1])
                new_error = abs(new_value) * 0.1  # Консервативная оценка 10%
                return new_value, new_error
        
        return self._dispatcher.dispatch_operation(operation_func, self, other)
    
    def _universal_unary_operation(self, value_func, error_func):
        """Универсальный метод для унарных операций с улучшенной обработкой ошибок"""
        def operation_func(values, errors):
            try:
                new_value = value_func(values[0])
                
                with np.errstate(divide='ignore', invalid='ignore'):
                    new_error = error_func(errors[0], values[0])
                
                # Обработка проблемных значений погрешности
                if np.isscalar(new_error):
                    if np.isinf(new_error) or np.isnan(new_error):
                        new_error = abs(new_value) * 0.1
                else:
                    new_error = np.where(np.isinf(new_error) | np.isnan(new_error), 
                                       abs(new_value) * 0.1, new_error)
                
                return new_value, new_error
            except Exception as e:
                new_value = value_func(values[0])
                new_error = abs(new_value) * 0.1
                return new_value, new_error
        
        return self._dispatcher.dispatch_operation(operation_func, self)
    
    # ==================== МАТЕМАТИЧЕСКИЕ ОПЕРАЦИИ ====================
    
    # Сложение
    def __add__(self, other):
        def value_func(a, b): return a + b
        def error_func(sa, sb, a, b): 
            if isinstance(other, phys):
                return np.sqrt(sa**2 + sb**2)
            else:
                return sa
        return self._universal_operation(other, value_func, error_func)
    
    def __radd__(self, other):
        return self.__add__(other)
    
    # Вычитание
    def __sub__(self, other):
        def value_func(a, b): return a - b
        def error_func(sa, sb, a, b):
            if isinstance(other, phys):
                return np.sqrt(sa**2 + sb**2)
            else:
                return sa
        return self._universal_operation(other, value_func, error_func)
    
    def __rsub__(self, other):
        def value_func(a, b): return b - a
        def error_func(sa, sb, a, b): return sa
        return self._universal_operation(other, value_func, error_func)
    
    # Умножение
    def __mul__(self, other):
        def value_func(a, b): return a * b
        def error_func(sa, sb, a, b):
            if isinstance(other, phys):
                eps1 = sa / np.abs(a) if a != 0 else (np.inf if sa != 0 else 0.0)
                eps2 = sb / np.abs(b) if b != 0 else (np.inf if sb != 0 else 0.0)
                new_eps = np.sqrt(eps1**2 + eps2**2)
                return np.abs(a * b) * new_eps
            else:
                return np.abs(sa * b)
        return self._universal_operation(other, value_func, error_func)
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    # Деление
    def __truediv__(self, other):
        def value_func(a, b): return a / b
        def error_func(sa, sb, a, b):
            if isinstance(other, phys):
                eps1 = sa / np.abs(a) if a != 0 else (np.inf if sa != 0 else 0.0)
                eps2 = sb / np.abs(b) if b != 0 else (np.inf if sb != 0 else 0.0)
                new_eps = np.sqrt(eps1**2 + eps2**2)
                return np.abs(a / b) * new_eps
            else:
                return np.abs(sa / b)
        return self._universal_operation(other, value_func, error_func)
    
    def __rtruediv__(self, other):
        def value_func(a, b): return b / a
        def error_func(sa, sb, a, b): return np.abs(b * sa / (a**2))
        return self._universal_operation(other, value_func, error_func)
    
    # Возведение в степень
    def __pow__(self, power):
        def value_func(a, b): return a ** b
        def error_func(sa, sb, a, b):
            # Для a^b
            if a <= 0:
                return np.inf
            term1 = (np.log(a) * (a**b) * sb) ** 2
            term2 = (b * (a**b) * sa / a) ** 2
            return np.sqrt(term1 + term2)
        
        if isinstance(power, phys):
            return self._universal_operation(power, value_func, error_func)
        else:
            # Если power - обычное число
            def value_func_num(a): return a ** power
            def error_func_num(sa, a):
                if a <= 0:
                    return np.inf
                return abs(power) * (a ** (power - 1)) * sa
            return self._universal_unary_operation(value_func_num, error_func_num)
    
    def __rpow__(self, other):
        """Обработка случая: number ** phys"""
        def value_func(a, b): return a ** b
        def error_func(sa, sb, a, b):
            if a <= 0:
                return np.inf
            result_value = a ** b
            return abs(np.log(a) * result_value * sb)
        
        return self._universal_operation(other, value_func, error_func)
    
    # ==================== СУЩЕСТВУЮЩИЕ МЕТОДЫ (сохраняем API) ====================
    
    @staticmethod
    def concatenate(phys_objects):
        """Создает phys-массив из списка phys-скаляров."""
        if not isinstance(phys_objects, (list, tuple)):
            raise ValueError("Необходимо передать список или кортеж phys-объектов")
        
        if not all(isinstance(item, phys) for item in phys_objects):
            raise ValueError("Все элементы списка должны быть объектами phys")
        
        if not all(not item._is_array() for item in phys_objects):
            raise ValueError("Все phys-объекты должны быть скалярами")
        
        # Извлекаем значения и погрешности
        values = [item._value for item in phys_objects]
        errors = [item._abs_err for item in phys_objects]
        
        return phys(values, errors)
    
    def __iter__(self):
        """Поддержка распаковки: a, b, c = *phys_array"""
        if not self._is_array():
            yield self
            return
        
        for i in range(len(self._value)):
            yield phys(self._value[i], self._abs_err[i])
    
    def append(self, other):
        """Добавляет элемент в конец phys-массива."""
        if isinstance(other, phys):
            if not other._is_array():
                other_value = other._value
                other_error = other._abs_err
            else:
                if len(other._value) != 1:
                    raise ValueError("Можно добавлять только скаляры или phys-объекты с одним элементом")
                other_value = other._value[0]
                other_error = other._abs_err[0]
        elif isinstance(other, (int, float)):
            other_value = float(other)
            other_error = 0.0
        else:
            raise TypeError("Можно добавлять только phys-объекты или числа")
        
        if not self._is_array():
            self._value = np.array([self._value, other_value])
            self._abs_err = np.array([self._abs_err, other_error])
        else:
            self._value = np.append(self._value, other_value)
            self._abs_err = np.append(self._abs_err, other_error)
    
    @property
    def value(self):
        return self._value
    
    @property
    def sigma(self):
        return self._abs_err
    
    @sigma.setter
    def sigma(self, abs_err):
        if isinstance(self._value, np.ndarray):
            if isinstance(abs_err, (int, float)):
                self._abs_err = np.full_like(self._value, float(abs_err))
            else:
                self._abs_err = np.array(abs_err, dtype=float)
        else:
            self._abs_err = float(abs_err)
    
    @property
    def eps(self):
        if isinstance(self._value, np.ndarray):
            with np.errstate(divide='ignore', invalid='ignore'):
                eps_array = np.where(self._value == 0, 
                                   np.where(self._abs_err != 0, np.inf, 0.0),
                                   self._abs_err / np.abs(self._value))
            return eps_array
        else:
            if self._value == 0:
                return float('inf') if self._abs_err != 0 else 0.0
            return self._abs_err / abs(self._value)
    
    @eps.setter
    def eps(self, rel_err):
        if isinstance(self._value, np.ndarray):
            if isinstance(rel_err, (int, float)):
                rel_err_array = np.full_like(self._value, float(rel_err))
            else:
                rel_err_array = np.array(rel_err, dtype=float)
            self._abs_err = rel_err_array * np.abs(self._value)
        else:
            self._abs_err = float(rel_err) * abs(self._value)
    
    def _is_array(self):
        return isinstance(self._value, np.ndarray)
    
    def sort(self):
        if not self._is_array():
            return phys(self._value, self._abs_err)
        
        sorted_indices = np.argsort(self._value)
        sorted_value = self._value[sorted_indices]
        sorted_abs_err = self._abs_err[sorted_indices]
        sorted_obj = phys(sorted_value, sorted_abs_err)
        sorted_obj._sort_order = sorted_indices
        self._sort_order = sorted_indices
        return sorted_obj
        
    @property
    def sorted(self):
        return self.sort()
        
    @property
    def sort_order(self):
        self.sort()
        return getattr(self, '_sort_order', None)

    def in_order(self, order):
        if not self._is_array():
            raise ValueError("Метод in_order применим только к массивам")
        
        if isinstance(order, phys):
            if order.sort_order is None:
                raise ValueError("Переданный phys-объект не имеет sort_order")
            order_indices = order.sort_order
        elif isinstance(order, (list, tuple, np.ndarray)):
            order_indices = np.array(order)
        else:
            raise ValueError("order должен быть list, numpy.ndarray или phys-объектом")
        
        if len(order_indices) != len(self._value):
            raise ValueError("Размер order не совпадает с размером массива")
        
        if np.any(order_indices < 0) or np.any(order_indices >= len(self._value)):
            raise ValueError("Некорректные индексы в order")
        
        new_value = self._value[order_indices]
        new_abs_err = self._abs_err[order_indices]
        new_obj = phys(new_value, new_abs_err)
        new_obj._sort_order = order_indices
        return new_obj
        
    def __repr__(self):
        if self._is_array():
            return f"phys({self.value.tolist()}, {self.sigma.tolist()})"
        else:
            return f"phys({self.value}, {self.sigma})"
    
    def __str__(self):
        import inspect
        frame = inspect.currentframe()
        try:
            frames = inspect.getouterframes(frame)
            if len(frames) > 2:
                caller_frame = frames[2].frame
                local_vars = caller_frame.f_locals
                
                for name, obj in local_vars.items():
                    if obj is self:
                        if not name.startswith('_'):
                            return f"{name} = {self._format_value()}"
            
            return self._format_value()
        finally:
            del frame
        
    def _format_value(self):
        if self._is_array():
            if len(self._value.shape) == 1:
                return self._format_array_detailed()
            else:
                return f"phys(shape={self._value.shape})"
        else:
            return self._format_scalar()

    def _format_scalar(self):
        if self._abs_err == 0:
            if abs(self._value) < 1e-3 or abs(self._value) > 1e6:
                return f"{self._value:.4e}"
            return f"{self._value}"
        else:
            if abs(self._value) < 1e-3 or abs(self._value) > 1e6 or abs(self._abs_err) < 1e-3 or abs(self._abs_err) > 1e6:
                v_exp = int(np.floor(np.log10(abs(self._value)))) if self._value != 0 else 0
                v_coeff = self._value / (10 ** v_exp)
                s_coeff = self._abs_err / (10 ** v_exp)
                return f"{v_coeff:.4f}e{v_exp:+.0f} ± {s_coeff:.4f}e{v_exp:+.0f} (eps = {self.eps:.6f})"
            return f"{self._value:.6f} ± {self._abs_err:.6f} (eps = {self.eps:.6f})"

    def _format_array_detailed(self):
        formatted_elements = []
        for v, s in zip(self._value, self._abs_err):
            if s == 0:
                if abs(v) < 1e-3 or abs(v) > 1e6:
                    formatted = f"{v:.4e}"
                else:
                    formatted = f"{v}"
            else:
                eps_val = s / abs(v) if v != 0 else (np.inf if s != 0 else 0.0)
                if abs(v) < 1e-3 or abs(v) > 1e6 or abs(s) < 1e-3 or abs(s) > 1e6:
                    v_exp = int(np.floor(np.log10(abs(v)))) if v != 0 else 0
                    v_coeff = v / (10 ** v_exp)
                    s_coeff = s / (10 ** v_exp)
                    formatted = f"{v_coeff:.4f}e{v_exp:+.0f} ± {s_coeff:.4f}e{v_exp:+.0f} (eps = {eps_val:.6f})"
                else:
                    formatted = f"{v:.6f} ± {s:.6f} (eps = {eps_val:.6f})"
            formatted_elements.append(formatted)
        
        max_length = max(len(element) for element in formatted_elements)
        
        result = "[\n"
        for i, element in enumerate(formatted_elements):
            aligned_element = element.rjust(max_length)
            result += f"  {aligned_element}"
            if i < len(formatted_elements) - 1:
                result += ","
            result += "\n"
        result += "]"
        return result
    
    def __call__(self):
        return self._value
    
    def __float__(self):
        if self._is_array():
            if self._value.size == 1:
                return float(self._value.flat[0])
            raise ValueError("Нельзя преобразовать массив в float")
        return self._value
    
    def __int__(self):
        if self._is_array():
            if self._value.size == 1:
                return int(self._value.flat[0])
            raise ValueError("Нельзя преобразовать массив в int")
        return int(self._value)
    
    def __getitem__(self, index):
        if self._is_array():
            return phys(self._value[index], self._abs_err[index])
        else:
            if index == 0:
                return self
            raise IndexError("Скалярный phys имеет только один элемент")
    
    def __len__(self):
        if self._is_array():
            return len(self._value)
        else:
            return 1
    
    @property
    def shape(self):
        if self._is_array():
            return self._value.shape
        else:
            return ()

"""
Дополнительные математический функции для класса phys
"""

def cos(x):
    """Косинус с поддержкой phys объектов и универсальной обработкой типов"""
    def value_func(a): return np.cos(a)
    def error_func(sa, a): return np.abs(np.sin(a)) * sa
    
    if isinstance(x, phys):
        return x._universal_unary_operation(value_func, error_func)
    else:
        return np.cos(x)

def sin(x):
    """Синус с поддержкой phys объектов и универсальной обработкой типов"""
    def value_func(a): return np.sin(a)
    def error_func(sa, a): return np.abs(np.cos(a)) * sa
    
    if isinstance(x, phys):
        return x._universal_unary_operation(value_func, error_func)
    else:
        return np.sin(x)

def tg(x):
    """Тангенс с поддержкой phys объектов и универсальной обработкой типов"""
    def value_func(a): return np.tan(a)
    def error_func(sa, a): return np.abs(1.0 / (np.cos(a) ** 2)) * sa
    
    if isinstance(x, phys):
        return x._universal_unary_operation(value_func, error_func)
    else:
        return np.tan(x)

def ctg(x):
    """Котангенс с поддержкой phys объектов и универсальной обработкой типов"""
    return 1 / tg(x)

def exp(x):
    """Экспонента с улучшенной обработкой погрешностей"""
    def value_func(a): 
        return np.exp(a)
    def error_func(sa, a): 
        # σ_exp = exp(a) * σ_a
        return np.abs(np.exp(a)) * np.abs(sa)
    
    if isinstance(x, phys):
        return x._universal_unary_operation(value_func, error_func)
    else:
        return np.exp(x)

def ln(x):
    """Натуральный логарифм с улучшенной обработкой погрешностей"""
    def value_func(a): 
        if np.any(a <= 0):
            raise ValueError("Логарифм определен только для положительных чисел")
        return np.log(a)
    def error_func(sa, a): 
        # σ_ln = σ_a / a
        return np.abs(sa / a)
    
    if isinstance(x, phys):
        return x._universal_unary_operation(value_func, error_func)
    else:
        return np.log(x)

def log10(x):
    """Десятичный логарифм с улучшенной обработкой погрешностей"""
    def value_func(a): 
        if np.any(a <= 0):
            raise ValueError("Логарифм определен только для положительных чисел")
        return np.log10(a)
    def error_func(sa, a): 
        # σ_log10 = σ_a / (a * ln(10))
        return np.abs(sa / (a * np.log(10)))
    
    if isinstance(x, phys):
        return x._universal_unary_operation(value_func, error_func)
    else:
        return np.log10(x)

def sqrt(x):
    """Квадратный корень с улучшенной обработкой погрешностей"""
    def value_func(a): 
        if np.any(a < 0):
            raise ValueError("Квадратный корень определен только для неотрицательных чисел")
        return np.sqrt(a)
    def error_func(sa, a): 
        # σ_sqrt = σ_a / (2 * sqrt(a))
        return np.abs(sa / (2 * np.sqrt(a))) if a > 0 else 0.0
    
    if isinstance(x, phys):
        return x._universal_unary_operation(value_func, error_func)
    else:
        return np.sqrt(x)

def arcsin(x):
    """Арксинус с поддержкой phys объектов"""
    def value_func(a): 
        if np.any(np.abs(a) > 1):
            raise ValueError("Арксинус определен только для значений в диапазоне [-1, 1]")
        return np.arcsin(a)
    def error_func(sa, a): 
        # σ_arcsin = σ_a / sqrt(1 - a²)
        return np.abs(sa / np.sqrt(1 - a**2)) if np.abs(a) < 1 else np.inf
    
    if isinstance(x, phys):
        return x._universal_unary_operation(value_func, error_func)
    else:
        return np.arcsin(x)

def arccos(x):
    """Арккосинус с поддержкой phys объектов"""
    def value_func(a): 
        if np.any(np.abs(a) > 1):
            raise ValueError("Арккосинус определен только для значений в диапазоне [-1, 1]")
        return np.arccos(a)
    def error_func(sa, a): 
        # σ_arccos = σ_a / sqrt(1 - a²)  
        return np.abs(sa / np.sqrt(1 - a**2)) if np.abs(a) < 1 else np.inf
    
    if isinstance(x, phys):
        return x._universal_unary_operation(value_func, error_func)
    else:
        return np.arccos(x)

def arctg(x):
    """Арктангенс с поддержкой phys объектов"""
    def value_func(a): 
        return np.arctan(a)
    def error_func(sa, a): 
        # σ_arctan = σ_a / (1 + a²)
        return np.abs(sa / (1 + a**2))
    
    if isinstance(x, phys):
        return x._universal_unary_operation(value_func, error_func)
    else:
        return np.arctan(x)
          

class ErrorProcessor:
    """
    Обработчик погрешностей для МНК.
    Автоматически обрабатывает нулевые погрешности и нормализует веса.
    """
    
    @staticmethod
    def process_errors(values: np.ndarray, errors: np.ndarray = None, 
                      method: str = 'relative') -> np.ndarray:
        """
        Обрабатывает погрешности, заменяя нулевые на разумные значения.
        
        Parameters:
        -----------
        values : np.ndarray
            Значения данных
        errors : np.ndarray, optional
            Исходные погрешности
        method : str
            'relative' - использовать относительную погрешность для замены
            'std' - использовать стандартное отклонение
            
        Returns:
        --------
        np.ndarray
            Обработанные погрешности
        """
        if errors is None:
            # Если погрешности не заданы, оцениваем их
            if len(values) > 1:
                if method == 'std':
                    return np.std(values, ddof=1) * np.ones_like(values)
                else:
                    # relative method - 1% от среднего значения
                    mean_val = np.mean(np.abs(values))
                    return 0.01 * mean_val * np.ones_like(values)
            else:
                return np.zeros_like(values) if len(values) > 0 else np.array([0.0])
        
        # Создаем копию для избежания side effects
        processed_errors = errors.copy()
        
        # Заменяем нулевые и отрицательные погрешности
        zero_mask = (processed_errors <= 0) | np.isnan(processed_errors)
        if np.any(zero_mask):
            if method == 'std' and len(values) > 1:
                # Используем стандартное отклонение
                std_val = np.std(values[~zero_mask], ddof=1) if np.any(~zero_mask) else 1.0
                replacement = max(std_val, 1e-10)
            else:
                # Используем относительную погрешность (1%)
                mean_val = np.mean(np.abs(values)) if len(values) > 0 else 1.0
                replacement = max(0.01 * mean_val, 1e-10)
            
            processed_errors[zero_mask] = replacement
        
        return processed_errors
    
    @staticmethod
    def compute_weights(errors: np.ndarray) -> np.ndarray:
        """
        Вычисляет веса на основе погрешностей.
        
        Parameters:
        -----------
        errors : np.ndarray
            Погрешности данных
            
        Returns:
        --------
        np.ndarray
            Веса (обратно пропорциональны квадрату погрешностей)
        """
        if errors is None or len(errors) == 0:
            return None
            
        # Убеждаемся, что погрешности положительные
        positive_errors = np.maximum(errors, 1e-10)
        
        # Веса = 1 / σ²
        weights = 1.0 / (positive_errors ** 2)
        
        #Не нормализуем веса
        if np.sum(weights) > 0:
            pass #weights = weights / np.sum(weights)
        
        return weights
    
    @staticmethod
    def has_errors(errors: np.ndarray) -> bool:
        """
        Проверяет, есть ли ненулевые погрешности.
        """
        if errors is None:
            return False
        return np.any(errors > 1e-10)

class EnhancedLeastSquares:
    """
    Улучшенная реализация метода наименьших квадратов.
    Содержит статистически корректные формулы для различных случаев.
    """
    
    def __init__(self):
        self.error_processor = ErrorProcessor()
        
    def _select_method(self, x_err: np.ndarray, y_err: np.ndarray) -> str:
        """
        Автоматически выбирает метод МНК на основе погрешностей.
        """
        has_x_errors = self.error_processor.has_errors(x_err)
        has_y_errors = self.error_processor.has_errors(y_err)
        
        if not has_x_errors and not has_y_errors:
            return 'ols'
        elif has_y_errors and not has_x_errors:
            return 'wls_y'
        elif has_x_errors and not has_y_errors:
            return 'wls_x'
        else:
            return 'wls_xy'
    
    def _ordinary_least_squares(self, x: np.ndarray, y: np.ndarray) -> Tuple['phys', 'phys', dict]:
        """
        Улучшенный обычный МНК с правильными формулами погрешностей
        """
        n = len(x)
        
        if n < 2:
            raise ValueError("Для МНК нужно как минимум 2 точки")
        
        # Проверяем, не являются ли данные вырожденными
        x_range = np.max(x) - np.min(x)
        y_range = np.max(y) - np.min(y)
        
        if x_range < 1e-12:
            raise ValueError("Данные вырождены: все значения X одинаковые")
        
        if y_range < 1e-12:
            # Все y одинаковые - горизонтальная линия
            k_value = 0.0
            b_value = np.mean(y)
            # Погрешности на основе разброса данных
            if n > 1:
                sigma_y = np.std(y, ddof=1)
                sigma_k = sigma_y / (np.std(x, ddof=1) * np.sqrt(n)) if np.std(x, ddof=1) > 0 else float('inf')
                sigma_b = sigma_y / np.sqrt(n)
            else:
                sigma_k = 0.0
                sigma_b = 0.0
            
            stats = {'r_squared': 0.0, 'sigma_y': np.std(y) if n > 1 else 0.0, 'residuals': y - b_value}
            return phys(k_value, sigma_k), phys(b_value, sigma_b), stats
        
        # Используем центрированные данные для лучшей численной устойчивости
        x_mean = np.mean(x)
        y_mean = np.mean(y)
        x_centered = x - x_mean
        y_centered = y - y_mean
        
        # Вычисляем наклон через ковариацию
        covariance = np.sum(x_centered * y_centered)
        x_variance = np.sum(x_centered ** 2)
        
        if x_variance < 1e-15:
            k_value = 0.0
        else:
            k_value = covariance / x_variance
        
        b_value = y_mean - k_value * x_mean
        
        # Оценка погрешностей
        y_pred = k_value * x + b_value
        residuals = y - y_pred
        
        if n > 2:
            sigma2 = np.sum(residuals ** 2) / (n - 2)  # Несмещенная оценка
        else:
            sigma2 = np.var(residuals) if n > 1 else 0.0
        
        # Стандартные ошибки коэффициентов
        if x_variance > 0:
            sigma_k = np.sqrt(sigma2 / x_variance)
            sigma_b = np.sqrt(sigma2 * (1/n + x_mean**2 / x_variance))
        else:
            sigma_k = 0.0
            sigma_b = np.sqrt(sigma2 / n) if n > 0 else 0.0
        
        # Статистики
        ss_tot = np.sum((y - y_mean) ** 2)
        ss_res = np.sum(residuals ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        
        stats = {
            'r_squared': r_squared,
            'sigma_y': np.sqrt(sigma2) if sigma2 > 0 else 0.0,
            'residuals': residuals
        }
        
        return phys(k_value, sigma_k), phys(b_value, sigma_b), stats

    def _robust_ordinary_least_squares(self, x: np.ndarray, y: np.ndarray) -> Tuple['phys', 'phys', dict]:
        """
        Устойчивый МНК для численно нестабильных данных с использованием SVD.
        """
        n = len(x)
        
        try:
            # Используем SVD метод
            k_value, b_value = self._svd_least_squares(x, y)
            
            # Оценка погрешностей через остатки
            y_pred = k_value * x + b_value
            residuals = y - y_pred
            
            if n > 2:
                sigma2 = np.sum(residuals ** 2) / (n - 2)
            else:
                sigma2 = np.var(residuals) if n > 1 else 0.0
            
            # Для SVD оценка погрешностей сложнее, используем приближенные формулы
            x_mean = np.mean(x)
            x_variance = np.sum((x - x_mean) ** 2)
            
            if x_variance > 0 and n > 0:
                sigma_k = np.sqrt(sigma2 / x_variance)
                sigma_b = np.sqrt(sigma2 * (1/n + x_mean**2 / x_variance))
            else:
                sigma_k = 0.0
                sigma_b = np.sqrt(sigma2 / n) if n > 0 else 0.0
            
            # Статистики
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            ss_res = np.sum(residuals ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
            
            stats = {
                'r_squared': r_squared,
                'sigma_y': np.sqrt(sigma2) if sigma2 > 0 else 0.0,
                'residuals': residuals,
                'method': 'SVD'
            }
            
            return phys(k_value, sigma_k), phys(b_value, sigma_b), stats
            
        except Exception as e:
            # Аварийный возврат
            print(f"Ошибка в устойчивом МНК: {e}")
            return phys(0.0, float('inf')), phys(np.mean(y), float('inf')), {'error': str(e)}

    def _handle_degenerate_cases(self, x: np.ndarray, y: np.ndarray, 
                               x_err: np.ndarray = None, y_err: np.ndarray = None):
        """
        Обрабатывает вырожденные случаи: одна точка, вертикальная линия и т.д.
        """
        n = len(x)
        
        # Случай одной точки
        if n == 1:
            k_value = 0.0
            k_sigma = float('inf')  # Бесконечная погрешность - наклон не определен
            b_value = y[0]
            b_sigma = y_err[0] if y_err is not None and len(y_err) > 0 else float('inf')
            
            stats = {
                'r_squared': 0.0,
                'sigma_y': 0.0,
                'residuals': np.array([0.0]),
                'warning': 'Одна точка данных - наклон не определен'
            }
            return phys(k_value, k_sigma), phys(b_value, b_sigma), stats
        
        # Случай вертикальной линии (все x одинаковые)
        x_range = np.max(x) - np.min(x)
        if x_range < 1e-12:
            k_value = float('inf')  # Бесконечный наклон
            k_sigma = float('inf')
            b_value = np.mean(y)
            
            # Погрешность b на основе разброса y
            if n > 1:
                b_sigma = np.std(y, ddof=1) / np.sqrt(n)
            else:
                b_sigma = y_err[0] if y_err is not None and len(y_err) > 0 else float('inf')
            
            stats = {
                'r_squared': 0.0,
                'sigma_y': np.std(y) if n > 1 else 0.0,
                'residuals': y - b_value,
                'warning': 'Вертикальная линия - наклон бесконечен'
            }
            return phys(k_value, k_sigma), phys(b_value, b_sigma), stats
        
        # Если не вырожденный случай, возвращаем None
        return None

    def _svd_least_squares(self, x: np.ndarray, y: np.ndarray, weights: np.ndarray = None):
        """
        Устойчивое решение МНК через SVD разложение.
        """
        n = len(x)
        
        # Подготавливаем матрицу A
        if weights is not None:
            A = np.vstack([np.sqrt(weights) * x, np.sqrt(weights)]).T
            b_weighted = np.sqrt(weights) * y
        else:
            A = np.vstack([x, np.ones(n)]).T
            b_weighted = y
        
        # SVD разложение
        try:
            U, s, Vt = np.linalg.svd(A, full_matrices=False)
            
            # Регуляризация малых сингулярных чисел
            threshold = max(A.shape) * np.finfo(A.dtype).eps * s[0]
            s_inv = np.zeros_like(s)
            s_inv[s > threshold] = 1.0 / s[s > threshold]
            
            # Решение системы
            coeffs = Vt.T @ (s_inv * (U.T @ b_weighted))
            
            k = coeffs[0]
            b = coeffs[1]
            
            return k, b
            
        except np.linalg.LinAlgError:
            # Если SVD не удался, используем псевдообратную матрицу
            try:
                coeffs = np.linalg.pinv(A) @ b_weighted
                return coeffs[0], coeffs[1]
            except:
                # Последний резервный вариант
                return 0.0, np.mean(y)
     
    def _weighted_least_squares_y(self, x: np.ndarray, y: np.ndarray, 
                                y_err: np.ndarray) -> Tuple['phys', 'phys', dict]:
        """
        Взвешенный МНК с погрешностями по Y - ИСПРАВЛЕННАЯ ВЕРСИЯ
        """
        n = len(x)
        
        if n < 2:
            raise ValueError("Для МНК нужно как минимум 2 точки")
        
        # Вычисляем веса
        weights = self.error_processor.compute_weights(y_err)
        
        # Взвешенные суммы
        S = np.sum(weights)
        Sx = np.sum(weights * x)
        Sy = np.sum(weights * y)
        Sxx = np.sum(weights * x * x)
        Sxy = np.sum(weights * x * y)
        
        # Вычисляем коэффициенты
        denominator = S * Sxx - Sx ** 2
        if abs(denominator) < 1e-12:
            raise ValueError("Матрица системы вырождена")
        
        k = (S * Sxy - Sx * Sy) / denominator
        b = (Sxx * Sy - Sx * Sxy) / denominator
        
        # Предсказанные значения и остатки
        y_pred = k * x + b
        residuals = y - y_pred
        
        # Взвешенное стандартное отклонение остатков
        if n > 2:
            # sigma_y = sqrt( sum(w * residuals^2) / (n-2) )
            chi2 = np.sum(weights * residuals ** 2)
            sigma_y = np.sqrt(chi2 / (n - 2))
        else:
            sigma_y = 0.0
        
        # Стандартные ошибки коэффициентов - ИСПРАВЛЕННЫЕ ФОРМУЛЫ
        sigma_k = sigma_y * np.sqrt(S / denominator)
        sigma_b = sigma_y * np.sqrt(Sxx / denominator)
        
        # Статистики
        y_mean_weighted = np.average(y, weights=weights)
        ss_tot = np.sum(weights * (y - y_mean_weighted) ** 2)
        ss_res = np.sum(weights * residuals ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        
        # χ²
        chi2_value = np.sum((residuals / y_err) ** 2) if self.error_processor.has_errors(y_err) else 0.0
        
        stats = {
            'r_squared': r_squared,
            'chi2': chi2_value,
            'residuals': residuals,
            'weights': weights,
            'sigma_y': sigma_y
        }
        
        return phys(k, sigma_k), phys(b, sigma_b), stats
    
    def _weighted_least_squares_x(self, x: np.ndarray, y: np.ndarray,
                                x_err: np.ndarray) -> Tuple['phys', 'phys', dict]:
        """
        МНК с погрешностями по X - УЛУЧШЕННАЯ ВЕРСИЯ.
        """
        # Используем итеративный метод с лучшей сходимостью
        max_iterations = 10
        tolerance = 1e-6
        
        # Начальное приближение через обычный МНК
        k_current, b_current, _ = self._ordinary_least_squares(x, y)
        k_value = k_current.value
        b_value = b_current.value
        
        for iteration in range(max_iterations):
            # Проецируем погрешности по X на Y
            projected_y_err = np.abs(k_value) * x_err
            
            # Объединяем с погрешностями по Y (если они есть)
            total_y_err = projected_y_err  # В данном методе предполагаем, что y_err = 0
            
            # Взвешенный МНК с суммарными погрешностями
            weights = 1.0 / (total_y_err ** 2)
            
            # Взвешенные суммы
            S = np.sum(weights)
            Sx = np.sum(weights * x)
            Sy = np.sum(weights * y)
            Sxx = np.sum(weights * x * x)
            Sxy = np.sum(weights * x * y)
            
            denominator = S * Sxx - Sx ** 2
            if abs(denominator) < 1e-12:
                break
                
            k_new = (S * Sxy - Sx * Sy) / denominator
            b_new = (Sxx * Sy - Sx * Sxy) / denominator
            
            # Проверяем сходимость
            if abs(k_new - k_value) < tolerance and abs(b_new - b_value) < tolerance:
                break
                
            k_value = k_new
            b_value = b_new
        
        # Финальная оценка погрешностей
        y_pred = k_value * x + b_value
        residuals = y - y_pred
        
        if len(x) > 2:
            sigma2 = np.sum(residuals ** 2) / (len(x) - 2)
        else:
            sigma2 = np.var(residuals) if len(x) > 1 else 0.0
        
        # Используем финальные веса для оценки погрешностей
        final_projected_y_err = np.abs(k_value) * x_err
        final_weights = 1.0 / (final_projected_y_err ** 2)
        
        S_final = np.sum(final_weights)
        Sxx_final = np.sum(final_weights * x * x)
        denominator_final = S_final * Sxx_final - (np.sum(final_weights * x)) ** 2
        
        if denominator_final > 0:
            sigma_k = np.sqrt(S_final / denominator_final) * np.sqrt(sigma2)
            sigma_b = np.sqrt(Sxx_final / denominator_final) * np.sqrt(sigma2)
        else:
            sigma_k = 0.0
            sigma_b = 0.0
        
        stats = {
            'r_squared': 1 - np.sum(residuals**2) / np.sum((y - np.mean(y))**2) if len(y) > 1 else 0.0,
            'residuals': residuals,
            'iterations': iteration + 1
        }
        
        return phys(k_value, sigma_k), phys(b_value, sigma_b), stats
        
    def _total_least_squares(self, x: np.ndarray, y: np.ndarray,
                           x_err: np.ndarray, y_err: np.ndarray) -> Tuple['phys', 'phys', dict]:
        """
        Полный взвешенный МНК с погрешностями по X и Y.
        Используем итеративный метод.
        """
        # Первая итерация: взвешенный МНК только с погрешностями по Y
        k_first, b_first, stats_first = self._weighted_least_squares_y(x, y, y_err)
        
        # Проецируем погрешности по X на Y и объединяем
        projected_y_err = np.abs(k_first.value) * x_err
        total_y_err = np.sqrt(y_err ** 2 + projected_y_err ** 2)
        
        # Вторая итерация: взвешенный МНК с суммарными погрешностями
        return self._weighted_least_squares_y(x, y, total_y_err)

    def fit(self, x: np.ndarray, y: np.ndarray, 
            x_err: np.ndarray = None, y_err: np.ndarray = None,
            method: str = 'auto') -> Tuple['phys', 'phys', dict]:
        """
        Выполняет МНК с автоматическим выбором метода и обработкой вырожденных случаев.
        """
        # Проверяем и очищаем данные от NaN и Inf
        x_clean, y_clean, x_err_clean, y_err_clean = self._clean_data(x, y, x_err, y_err)
        
        # Сначала проверяем вырожденные случаи
        degenerate_result = self._handle_degenerate_cases(x_clean, y_clean, x_err_clean, y_err_clean)
        if degenerate_result is not None:
            return degenerate_result
        
        if len(x_clean) < 2:
            raise ValueError("После очистки от NaN/Inf осталось меньше 2 точек")
        
        # Обработка погрешностей
        x_err_processed = self.error_processor.process_errors(x_clean, x_err_clean)
        y_err_processed = self.error_processor.process_errors(y_clean, y_err_clean)
        
        # Автоматический выбор метода
        if method == 'auto':
            method = self._select_method(x_err_processed, y_err_processed)
        
        # Выполнение выбранного метода
        try:
            if method == 'ols':
                return self._ordinary_least_squares(x_clean, y_clean)
            elif method == 'wls_y':
                return self._weighted_least_squares_y(x_clean, y_clean, y_err_processed)
            elif method == 'wls_x':
                return self._weighted_least_squares_x(x_clean, y_clean, x_err_processed)
            elif method == 'wls_xy':
                return self._total_least_squares(x_clean, y_clean, x_err_processed, y_err_processed)
            else:
                raise ValueError(f"Неизвестный метод: {method}")
        except Exception as e:
            # Если метод падает, пробуем обычный МНК как запасной вариант
            print(f"Предупреждение: метод {method} не удался: {e}. Используется обычный МНК.")
            return self._ordinary_least_squares(x_clean, y_clean)
    
    def _clean_data(self, x: np.ndarray, y: np.ndarray, 
                   x_err: np.ndarray = None, y_err: np.ndarray = None):
        """
        Очищает данные от NaN и Inf значений.
        """
        # Создаем маску валидных точек
        valid_mask = np.isfinite(x) & np.isfinite(y)
        
        if x_err is not None:
            valid_mask = valid_mask & np.isfinite(x_err)
        if y_err is not None:
            valid_mask = valid_mask & np.isfinite(y_err)
        
        # Применяем маску
        x_clean = x[valid_mask]
        y_clean = y[valid_mask]
        
        x_err_clean = x_err[valid_mask] if x_err is not None else None
        y_err_clean = y_err[valid_mask] if y_err is not None else None
        
        # Предупреждение, если удалили точки
        n_removed = len(x) - len(x_clean)
        if n_removed > 0:
            print(f"Предупреждение: удалено {n_removed} точек с NaN/Inf значениями")
        
        return x_clean, y_clean, x_err_clean, y_err_clean

class LabProcessor:
    """
    Класс для обработки лабораторных работ с поддержкой физических величин.
    """
    

    def __init__(self):
        self.enhanced_ls = EnhancedLeastSquares()
    
    def weighted_least_squares(self, x, y, xerr=None, yerr=None):
        """
        Улучшенный взвешенный МНК с учётом погрешностей по x и y.
        """
        try:
            # Обрабатываем разные случаи входных данных
            if (self._is_array_of_phys_vectors(x) and self._is_array_of_phys_vectors(y) and 
                len(x) == len(y)):
                return self._process_vector_arrays(x, y, xerr, yerr)  # ДОБАВИЛИ xerr, yerr
            
            elif (self._is_array_of_phys_vectors(x) and self._is_phys_vector(y)):
                return self._process_mixed_vector_scalar(x, y, xerr, yerr, x_is_array=True)
            
            elif (self._is_phys_vector(x) and self._is_array_of_phys_vectors(y)):
                return self._process_mixed_vector_scalar(y, x, xerr, yerr, x_is_array=False)
            
            else:
                return self._core_least_squares(x, y, xerr, yerr)
                
        except Exception as e:
            print(f"Ошибка в МНК: {e}")
            import traceback
            traceback.print_exc()
            return None, None
    
    def _core_least_squares(self, x, y, xerr=None, yerr=None):
        """
        Единая надежная функция МНК с использованием новой системы.
        """
        # Извлекаем значения и погрешности
        x_data, x_sigma = self._extract_phys_data(x, xerr)
        y_data, y_sigma = self._extract_phys_data(y, yerr)
        
        # Проверяем данные
        try:
            self._validate_data(x_data, y_data, x_sigma, y_sigma)
        except ValueError as e:
            print(f"Ошибка валидации данных: {e}")
            return None, None
        
        # Используем улучшенный МНК
        try:
            k, b, stats = self.enhanced_ls.fit(x_data, y_data, x_sigma, y_sigma, method='auto')
            return k, b
        except Exception as e:
            print(f"Ошибка в EnhancedLeastSquares: {e}")
            return None, None
    
    @staticmethod
    def _is_phys_vector(obj):
        return isinstance(obj, phys) and obj._is_array()

    @staticmethod
    def _is_array_of_phys_vectors(obj):
        if not isinstance(obj, (list, tuple, np.ndarray)):
            return False
        if len(obj) == 0:
            return False
        return all(LabProcessor._is_phys_vector(item) for item in obj)


    def _process_vector_arrays(self, x_array, y_array, xerr=None, yerr=None):  # ДОБАВИЛИ АРГУМЕНТЫ
        """
        Обрабатывает массивы векторов.
        """
        k_results = []
        b_results = []
        
        for i, (x_vec, y_vec) in enumerate(zip(x_array, y_array)):
            try:
                if len(x_vec) != len(y_vec):
                    print(f"Предупреждение: длины векторов в паре {i} не совпадают: {len(x_vec)} != {len(y_vec)}")
                    continue
                
                k, b = self._core_least_squares(x_vec, y_vec, xerr, yerr)  # ПЕРЕДАЕМ xerr, yerr
                k_results.append(k)
                b_results.append(b)
            except Exception as e:
                print(f"Ошибка при обработке пары векторов {i}: {e}")
                # Добавляем None для сохранения порядка
                k_results.append(None)
                b_results.append(None)
        
        return k_results, b_results
        

    def _process_mixed_vector_scalar(self, array_side, scalar_side, xerr=None, yerr=None, x_is_array=True):
        """
        Обрабатывает смешанные типы данных.
        """
        k_results = []
        b_results = []
        
        for i, vec in enumerate(array_side):
            try:
                if len(vec) != len(scalar_side):
                    print(f"Предупреждение: длина вектора {i} ({len(vec)}) не совпадает с длиной скаляра ({len(scalar_side)})")
                    continue
                
                if x_is_array:
                    k, b = self._core_least_squares(vec, scalar_side, xerr, yerr)
                else:
                    k, b = self._core_least_squares(scalar_side, vec, xerr, yerr)
                
                k_results.append(k)
                b_results.append(b)
            except Exception as e:
                print(f"Ошибка при обработке элемента {i}: {e}")
                k_results.append(None)
                b_results.append(None)
        
        return k_results, b_results
        
    @staticmethod
    def weighted_mean(arr, err=None):
        """
        Вычисляет взвешенное среднее значение и его погрешность.
        ПРАВИЛЬНАЯ РЕАЛИЗАЦИЯ.
        """
        if not arr:
            raise ValueError("Пустой массив данных")
        
        # Извлекаем значения и погрешности из phys объектов
        if isinstance(arr[0], phys):
            values = np.array([x.value for x in arr])
            if err is None:
                errors = np.array([x.sigma for x in arr])
            else:
                errors = err
        else:
            values = np.array(arr)
            errors = err
        
        # Если погрешности не заданы, используем обычное среднее
        if errors is None:
            mean_val = np.mean(values)
            if len(values) > 1:
                sigma_mean = np.std(values, ddof=1) / np.sqrt(len(values))
            else:
                sigma_mean = 0.0
            return phys(mean_val, sigma_mean)
        
        # Нормализуем погрешности
        if isinstance(errors, (int, float, np.number)):
            errors = np.full_like(values, errors)
        elif isinstance(errors, (list, tuple)):
            errors = np.array(errors)
        
        # Убеждаемся, что все погрешности положительные
        errors = np.maximum(errors, 1e-10)  # Избегаем деления на ноль
        
        # Вычисляем веса
        weights = 1.0 / (errors ** 2)
        
        # Взвешенное среднее
        mean_val = np.sum(weights * values) / np.sum(weights)
        
        # Погрешность взвешенного среднего
        sigma_mean = 1.0 / np.sqrt(np.sum(weights))
        
        return phys(mean_val, sigma_mean)

    @staticmethod
    def _extract_phys_data(data, external_err):
        """Извлекает значения и погрешности из phys объектов или обычных данных"""
        if isinstance(data, phys):
            if data._is_array():
                # phys-массив
                values = data.value
                sigma = data.sigma if external_err is None else external_err
            else:
                # phys-скаляр
                values = np.array([data.value])
                sigma = np.array([data.sigma]) if external_err is None else np.array([external_err])
        elif isinstance(data, (list, tuple)) and len(data) > 0 and isinstance(data[0], phys):
            # Список phys-скаляров
            values = np.array([item.value for item in data])
            if external_err is None:
                sigma = np.array([item.sigma for item in data])
            else:
                sigma = external_err
        else:
            # Обычные числа или массивы
            values = np.array(data)
            sigma = external_err
        
        # Нормализуем сигмы
        if sigma is not None:
            if isinstance(sigma, (int, float, np.number)):
                sigma = np.full_like(values, sigma, dtype=float)
            elif isinstance(sigma, (list, tuple)):
                sigma = np.array(sigma)
            
            # Обработка двумерных погрешностей [lower, upper]
            if sigma.ndim == 2 and sigma.shape[0] == 2:
                sigma = (sigma[0] + sigma[1]) / 2
        
        return values, sigma

    @staticmethod
    def _validate_data(x, y, x_sigma, y_sigma):
        if len(x) != len(y):
            raise ValueError(f"Массивы x и y разной длины: {len(x)} != {len(y)}")
        
        if len(x) == 0:
            raise ValueError("Пустые массивы данных")
        
        if x_sigma is not None and len(x_sigma) != len(x):
            raise ValueError(f"Длина погрешностей x не совпадает с данными: {len(x_sigma)} != {len(x)}")
        
        if y_sigma is not None and len(y_sigma) != len(y):
            raise ValueError(f"Длина погрешностей y не совпадает с данными: {len(y_sigma)} != {len(y)}")

    @staticmethod
    def latex_table(data, header=None, first_column=None, hline_positions='all', 
                   alignment=None, caption='Таблица', orientation='horizontal', 
                   round_num=None, exp=False):
        """
        Генерирует код для таблицы в LaTeX на основе входного списка.
        Поддерживает phys объекты.
        """
        if not data:
            return ""

        # Преобразуем phys объекты в значения
        def extract_value(item):
            if isinstance(item, phys):
                return item.value
            return item

        # Рекурсивно обрабатываем данные
        def process_data(data_item):
            if isinstance(data_item, list):
                return [process_data(x) for x in data_item]
            elif isinstance(data_item, np.ndarray):
                return data_item.tolist()
            else:
                return extract_value(data_item)

        processed_data = process_data(data)
        
        # Если элементы - не списки, делаем их списками
        processed_data = [x if isinstance(x, list) else [x] for x in processed_data]

        # Определяем количество столбцов и строк
        if isinstance(processed_data[0], list):
            num_columns = len(processed_data[0])
            num_rows = len(processed_data)
        else:
            num_columns = 1
            num_rows = len(processed_data)

        if hline_positions == 'all':
            hline_positions = range(0, num_rows + 2)

        # Если задан first_column, увеличиваем количество столбцов на 1
        if first_column is not None:
            num_columns += 1

        # Определяем выравнивание столбцов
        if alignment is None:
            alignment = 'c' * num_columns
        elif len(alignment) != num_columns:
            raise ValueError("Количество символов в alignment должно соответствовать количеству столбцов")

        # Функция для форматирования чисел
        def format_number(value, round_digits=None, use_exp=False):
            if isinstance(value, (int, float)):
                if use_exp:
                    if round_digits is not None:
                        return f"{value:.{round_digits}e}"
                    else:
                        return f"{value:e}"
                else:
                    if round_digits is not None:
                        return f"{value:.{round_digits}f}"
                    else:
                        return str(value)
            else:
                return str(value)

        # Начинаем формировать таблицу
        latex_code = "\n\\begin{table}[H]\n\\centering\n\\begin{tabular}{|" + "|".join(alignment) + "|}\n"

        # Добавляем \hline в начале, если указано
        if hline_positions and 0 in hline_positions:
            latex_code += "\\hline\n"

        # Добавляем заголовок, если он есть
        if header:
            if orientation == 'horizontal':
                latex_code += " & ".join(map(str, header)) + " \\\\\n"
            elif orientation == 'vertical':
                for i, h in enumerate(header):
                    if first_column is not None:
                        latex_code += str(first_column[i]) + " & " + str(h) + " \\\\\n"
                    else:
                        latex_code += str(h) + " \\\\\n"
            if hline_positions and 1 in hline_positions:
                latex_code += "\\hline\n"

        # Добавляем строки данных
        if orientation == 'horizontal':
            for i, row in enumerate(processed_data):
                if not isinstance(row, list):
                    row = [row]

                # Добавляем первый элемент строки, если указано
                if first_column is not None:
                    row = [first_column[i]] + row

                # Определяем параметры округления и экспоненциального представления для текущей строки
                current_round = round_num[i] if isinstance(round_num, list) and i < len(round_num) else round_num
                current_exp = exp[i] if isinstance(exp, list) and i < len(exp) else exp

                # Форматируем числа в строке
                row = [format_number(x, current_round, current_exp) for x in row]

                latex_code += " & ".join(map(str, row)) + " \\\\\n"

                # Добавляем \hline, если указано
                if hline_positions and (i + 2) in hline_positions:
                    latex_code += "\\hline\n"
        elif orientation == 'vertical':
            for i in range(num_columns):
                row = []
                for j in range(num_rows):
                    if isinstance(processed_data[j], list):
                        row.append(processed_data[j][i])
                    else:
                        row.append(processed_data[j])

                # Добавляем первый элемент строки, если указано
                if first_column is not None:
                    row = [first_column[i]] + row

                # Определяем параметры округления и экспоненциального представления для текущей строки
                current_round = round_num[i] if isinstance(round_num, list) and i < len(round_num) else round_num
                current_exp = exp[i] if isinstance(exp, list) and i < len(exp) else exp

                # Форматируем числа в строке
                row = [format_number(x, current_round, current_exp) for x in row]

                latex_code += " & ".join(map(str, row)) + " \\\\\n"

                # Добавляем \hline, если указано
                if hline_positions and (i + 2) in hline_positions:
                    latex_code += "\\hline\n"

        # Завершаем таблицу
        latex_code += "\\end{tabular}\n\\caption{" + caption + "}\n\\end{table}"
        return LabProcessor.e_to_tex(latex_code, dollar=True)
    
    @staticmethod
    def latex_value(x, name='', sigma=None, eps=None, round_num=3, exp=False, dollar=True, mult=1):
        """
        Форматирует значение с погрешностью для вывода в LaTeX.
        Поддерживает phys объекты.
        """
        # Извлекаем значения из phys объекта
        if isinstance(x, phys):
            value = x.value
            if sigma is None:
                sigma = x.sigma
            if eps is None:
                eps = x.eps
        else:
            value = x
            
        if mult != 1:
            value = value / mult
            if sigma:
                sigma = sigma / mult
                
        # Функция для форматирования чисел
        def format_number(val, round_digits=None, use_exp=False):
            if isinstance(val, (int, float)):
                if use_exp:
                    if round_digits is not None:
                        return f"{val:.{round_digits}e}"
                    else:
                        return f"{val:e}"
                else:
                    if round_digits is not None:
                        return f"{val:.{round_digits}f}"
                    else:
                        return str(val)
            else:
                return str(val)
            
        output = name + ' = ' + ('( ' if sigma or eps else '') + format_number(value, round_num, exp)

        if sigma or eps:
            if sigma:
                output = output + ' \\pm ' + format_number(sigma, round_num, exp)
            elif eps:
                output = output + ' \\pm ' + format_number(eps * value, round_num, exp)
            output = output + ')'

        if mult != 1:
            output = output + LabProcessor.e_to_tex(str(mult), multiply=True)
        
        if dollar:
            output = '$' + output + '$ '
        
        return output
    
    @staticmethod
    def e_to_tex(input_string, dollar=False, multiply=False):
        """
        Преобразует числа в научной нотации (например, 1.23e-4) в формат LaTeX.
        """
        # Регулярное выражение для поиска чисел в научной нотации
        pattern = r'([+-]?\d*\.?\d+)[eE]([+-]?\d+)'
        
        # Функция для замены найденных чисел на тех-код
        def replace_with_tex(match):
            base = match.group(1)  # Основание числа
            if multiply and base == '1':
                base = ''
            exponent = match.group(2)# Экспонента
            exponent = exponent.lstrip('0') if not '-' in exponent else '-' + exponent.replace('-','').lstrip('0')
            if not exponent:  # Если экспонента состояла только из нулей
                exponent = '0'
            if multiply and base != "":
                dot_part = '{\\cdot'
            else:
                dot_part = ''

            expression = f'{dot_part}{base} \\cdot 10^{{{exponent}}}'

            if dollar:
                return f'${expression}$'
            else:
                return expression
            #return f '{"\\cdot" if (multiply and base != "") else ""}{base} \\cdot 10^{{{exponent}}}' if not dollar else '$' + f'{base} \\cdot 10^{{{exponent}}}' + '$'
        
        # Заменяем все вхождения чисел в научной нотации на тех-код
        result = re.sub(pattern, replace_with_tex, input_string)
        
        return result
'''        
    def old_graph(self, x, y, approx=True):
        import matplotlib.pyplot as plt
        import matplotlib.colors as mcolors
        plt.rcParams.update({'font.size': 14,
                             "pgf.preamble": "\\usepackage[utf8]{inputenc}\n\\usepackage[russian]{babel}\n\\usepackage{amsmath}"})
        plt.figure(figsize=(12, 7))
        plt.grid()
        colors = ['r', 'b', 'g', 'purple', 'y']   
        
        def is_phys_vector(obj):
            return isinstance(obj, phys) and obj._is_array()
        
        def is_array_of_phys(obj):
            if not isinstance(obj, (list, tuple, np.ndarray)) or len(obj) == 0:
                return False
            return all(isinstance(item, phys) for item in obj)
        
        def plot_approximation(x_vec, k, b, color='0.5', alpha=0.7):
            """Рисует аппроксимирующую прямую для одного вектора"""
            x_sorted = x_vec.sort()
            y_fit = k * x_sorted.value + b
            plt.plot(x_sorted.value, y_fit, '--', color=color, alpha=alpha)
        
        def plot_data_points(x_vec, y_vec, color_index=0, label=None):
            """Рисует экспериментальные точки для одной пары векторов"""
            plt.errorbar(
                x_vec.value, y_vec.value,
                xerr=x_vec.sigma,
                yerr=y_vec.sigma,
                ecolor=mcolors.to_rgba(colors[color_index % len(colors)], alpha=0.75),
                fmt='.',
                color=colors[color_index % len(colors)],
                capsize=4,
                label=label or f'Серия {color_index + 1}'
            )
        
        def process_vector_array_case(x_single, y_array):
            """Обрабатывает случай: x - единичный вектор, y - массив векторов"""
            k_array, b_array = self.weighted_least_squares(x_single, y_array)
            
            if approx:
                for i in range(len(y_array)):
                    k_val = k_array[i].value if hasattr(k_array, '__len__') and i < len(k_array) else k_array.value
                    b_val = b_array[i].value if hasattr(b_array, '__len__') and i < len(b_array) else b_array.value
                    plot_approximation(x_single, k_val, b_val)
            
            for i, y_vec in enumerate(y_array):
                plot_data_points(x_single, y_vec, i)
        
        def process_array_vector_case(x_array, y_single):
            """Обрабатывает случай: x - массив векторов, y - единичный вектор"""
            k_array, b_array = self.weighted_least_squares(x_array, y_single)
            
            if approx:
                for i, x_vec in enumerate(x_array):
                    k_val = k_array[i].value if hasattr(k_array, '__len__') and i < len(k_array) else k_array.value
                    b_val = b_array[i].value if hasattr(b_array, '__len__') and i < len(b_array) else b_array.value
                    plot_approximation(x_vec, k_val, b_val)
            
            for i, x_vec in enumerate(x_array):
                plot_data_points(x_vec, y_single, i)
        
        def process_array_array_case(x_array, y_array):
            """Обрабатывает случай: оба - массивы векторов одинаковой длины"""
            k_array, b_array = self.weighted_least_squares(x_array, y_array)
            
            if approx:
                for i, (x_vec, y_vec) in enumerate(zip(x_array, y_array)):
                    k_val = k_array[i].value if hasattr(k_array, '__len__') and i < len(k_array) else k_array.value
                    b_val = b_array[i].value if hasattr(b_array, '__len__') and i < len(b_array) else b_array.value
                    plot_approximation(x_vec, k_val, b_val)
            
            for i, (x_vec, y_vec) in enumerate(zip(x_array, y_array)):
                plot_data_points(x_vec, y_vec, i)
        
        def process_single_case(x_data, y_data):
            """Обрабатывает случай обычных данных или единичных phys-объектов"""
            # Извлекаем данные из phys объектов
            x_val = x_data.value if isinstance(x_data, phys) else np.array(x_data)
            y_val = y_data.value if isinstance(y_data, phys) else np.array(y_data)
            x_err = x_data.sigma if isinstance(x_data, phys) else None
            y_err = y_data.sigma if isinstance(y_data, phys) else None
            
            if (isinstance(x_val, np.ndarray) and isinstance(y_val, np.ndarray) and 
                len(x_val) == len(y_val)):
                
                # Аппроксимация
                if approx:
                    try:
                        k, b = self.weighted_least_squares(x_data, y_data)
                        if k is not None and b is not None:
                            x_sorted = np.sort(x_val)
                            y_fit = k.value * x_sorted + b.value
                            plt.plot(x_sorted, y_fit, 'r--', alpha=0.8, label='Аппроксимация')
                    except Exception as e:
                        print(f"Ошибка аппроксимации: {e}")
                
                # Экспериментальные точки
                plot_data_points_simple(x_val, y_val, x_err, y_err)
        
        def plot_data_points_simple(x_val, y_val, x_err=None, y_err=None, color_index=0, label='Эксперимент'):
            """Упрощенная версия для обычных данных"""
            plt.errorbar(
                x_val, y_val,
                xerr=x_err,
                yerr=y_err,
                ecolor=mcolors.to_rgba(colors[color_index], alpha=0.75),
                fmt='.',
                color=colors[color_index],
                capsize=4,
                label=label
            )
        
        # Основная логика выбора сценария
        x_is_phys_vector = is_phys_vector(x)
        y_is_phys_vector = is_phys_vector(y)
        x_is_array_of_phys = is_array_of_phys(x)
        y_is_array_of_phys = is_array_of_phys(y)
        
        if x_is_phys_vector and y_is_array_of_phys:
            process_vector_array_case(x, y)
        elif y_is_phys_vector and x_is_array_of_phys:
            process_array_vector_case(x, y)
        elif x_is_array_of_phys and y_is_array_of_phys and len(x) == len(y):
            process_array_array_case(x, y)
        else:
            process_single_case(x, y)
        
        plt.legend()
        plt.tight_layout()
        return plt
'''        

class graph:
    """
    Умный класс для построения научных графиков.
    
    Особенности:
    - Автоматическое определение типов данных
    - Умные настройки по умолчанию
    - Минимальный код для профессионального графика
    - Полная совместимость с matplotlib.pyplot
    """
    
    def __init__(self, x=None, y=None, approx=True, figsize=(12, 7), **kwargs):
        import matplotlib.pyplot as plt
        import matplotlib.colors as mcolors
        
        self.plt = plt
        self.mcolors = mcolors
        self.figsize = figsize
        
        # Умные настройки по умолчанию
        plt.rcParams.update({
            'font.size': 14,
            
            'mathtext.fontset': 'stix',
            'axes.grid': True,
            'grid.alpha': 0.3,
            'legend.frameon': True,
            'legend.framealpha': 0.9,
            'legend.edgecolor': 'black',
            "pgf.preamble": "\\usepackage[utf8]{inputenc}\n\\usepackage[russian]{babel}\n\\usepackage{amsmath}"
        })
        
        # Создание фигуры
        self.fig, self.ax = plt.subplots(figsize=figsize)
        
        # Умные цвета (цветовая палитра для научных графиков)
        self.color_cycle = [
            '#ff0000', '#1f77b4', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#ff7f0e', '#17becf'
        ]
        
        self.processor = LabProcessor()
        self.series_count = 0
        self.approx = approx
        self.k = None
        self.b = None
        
        # Автоматическое построение если переданы данные
        if x is not None and y is not None:
            self._auto_plot(x, y, approx, **kwargs)
    
    def _auto_plot(self, x, y, approx, **kwargs):
        """
        Автоматическое построение графика на основе типов данных.
        """
        # Определяем тип данных и строим соответствующий график
        data_type = self._classify_data(x, y)
        
        if data_type == "single_series":
            self._plot_single_series(x, y, approx, **kwargs)
        elif data_type == "multiple_series_y":
            self._plot_multiple_series_y(x, y, approx, **kwargs)
        elif data_type == "multiple_series_x":
            self._plot_multiple_series_x(x, y, approx, **kwargs)
        elif data_type == "paired_series":
            self._plot_paired_series(x, y, approx, **kwargs)
        else:
            self._plot_fallback(x, y, approx, **kwargs)
    
    def _classify_data(self, x, y):
        """
        Автоматически классифицирует тип данных для выбора стратегии построения.
        """
        def is_phys_vector(obj):
            return isinstance(obj, phys) and obj._is_array()
        
        def is_array_of_phys_vectors(obj):
            if not isinstance(obj, (list, tuple, np.ndarray)) or len(obj) == 0:
                return False
            return all(is_phys_vector(item) for item in obj)
        
        x_is_vector = is_phys_vector(x)
        y_is_vector = is_phys_vector(y)
        x_is_array = is_array_of_phys_vectors(x)
        y_is_array = is_array_of_phys_vectors(y)
        
        # Одна серия данных
        if (x_is_vector and y_is_vector) or (not x_is_array and not y_is_array):
            return "single_series"
        
        # Несколько серий Y при одном X
        elif x_is_vector and y_is_array:
            return "multiple_series_y"
        
        # Несколько серий X при одном Y  
        elif x_is_array and y_is_vector:
            return "multiple_series_x"
        
        # Парные серии (массивы векторов)
        elif x_is_array and y_is_array and len(x) == len(y):
            return "paired_series"
        
        else:
            return "fallback"
    
    def _plot_single_series(self, x, y, approx, **kwargs):
        """Построение одной серии данных."""
        color = self._get_next_color()
        label = kwargs.get('label', 'Экспериментальные данные')
        
        # Извлекаем данные
        x_data, x_err = self._extract_data(x)
        y_data, y_err = self._extract_data(y)
        
        # Строим точки
        self.ax.errorbar(
            x_data, y_data,
            xerr=x_err, yerr=y_err,
            fmt='o', markersize=6,
            color=color, alpha=0.8,
            capsize=4, capthick=1.5,
            label=label
        )
        
        # Аппроксимация
        if approx and len(x_data) >= 2:
            try:
                self.k, self.b = self.processor.weighted_least_squares(x, y)
                if self.k is not None and self.b is not None:
                    x_sorted = np.sort(x_data)
                    y_fit = self.k.value * x_sorted + self.b.value
                    
                    self.ax.plot(
                        x_sorted, y_fit,
                        '--', color=color, alpha=0.7, linewidth=2,
                        label=f'Аппроксимация (k={self.k.value:.3f})'
                    )
            except Exception as e:
                print(f"Предупреждение: аппроксимация не удалась: {e}")
    
    def _plot_multiple_series_y(self, x, y_arrays, approx, **kwargs):
        """Несколько серий Y при одном X."""
        x_data, x_err = self._extract_data(x)
        
        for i, y_item in enumerate(y_arrays):
            color = self._get_next_color()
            label = kwargs.get('label', f'Серия {i+1}')
            if isinstance(kwargs.get('labels'), (list, tuple)) and i < len(kwargs['labels']):
                label = kwargs['labels'][i]
            
            y_data, y_err = self._extract_data(y_item)
            
            self.ax.errorbar(
                x_data, y_data,
                xerr=x_err, yerr=y_err,
                fmt='o', markersize=5,
                color=color, alpha=0.7,
                capsize=3, label=label
            )
            
            # Аппроксимация для каждой серии
            if approx and len(x_data) >= 2:
                try:
                    k, b = self.processor.weighted_least_squares(x, y_item)
                    if k is not None and b is not None:
                        x_sorted = np.sort(x_data)
                        y_fit = k.value * x_sorted + b.value
                        
                        self.ax.plot(
                            x_sorted, y_fit,
                            '--', color=color, alpha=0.5, linewidth=1.5
                        )
                except Exception as e:
                    print(f"Предупреждение: аппроксимация серии {i+1} не удалась: {e}")
    
    def _plot_paired_series(self, x_arrays, y_arrays, approx, **kwargs):
        """Парные серии данных (массивы векторов)."""
        k_results = []
        b_results = []
        
        for i, (x_item, y_item) in enumerate(zip(x_arrays, y_arrays)):
            color = self._get_next_color()
            label = kwargs.get('label', f'Серия {i+1}')
            if isinstance(kwargs.get('labels'), (list, tuple)) and i < len(kwargs['labels']):
                label = kwargs['labels'][i]
            
            x_data, x_err = self._extract_data(x_item)
            y_data, y_err = self._extract_data(y_item)
            
            self.ax.errorbar(
                x_data, y_data,
                xerr=x_err, yerr=y_err,
                fmt='o', markersize=5,
                color=color, alpha=0.7,
                capsize=3, label=label
            )
            
            # Аппроксимация
            if approx and len(x_data) >= 2:
                try:
                    k, b = self.processor.weighted_least_squares(x_item, y_item)
                    if k is not None and b is not None:
                        k_results.append(k)
                        b_results.append(b)
                        
                        x_sorted = np.sort(x_data)
                        y_fit = k.value * x_sorted + b.value
                        
                        self.ax.plot(
                            x_sorted, y_fit,
                            '--', color=color, alpha=0.5, linewidth=1.5
                        )
                except Exception as e:
                    print(f"Предупреждение: аппроксимация серии {i+1} не удалась: {e}")
        
        if k_results and b_results:
            self.k = k_results
            self.b = b_results
    
    def _plot_fallback(self, x, y, approx, **kwargs):
        """Резервный метод построения."""
        print("Предупреждение: используется резервный метод построения")
        x_data, x_err = self._extract_data(x)
        y_data, y_err = self._extract_data(y)
        
        self.ax.errorbar(x_data, y_data, xerr=x_err, yerr=y_err, fmt='o')
        
        if approx and len(x_data) >= 2:
            try:
                self.k, self.b = self.processor.weighted_least_squares(x, y)
                if self.k is not None and self.b is not None:
                    x_sorted = np.sort(x_data)
                    y_fit = self.k.value * x_sorted + self.b.value
                    self.ax.plot(x_sorted, y_fit, 'r--', alpha=0.7)
            except Exception as e:
                print(f"Предупреждение: аппроксимация не удалась: {e}")
    
    def _extract_data(self, data):
        """Извлекает значения и погрешности из данных."""
        if isinstance(data, phys):
            if data._is_array():
                return data.value, data.sigma
            else:
                return np.array([data.value]), np.array([data.sigma])
        elif isinstance(data, (list, tuple, np.ndarray)):
            return np.array(data), None
        else:
            return np.array([float(data)]), None
    
    def _get_next_color(self):
        """Возвращает следующий цвет из цикла."""
        color = self.color_cycle[self.series_count % len(self.color_cycle)]
        self.series_count += 1
        return color
    
    # ==================== УМНЫЕ МЕТОДЫ ДЛЯ БЫСТРОГО ПОСТРОЕНИЯ ====================
    
    def style_scientific(self):
        """Применяет научный стиль в стиле LaTeX к графику."""
        # Настройки шрифтов для LaTeX-стиля
        plt.rcParams.update({'font.size': 14,
                     "pgf.preamble": "\\usepackage[utf8]{inputenc}\n\\usepackage[russian]{babel}\n\\usepackage{amsmath}"})
        
        # Настройки осей и сетки
        self.ax.minorticks_on()
        self.ax.tick_params(which='both', direction='in', top=True, right=True)
        self.ax.tick_params(which='major', length=6, width=1)
        self.ax.tick_params(which='minor', length=3, width=1)
        
        # Настройка сетки
        self.ax.grid(True, which='major', linestyle='-', alpha=0.3, linewidth=0.5)
        self.ax.grid(True, which='minor', linestyle=':', alpha=0.2, linewidth=0.5)
        
        # Настройка рамки
        for spine in self.ax.spines.values():
            spine.set_linewidth(1)
            spine.set_color('black')
        
        return self
    
    def auto_labels(self, xlabel=None, ylabel=None, title=None):
        """Автоматически устанавливает подписи если они не заданы."""
        if not hasattr(self, '_labels_set') or not self._labels_set:
            if xlabel:
                self.ax.set_xlabel(xlabel)
            if ylabel:
                self.ax.set_ylabel(ylabel)
            if title:
                self.ax.set_title(title)
            self._labels_set = True
        return self
    
    def auto_legend(self, **kwargs):
        """Автоматически добавляет легенду если есть метки."""
        if any(line.get_label() not in ['_nolegend_', 'Аппроксимация'] for line in self.ax.get_lines()):
            default_kwargs = {'loc': 'best', 'frameon': True, 'framealpha': 0.9}
            default_kwargs.update(kwargs)
            self.ax.legend(**default_kwargs)
        return self
    
    def add_stats(self, x=0.02, y=0.98, **kwargs):
        """Добавляет блок с параметрами аппроксимации."""
        if self.k is not None and self.b is not None:
            if isinstance(self.k, (list, tuple)):
                # Множественные коэффициенты
                stats_text = []
                for i, (k, b) in enumerate(zip(self.k, self.b)):
                    if k is not None and b is not None:
                        stats_text.append(
                            f"Серия {i+1}:\n"
                            f"k = {k.value:.4f} ± {k.sigma:.4f}\n"
                            f"b = {b.value:.4f} ± {b.sigma:.4f}"
                        )
                text = "\n\n".join(stats_text)
            else:
                # Одиночные коэффициенты
                text = (
                    f"Аппроксимация:\n"
                    f"k = {self.k.value:.4f} ± {self.k.sigma:.4f}\n"
                    f"b = {self.b.value:.4f} ± {self.b.sigma:.4f}"
                )
            
            bbox_props = dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8, edgecolor='gray')
            self.ax.text(x, y, text, transform=self.ax.transAxes, 
                        bbox=bbox_props, verticalalignment='top', fontsize=10)
        return self
    
    def quick_save(self, filename, subdir = '', format = 'pdf', dpi=300, **kwargs):
        """Быстрое сохранение графика с умными настройками."""
        
        
        if filename == '':
            if self.gca().get_title() != '':
                filename = self.gca().get_title()
            else:
                filename = 'Graph'

        fullname = f"{subdir}{'/' if subdir else ''}{filename}.{format}"
        print(fullname)
        #self.plt.tight_layout()
        
        #save_kwargs = {'dpi': dpi, 'bbox_inches': 'tight', 'facecolor': 'white'}
        #save_kwargs.update(kwargs)
        self.savefig(fullname, format = format, **kwargs)
        return self
    
    # ==================== СТАРЫЙ API ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ ====================
    
    def xlabel(self, label, **kwargs):
        self.ax.set_xlabel(label, **kwargs)
        return self  # Возвращаем self для цепочки

    def ylabel(self, label, **kwargs):
        self.ax.set_ylabel(label, **kwargs)
        return self

    def add_title(self, text, **kwargs):
        self.ax.set_title(text, **kwargs)
        return self
    
    def set_legend(self, labels=None, **kwargs):
        """Старый метод для обратной совместимости."""
        if labels is not None:
            # Обновляем метки линий
            lines = self.ax.get_lines()
            for i, line in enumerate(lines):
                if i < len(labels):
                    line.set_label(labels[i])
        
        self.auto_legend(**kwargs)
        return self
    
    def add_params_text(self, series_names=None, x=0.02, y=0.98, **kwargs):
        """Старый метод для обратной совместимости."""
        return self.add_stats(x=x, y=y, **kwargs)
    
    # ==================== ДЕЛЕГИРОВАНИЕ К MATPLOTLIB ====================
    
    def __getattr__(self, name):
        """
        Делегирует все вызовы к matplotlib.pyplot и axes.
        Это сохраняет полную совместимость со старым кодом.
        """
        # Сначала пробуем найти в axes
        if hasattr(self.ax, name):
            return getattr(self.ax, name)
        # Затем в pyplot
        elif hasattr(self.plt, name):
            return getattr(self.plt, name)
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

'''
class graph_old:
    """
    Класс для построения графиков с экспериментальными данными и их аппроксимацией.
    
    Автоматически обрабатывает различные форматы входных данных:
    - phys-векторы и массивы phys-векторов
    - обычные массивы чисел
    - поддерживает взвешенный метод наименьших квадратов для учёта погрешностей
    
    Особенности:
    - Автоматическое построение аппроксимирующих прямых
    - Учёт погрешностей измерений при построении графиков
    - Поддержка нескольких серий данных
    - Красивое оформление с настройкой стилей
    - Автоматический подбор размера крышечек для оптимального отображения
    """
    
    def __init__(self, x, y, approx=True):
        """
        Инициализация графика.
        
        Параметры:
        ----------
        x : phys, list, np.ndarray
            Данные по оси X. Может быть:
            - phys-вектор
            - массив phys-векторов  
            - обычный массив чисел
            
        y : phys, list, np.ndarray
            Данные по оси Y. Аналогично x.
            
        approx : bool, optional
            Выполнять ли аппроксимацию методом наименьших квадратов.
            По умолчанию True.
        """
        import matplotlib.pyplot as plt
        import matplotlib.colors as mcolors
        
        self.plt = plt
        self.mcolors = mcolors
        
        # Настройка стиля matplotlib для научных графиков
        self.plt.rcParams.update({
            'font.size': 14,
            "pgf.preamble": "\\usepackage[utf8]{inputenc}\n\\usepackage[russian]{babel}\n\\usepackage{amsmath}"
        })
        
        # Создание фигуры с заданным размером
        self.plt.figure(figsize=(12, 7))
        self.plt.grid()  # Включение сетки
        
        # Палитра цветов для разных серий данных (яркие цвета)
        self.colors = ['r', 'b', 'g', 'purple', 'y', 'pink', 'orange', 'cyan', 'magenta', 'lime', 
                      'teal', 'coral', 'gold', 'lightblue', 'darkred']
        self.k = None  # Коэффициенты наклона аппроксимирующих прямых
        self.b = None  # Коэффициенты смещения аппроксимирующих прямых
        
        # Строим график
        self._build_graph(x, y, approx)
    
    def _calculate_optimal_capsize(self, x_range, y_range, num_points, fig_size=(12, 7)):
        """
        Вычисляет оптимальный размер крышечек (capsize) на основе характеристик графика.
        
        Алгоритм основан на:
        - Размере фигуры
        - Диапазонах данных
        - Количестве точек
        
        Параметры:
        ----------
        x_range : float
            Диапазон данных по оси X (max - min)
        y_range : float
            Диапазон данных по оси Y (max - min)
        num_points : int
            Количество точек данных
        fig_size : tuple
            Размер фигуры в дюймах
            
        Возвращает:
        -----------
        float
            Оптимальный размер крышечек
        """
        # Базовый размер в пунктах (points)
        BASE_CAP_SIZE = 4.0
        
        # Корректировка на количество точек (меньше точек - больше крышечки)
        point_density_factor = max(0.5, min(2.0, 30.0 / num_points))
        
        # Корректировка на диапазон данных (меньший диапазон - больше крышечки)
        data_range = max(x_range, y_range)
        if data_range > 0:
            range_factor = max(0.3, min(3.0, 10.0 / data_range))
        else:
            range_factor = 1.0
        
        # Корректировка на размер фигуры
        fig_area = fig_size[0] * fig_size[1]
        size_factor = max(0.5, min(2.0, fig_area / 80.0))
        
        # Итоговый размер
        optimal_capsize = BASE_CAP_SIZE * point_density_factor * range_factor * size_factor
        
        # Ограничиваем разумными пределами
        return max(2.0, min(8.0, optimal_capsize))
    
    def _get_data_range(self, data):
        """
        Вычисляет диапазон данных для phys объектов или обычных массивов.
        """
        if isinstance(data, phys):
            values = data.value
        elif isinstance(data, (list, tuple, np.ndarray)) and len(data) > 0:
            if isinstance(data[0], phys):
                # Для массива phys объектов объединяем все значения
                all_values = []
                for item in data:
                    if hasattr(item, 'value'):
                        all_values.extend(np.array(item.value).flatten())
                values = np.array(all_values)
            else:
                values = np.array(data)
        else:
            values = np.array(data)
        
        if len(values) == 0:
            return 1.0  # Значение по умолчанию
        
        data_range = np.max(values) - np.min(values)
        return data_range if data_range > 0 else 1.0
    
    def _get_num_points(self, x, y):
        """
        Вычисляет общее количество точек данных.
        """
        def count_points(obj):
            if isinstance(obj, phys):
                return len(obj.value) if obj._is_array() else 1
            elif isinstance(obj, (list, tuple, np.ndarray)):
                if len(obj) == 0:
                    return 0
                if isinstance(obj[0], phys):
                    return sum(len(item.value) for item in obj)
                else:
                    return len(obj)
            else:
                return 1
        
        x_points = count_points(x)
        y_points = count_points(y)
        
        return max(x_points, y_points)
    
    def _calculate_adaptive_capsize(self, x, y):
        """
        Основной метод для расчета адаптивного размера крышечек.
        
        Комбинирует несколько стратегий для оптимального результата.
        """
        # Стратегия 1: на основе диапазона данных
        x_range = self._get_data_range(x)
        y_range = self._get_data_range(y)
        num_points = self._get_num_points(x, y)
        
        capsize1 = self._calculate_optimal_capsize(x_range, y_range, num_points)
        
        # Стратегия 2: на основе относительных погрешностей
        def get_avg_relative_error(data):
            """Вычисляет среднюю относительную погрешность."""
            if isinstance(data, phys):
                if data._is_array():
                    values = np.array(data.value)
                    errors = np.array(data.sigma)
                    with np.errstate(divide='ignore', invalid='ignore'):
                        relative_errors = np.where(values != 0, errors / np.abs(values), errors)
                    return np.nanmean(relative_errors)
                else:
                    return data.eps if hasattr(data, 'eps') else 0.0
            return 0.0
        
        x_error = get_avg_relative_error(x)
        y_error = get_avg_relative_error(y)
        avg_error = (x_error + y_error) / 2.0
        
        # Корректировка на погрешности (большие погрешности - большие крышечки)
        error_factor = 1.0 + min(2.0, avg_error * 10.0)  # 0-200% увеличение
        capsize2 = capsize1 * error_factor
        
        # Стратегия 3: на основе плотности точек
        density_factor = 1.0
        if num_points > 50:
            # Для очень плотных графиков уменьшаем крышечки
            density_factor = max(0.3, 50.0 / num_points)
        
        final_capsize = capsize2 * density_factor
        
        # Финальные ограничения
        return max(1.5, min(10.0, final_capsize))
    
    def _mix_with_gray(self, color, gray_factor=0.5):
        """
        Смешивает цвет с серым для создания приглушенного оттенка.
        
        Параметры:
        ----------
        color : str
            Исходный цвет (название или hex)
        gray_factor : float
            Коэффициент смешивания с серым (0-1)
            
        Возвращает:
        -----------
        tuple
            RGB цвет в формате (r, g, b)
        """
        # Преобразуем цвет в RGB
        rgb = self.mcolors.to_rgba(color)[:3]
        # Смешиваем с серым (0.5, 0.5, 0.5)
        mixed = tuple(gray_factor * 0.5 + (1 - gray_factor) * c for c in rgb)
        return mixed
    
    def _build_graph(self, x, y, approx):
        """
        Внутренний метод построения графика с экспериментальными данными.
        
        Обрабатывает различные комбинации входных данных и строит:
        - Точки экспериментальных данных с погрешностями
        - Аппроксимирующие прямые (если approx=True)
        """
        
        def is_phys_vector(obj):
            """Проверяет, является ли объект phys-вектором (массивом величин)."""
            return isinstance(obj, phys) and obj._is_array()
        
        def is_array_of_phys(obj):
            """Проверяет, является ли объект массивом phys-векторов."""
            if not isinstance(obj, (list, tuple, np.ndarray)) or len(obj) == 0:
                return False
            return all(isinstance(item, phys) for item in obj)
        
        def plot_approximation(x_vec, k, b, color_index=0, alpha=0.7):
            """
            Строит аппроксимирующую прямую.
            
            Параметры:
            ----------
            x_vec : phys
                Вектор данных по X для построения прямой
            k : float
                Коэффициент наклона
            b : float  
                Коэффициент смещения
            color_index : int
                Индекс цвета (для согласования с цветом точек)
            alpha : float
                Прозрачность линии
            """
            # Сортируем данные для гладкого отображения прямой
            x_sorted = x_vec.sort()
            # Вычисляем значения прямой
            y_fit = k * x_sorted.value + b
            
            # Создаем цвет для прямой - смесь серого и цвета соответствующих точек
            base_color = self.colors[color_index % len(self.colors)]
            mixed_color = self._mix_with_gray(base_color, 0.5)  # 50% серого
            
            # Построение аппроксимирующей прямой без подписи в легенде
            self.plt.plot(x_sorted.value, y_fit, '--', color=mixed_color, alpha=alpha)
        
        def plot_data_points(x_vec, y_vec, color_index=0, label=None):
            """
            Строит точки экспериментальных данных с погрешностями.
            
            Параметры:
            ----------
            x_vec : phys
                Данные по оси X
            y_vec : phys  
                Данные по оси Y
            color_index : int
                Индекс цвета в палитре
            label : str, optional
                Подпись для легенды
            """
            # Вычисляем адаптивный размер крышечек для этого набора данных
            adaptive_capsize = self._calculate_adaptive_capsize(x_vec, y_vec)
            
            self.plt.errorbar(
                x_vec.value, y_vec.value,           # Координаты точек
                xerr=x_vec.sigma,                   # Погрешности по X
                yerr=y_vec.sigma,                   # Погрешности по Y
                ecolor=self.mcolors.to_rgba(self.colors[color_index % len(self.colors)], alpha=0.75),  # Цвет погрешностей
                fmt='.',                            # Формат точек
                color=self.colors[color_index % len(self.colors)],  # Цвет точек
                capsize=adaptive_capsize,           # Адаптивный размер крышечек
                capthick=1,                         # Толщина крышечек
                label=label or f'Серия {color_index + 1}'  # Подпись в легенде
            )
        
        def plot_data_points_simple(x_val, y_val, x_err, y_err, color_index=0, label=None):
            """
            Упрощенная версия построения точек для обычных массивов.
            """
            # Для обычных массивов используем базовый расчет
            adaptive_capsize = self._calculate_adaptive_capsize(x_val, y_val)
            
            self.plt.errorbar(
                x_val, y_val,
                xerr=x_err,
                yerr=y_err,
                ecolor=self.mcolors.to_rgba(self.colors[color_index % len(self.colors)], alpha=0.75),
                fmt='.',
                color=self.colors[color_index % len(self.colors)],
                capsize=adaptive_capsize,
                capthick=1,
                label=label or f'Серия {color_index + 1}'
            )
        
        # Получаем параметры аппроксимации методом наименьших квадратов
        if approx:
            try:
                processor = LabProcessor()
                self.k, self.b = processor.weighted_least_squares(x, y)
            except Exception as e:
                print(f"Ошибка аппроксимации: {e}")
        
        # Определяем тип входных данных для выбора стратегии построения
        
        x_is_phys_vector = is_phys_vector(x)
        y_is_phys_vector = is_phys_vector(y)
        x_is_array_of_phys = is_array_of_phys(x)
        y_is_array_of_phys = is_array_of_phys(y)
        
        # Случай 1: оба аргумента - phys-векторы (один набор данных)
        if x_is_phys_vector and y_is_phys_vector:
            plot_data_points(x, y, 0, "Экспериментальные точки")
            if approx and self.k is not None:
                plot_approximation(x, self.k.value, self.b.value, 0)
        
        # Случай 2: x - phys-вектор, y - массив phys-векторов (несколько зависимостей от одного x)
        elif x_is_phys_vector and y_is_array_of_phys:
            for i, y_vec in enumerate(y):
                plot_data_points(x, y_vec, i, f"Серия {i+1}")
                if approx and self.k is not None:
                    # Извлекаем коэффициенты для текущей серии
                    k_val = self.k[i].value if hasattr(self.k, '__len__') and i < len(self.k) else self.k.value
                    b_val = self.b[i].value if hasattr(self.b, '__len__') and i < len(self.b) else self.b.value
                    plot_approximation(x, k_val, b_val, i)
        
        # Случай 3: y - phys-вектор, x - массив phys-векторов (несколько зависимостей от одного y)
        elif y_is_phys_vector and x_is_array_of_phys:
            for i, x_vec in enumerate(x):
                plot_data_points(x_vec, y, i, f"Серия {i+1}")
                if approx and self.k is not None:
                    k_val = self.k[i].value if hasattr(self.k, '__len__') and i < len(self.k) else self.k.value
                    b_val = self.b[i].value if hasattr(self.b, '__len__') and i < len(self.b) else self.b.value
                    plot_approximation(x_vec, k_val, b_val, i)
        
        # Случай 4: оба аргумента - массивы phys-векторов (парные наборы данных)
        elif x_is_array_of_phys and y_is_array_of_phys and len(x) == len(y):
            for i, (x_vec, y_vec) in enumerate(zip(x, y)):
                plot_data_points(x_vec, y_vec, i, f"Серия {i+1}")
                if approx and self.k is not None:
                    k_val = self.k[i].value if hasattr(self.k, '__len__') and i < len(self.k) else self.k.value
                    b_val = self.b[i].value if hasattr(self.b, '__len__') and i < len(self.b) else self.b.value
                    plot_approximation(x_vec, k_val, b_val, i)
        
        # Случай 5: обычные массивы чисел (без использования phys)
        else:
            # Извлекаем данные из phys объектов или используем как есть
            x_val = x.value if isinstance(x, phys) else np.array(x)
            y_val = y.value if isinstance(y, phys) else np.array(y)
            x_err = x.sigma if isinstance(x, phys) else None
            y_err = y.sigma if isinstance(y, phys) else None
            
            if (isinstance(x_val, np.ndarray) and isinstance(y_val, np.ndarray) and 
                len(x_val) == len(y_val)):
                
                plot_data_points_simple(x_val, y_val, x_err, y_err, 0, "Экспериментальные точки")
                
                # Аппроксимация для обычных данных
                if approx:
                    try:
                        processor = LabProcessor()
                        k, b = processor.weighted_least_squares(x, y)
                        if k is not None and b is not None:
                            x_sorted = np.sort(x_val)
                            y_fit = k.value * x_sorted + b.value
                            mixed_color = self._mix_with_gray(self.colors[0], 0.5)
                            self.plt.plot(x_sorted, y_fit, '--', color=mixed_color, alpha=0.8)
                    except Exception as e:
                        print(f"Ошибка аппроксимации: {e}")
    
    def __getattr__(self, name):
        """
        Делегирует вызовы методов к matplotlib.pyplot.
        
        Позволяет использовать методы matplotlib через объект graph:
        graph.xlabel() вместо graph.plt.xlabel()
        """
        return getattr(self.plt, name)
    
    def add_title(self, text, **kwargs):
        """
        Добавляет заголовок графика.
        
        Параметры:
        ----------
        text : str
            Текст заголовка
        **kwargs
            Дополнительные аргументы для plt.title()
            
        Возвращает:
        -----------
        self
            Для цепочки вызовов
        """
        self.plt.title(text, **kwargs)
        return self
    
    def set_legend(self, labels, **kwargs):
        """
        Устанавливает легенду графика.
        
        Параметры:
        ----------
        labels : list
            Список подписей для легенды
        **kwargs
            Дополнительные аргументы для plt.legend()
            
        Возвращает:
        -----------
        self
            Для цепочки вызовов
        """
        self.plt.legend(labels, **kwargs)
        return self
    
    def add_params_text(self, series_names=None, x=0.02, y=0.98, **kwargs):
        """
        Добавляет текстовый блок с параметрами аппроксимации на график.
        
        Параметры:
        ----------
        series_names : list, optional
            Названия серий данных
        x : float
            Позиция по X (0-1 от ширины графика)
        y : float  
            Позиция по Y (0-1 от высоты графика)
        **kwargs
            Дополнительные аргументы для figtext()
            
        Возвращает:
        -----------
        self
            Для цепочки вызовов
        """
        if self.k is not None and self.b is not None:
            texts = []
            # Обрабатываем случай как с одним, так и с несколькими наборами коэффициентов
            k_list = self.k if hasattr(self.k, '__len__') else [self.k]
            b_list = self.b if hasattr(self.b, '__len__') else [self.b]
            
            for i, (k, b) in enumerate(zip(k_list, b_list)):
                name = series_names[i] if series_names and i < len(series_names) else f"Серия {i+1}"
                text = f"{name}:\nk = {k.value:.4f} ± {k.sigma:.4f}\nb = {b.value:.4f} ± {b.sigma:.4f}"
                texts.append(text)
            
            param_text = "\n\n".join(texts)
            bbox_default = dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7)
            bbox = kwargs.pop('bbox', bbox_default)
            self.plt.figtext(x, y, param_text, bbox=bbox, **kwargs)
        return self
'''