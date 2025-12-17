import numpy as np
from core import phys, LabProcessor
import matplotlib.pyplot as plt

def run_mnk_tests():
    """Запуск всех тестов МНК"""
    lab = LabProcessor()
    test_results = []
    
    print("=== ТЕСТИРОВАНИЕ МЕТОДОВ МНК ===\n")
    
    # Тест 1: Идеальная прямая без погрешностей
    test_results.append(test_perfect_line(lab))
    
    # Тест 2: Идеальная прямая с малыми погрешностями
    test_results.append(test_perfect_line_small_errors(lab))
    
    # Тест 3: Идеальная прямая с большими погрешностями
    test_results.append(test_perfect_line_large_errors(lab))
    
    # Тест 4: Случайные данные с известными параметрами
    test_results.append(test_random_data_known_params(lab))
    
    # Тест 5: Вертикальная линия (вырожденный случай)
    test_results.append(test_vertical_line(lab))
    
    # Тест 6: Горизонтальная линия
    test_results.append(test_horizontal_line(lab))
    
    # Тест 7: Всего 2 точки
    test_results.append(test_only_two_points(lab))
    
    # Тест 8: Одна точка (граничный случай)
    test_results.append(test_single_point(lab))
    
    # Тест 9: Большой набор данных
    test_results.append(test_large_dataset(lab))
    
    # Тест 10: Данные с нулевыми погрешностями
    test_results.append(test_zero_errors(lab))
    
    # Тест 11: Сильно зашумленные данные
    test_results.append(test_noisy_data(lab))
    
    # Тест 12: Проверка взвешенного среднего
    test_results.append(test_weighted_mean(lab))
    
    # Тест 13: Несколько наборов данных
    test_results.append(test_multiple_datasets(lab))
    
    # Тест 14: Проверка на корреляцию
    test_results.append(test_correlation(lab))
    
    # Сводка результатов
    passed = sum(test_results)
    total = len(test_results)
    print(f"\n=== РЕЗУЛЬТАТЫ: {passed}/{total} тестов пройдено ===")
    
    return test_results

def test_perfect_line(lab):
    """Тест 1: Идеальная прямая y = 2x + 1 без погрешностей"""
    print("Тест 1: Идеальная прямая без погрешностей")
    
    x = phys([0, 1, 2, 3, 4, 5], 0.0)
    y = phys([1, 3, 5, 7, 9, 11], 0.0)  # y = 2x + 1
    
    k, b = lab.weighted_least_squares(x, y)
    
    expected_k = 2.0
    expected_b = 1.0
    
    print(f"Получено: k = {k.value:.6f} ± {k.sigma:.6f}, b = {b.value:.6f} ± {b.sigma:.6f}")
    print(f"Ожидалось: k = {expected_k}, b = {expected_b}")
    
    # Погрешности должны быть очень маленькими для идеальных данных
    k_ok = abs(k.value - expected_k) < 1e-10 and k.sigma < 1e-10
    b_ok = abs(b.value - expected_b) < 1e-10 and b.sigma < 1e-10
    
    print(f"Результат: {'ПРОЙДЕН' if k_ok and b_ok else 'НЕ ПРОЙДЕН'}\n")
    return k_ok and b_ok

def test_perfect_line_small_errors(lab):
    """Тест 2: Идеальная прямая с малыми погрешностями"""
    print("Тест 2: Идеальная прямая с малыми погрешностями")
    
    x = phys([0, 1, 2, 3, 4, 5], 0.01)
    y = phys([1, 3, 5, 7, 9, 11], 0.01)  # y = 2x + 1
    
    k, b = lab.weighted_least_squares(x, y)
    
    expected_k = 2.0
    expected_b = 1.0
    
    print(f"Получено: k = {k.value:.6f} ± {k.sigma:.6f}, b = {b.value:.6f} ± {b.sigma:.6f}")
    print(f"Ожидалось: k = {expected_k}, b = {expected_b}")
    
    # Значения должны быть близки к ожидаемым, погрешности небольшие
    k_ok = abs(k.value - expected_k) < 0.01 and k.sigma < 0.1
    b_ok = abs(b.value - expected_b) < 0.01 and b.sigma < 0.1
    
    print(f"Результат: {'ПРОЙДЕН' if k_ok and b_ok else 'НЕ ПРОЙДЕН'}\n")
    return k_ok and b_ok

def test_perfect_line_large_errors(lab):
    """Тест 3: Идеальная прямая с большими погрешностями"""
    print("Тест 3: Идеальная прямая с большими погрешностями")
    
    x = phys([0, 1, 2, 3, 4, 5], 0.5)
    y = phys([1, 3, 5, 7, 9, 11], 0.5)  # y = 2x + 1
    
    k, b = lab.weighted_least_squares(x, y)
    
    expected_k = 2.0
    expected_b = 1.0
    
    print(f"Получено: k = {k.value:.6f} ± {k.sigma:.6f}, b = {b.value:.6f} ± {b.sigma:.6f}")
    print(f"Ожидалось: k = {expected_k}, b = {expected_b}")
    
    # При больших погрешностях значения могут отличаться, но погрешности должны быть адекватными
    k_ok = abs(k.value - expected_k) < k.sigma * 3  # В пределах 3 сигм
    b_ok = abs(b.value - expected_b) < b.sigma * 3
    errors_reasonable = k.sigma > 0.1 and b.sigma > 0.1  # Погрешности не должны быть слишком маленькими
    
    print(f"Результат: {'ПРОЙДЕН' if k_ok and b_ok and errors_reasonable else 'НЕ ПРОЙДЕН'}\n")
    return k_ok and b_ok and errors_reasonable

def test_random_data_known_params(lab):
    """Тест 4: Случайные данные с известными параметрами"""
    print("Тест 4: Случайные данные с известными параметрами")
    
    np.random.seed(42)  # Для воспроизводимости
    n_points = 20
    true_k = 1.5
    true_b = 2.0
    
    x_clean = np.linspace(0, 10, n_points)
    y_clean = true_k * x_clean + true_b
    noise = np.random.normal(0, 0.5, n_points)
    
    x = phys(x_clean, 0.1)
    y = phys(y_clean + noise, 0.2)
    
    k, b = lab.weighted_least_squares(x, y)
    
    print(f"Получено: k = {k.value:.6f} ± {k.sigma:.6f}, b = {b.value:.6f} ± {b.sigma:.6f}")
    print(f"Истинные: k = {true_k}, b = {true_b}")
    
    # Проверяем, что истинные значения лежат в пределах погрешностей
    k_ok = abs(k.value - true_k) < k.sigma * 2
    b_ok = abs(b.value - true_b) < b.sigma * 2
    
    print(f"Результат: {'ПРОЙДЕН' if k_ok and b_ok else 'НЕ ПРОЙДЕН'}\n")
    return k_ok and b_ok

def test_vertical_line(lab):
    """Тест 5: Вертикальная линия (вырожденный случай)"""
    print("Тест 5: Вертикальная линия (вырожденный случай)")
    
    x = phys([5, 5, 5, 5, 5], 0.1)
    y = phys([0, 1, 2, 3, 4], 0.1)
    
    try:
        k, b = lab.weighted_least_squares(x, y)
        print(f"Получено: k = {k.value:.6f} ± {k.sigma:.6f}, b = {b.value:.6f} ± {b.sigma:.6f}")
        
        # Для вертикальной линии k должно быть большим, b не определено
        # Проверяем, что метод не падает и возвращает разумные значения
        k_ok = abs(k.value) > 10 or k.sigma > 10  # Большие значения/погрешности
        print(f"Результат: {'ПРОЙДЕН' if k_ok else 'НЕ ПРОЙДЕН'} (ожидались большие погрешности)\n")
        return k_ok
    except Exception as e:
        print(f"Метод упал с ошибкой: {e}")
        print("Результат: НЕ ПРОЙДЕН (метод не должен падать на вырожденных данных)\n")
        return False

def test_horizontal_line(lab):
    """Тест 6: Горизонтальная линия"""
    print("Тест 6: Горизонтальная линия")
    
    x = phys([0, 1, 2, 3, 4, 5], 0.1)
    y = phys([3, 3, 3, 3, 3, 3], 0.1)  # y = 3
    
    k, b = lab.weighted_least_squares(x, y)
    
    expected_k = 0.0
    expected_b = 3.0
    
    print(f"Получено: k = {k.value:.6f} ± {k.sigma:.6f}, b = {b.value:.6f} ± {b.sigma:.6f}")
    print(f"Ожидалось: k = {expected_k}, b = {expected_b}")
    
    k_ok = abs(k.value - expected_k) < k.sigma * 2
    b_ok = abs(b.value - expected_b) < b.sigma * 2
    
    print(f"Результат: {'ПРОЙДЕН' if k_ok and b_ok else 'НЕ ПРОЙДЕН'}\n")
    return k_ok and b_ok

def test_only_two_points(lab):
    """Тест 7: Всего 2 точки"""
    print("Тест 7: Всего 2 точки")
    
    x = phys([1, 2], 0.1)
    y = phys([2, 4], 0.1)  # y = 2x
    
    k, b = lab.weighted_least_squares(x, y)
    
    expected_k = 2.0
    expected_b = 0.0
    
    print(f"Получено: k = {k.value:.6f} ± {k.sigma:.6f}, b = {b.value:.6f} ± {b.sigma:.6f}")
    print(f"Ожидалось: k = {expected_k}, b = {expected_b}")
    
    k_ok = abs(k.value - expected_k) < 0.1
    # Для 2 точек погрешность b должна быть большой
    b_ok = abs(b.value - expected_b) < b.sigma * 3
    
    print(f"Результат: {'ПРОЙДЕН' if k_ok and b_ok else 'НЕ ПРОЙДЕН'}\n")
    return k_ok and b_ok

def test_single_point(lab):
    """Тест 8: Одна точка (граничный случай)"""
    print("Тест 8: Одна точка")
    
    x = phys([2.5], 0.1)
    y = phys([3.7], 0.1)
    
    try:
        k, b = lab.weighted_least_squares(x, y)
        print(f"Получено: k = {k.value:.6f} ± {k.sigma:.6f}, b = {b.value:.6f} ± {b.sigma:.6f}")
        
        # Для одной точки ожидаем большие погрешности
        errors_large = k.sigma > 1.0 and b.sigma > 1.0
        print(f"Результат: {'ПРОЙДЕН' if errors_large else 'НЕ ПРОЙДЕН'} (ожидались большие погрешности)\n")
        return errors_large
    except Exception as e:
        print(f"Метод упал с ошибкой: {e}")
        print("Результат: ПРОЙДЕН (метод может падать на одной точке)\n")
        return True  # Не все методы МНК работают с одной точкой

def test_large_dataset(lab):
    """Тест 9: Большой набор данных"""
    print("Тест 9: Большой набор данных")
    
    np.random.seed(123)
    n_points = 100
    true_k = 0.8
    true_b = -1.2
    
    x_clean = np.linspace(0, 10, n_points)
    y_clean = true_k * x_clean + true_b
    noise = np.random.normal(0, 0.3, n_points)
    
    x = phys(x_clean, 0.05)
    y = phys(y_clean + noise, 0.1)
    
    k, b = lab.weighted_least_squares(x, y)
    
    print(f"Получено: k = {k.value:.6f} ± {k.sigma:.6f}, b = {b.value:.6f} ± {b.sigma:.6f}")
    print(f"Истинные: k = {true_k}, b = {true_b}")
    
    # Для большого набора данных погрешности должны быть маленькими
    k_ok = abs(k.value - true_k) < k.sigma * 3 and k.sigma < 0.1
    b_ok = abs(b.value - true_b) < b.sigma * 3 and b.sigma < 0.2
    
    print(f"Результат: {'ПРОЙДЕН' if k_ok and b_ok else 'НЕ ПРОЙДЕН'}\n")
    return k_ok and b_ok

def test_zero_errors(lab):
    """Тест 10: Данные с нулевыми погрешностями"""
    print("Тест 10: Данные с нулевыми погрешностями")
    
    x = phys([1, 2, 3, 4, 5], 0.0)
    y = phys([1.5, 2.7, 4.1, 5.2, 6.8], 0.0)
    
    k, b = lab.weighted_least_squares(x, y)
    
    print(f"Получено: k = {k.value:.6f} ± {k.sigma:.6f}, b = {b.value:.6f} ± {b.sigma:.6f}")
    
    # При нулевых погрешностях метод не должен падать
    # Погрешности коэффициентов могут быть вычислены на основе разброса точек
    method_works = not np.isnan(k.value) and not np.isnan(b.value)
    errors_calculated = k.sigma > 0 and b.sigma > 0
    
    print(f"Результат: {'ПРОЙДЕН' if method_works and errors_calculated else 'НЕ ПРОЙДЕН'}\n")
    return method_works and errors_calculated

def test_noisy_data(lab):
    """Тест 11: Сильно зашумленные данные"""
    print("Тест 11: Сильно зашумленные данные")
    
    np.random.seed(456)
    n_points = 15
    true_k = 1.2
    true_b = 0.5
    
    x_clean = np.linspace(0, 5, n_points)
    noise = np.random.normal(0, 2.0, n_points)  # Большой шум
    y_noisy = true_k * x_clean + true_b + noise
    
    x = phys(x_clean, 0.1)
    y = phys(y_noisy, 0.5)
    
    k, b = lab.weighted_least_squares(x, y)
    
    print(f"Получено: k = {k.value:.6f} ± {k.sigma:.6f}, b = {b.value:.6f} ± {b.sigma:.6f}")
    print(f"Истинные: k = {true_k}, b = {true_b}")
    
    # Для зашумленных данных погрешности должны быть большими
    k_ok = abs(k.value - true_k) < k.sigma * 3
    b_ok = abs(b.value - true_b) < b.sigma * 3
    errors_large = k.sigma > 0.3 and b.sigma > 0.5
    
    print(f"Результат: {'ПРОЙДЕН' if k_ok and b_ok and errors_large else 'НЕ ПРОЙДЕН'}\n")
    return k_ok and b_ok and errors_large

def test_weighted_mean(lab):
    """Тест 12: Проверка взвешенного среднего"""
    print("Тест 12: Проверка взвешенного среднего")
    
    # Точки с разными погрешностями
    measurements = [
        phys(10.0, 0.1),  # Малая погрешность - большой вес
        phys(10.5, 0.5),  # Средняя погрешность  
        phys(9.8, 1.0)    # Большая погрешность - малый вес
    ]
    
    result = lab.weighted_mean(measurements)
    
    # Взвешенное среднее должно быть ближе к точке с малой погрешностью
    expected = 10.0  # Должно быть ближе к 10.0 чем к 9.8
    
    print(f"Получено: {result.value:.6f} ± {result.sigma:.6f}")
    print(f"Ожидалось: ~{expected}")
    
    mean_ok = abs(result.value - expected) < 0.2
    error_reasonable = result.sigma < 0.2
    
    print(f"Результат: {'ПРОЙДЕН' if mean_ok and error_reasonable else 'НЕ ПРОЙДЕН'}\n")
    return mean_ok and error_reasonable

def test_multiple_datasets(lab):
    """Тест 13: Несколько наборов данных"""
    print("Тест 13: Несколько наборов данных")
    
    # Два набора данных с разными параметрами
    x1 = phys([1, 2, 3, 4], 0.1)
    y1 = phys([2, 4, 6, 8], 0.1)  # y = 2x
    
    x2 = phys([1, 2, 3, 4], 0.1)  
    y2 = phys([3, 5, 7, 9], 0.1)  # y = 2x + 1
    
    k, b = lab.weighted_least_squares([x1, x2], [y1, y2])
    
    print(f"Получено: k = {[k_i.value for k_i in k]}, b = {[b_i.value for b_i in b]}")
    
    # Проверяем, что получили два набора коэффициентов
    two_sets = len(k) == 2 and len(b) == 2
    k1_ok = abs(k[0].value - 2.0) < 0.1
    b1_ok = abs(b[0].value - 0.0) < 0.2
    k2_ok = abs(k[1].value - 2.0) < 0.1  
    b2_ok = abs(b[1].value - 1.0) < 0.2
    
    print(f"Результат: {'ПРОЙДЕН' if two_sets and k1_ok and b1_ok and k2_ok and b2_ok else 'НЕ ПРОЙДЕН'}\n")
    return two_sets and k1_ok and b1_ok and k2_ok and b2_ok

def test_correlation(lab):
    """Тест 14: Проверка на корреляцию параметров"""
    print("Тест 14: Проверка на корреляцию параметров")
    
    # Данные, где k и b сильно коррелированы
    x = phys([1, 2, 3, 4, 5], 0.1)
    y = phys([3, 5, 7, 9, 11], 0.1)  # y = 2x + 1
    
    k, b = lab.weighted_least_squares(x, y)
    
    print(f"Получено: k = {k.value:.6f} ± {k.sigma:.6f}, b = {b.value:.6f} ± {b.sigma:.6f}")
    
    # Проверяем, что погрешности не чрезмерно большие
    # При сильной корреляции погрешности могут быть увеличены, но не на порядки
    k_error_reasonable = k.sigma < 0.5
    b_error_reasonable = b.sigma < 1.0
    
    print(f"Результат: {'ПРОЙДЕН' if k_error_reasonable and b_error_reasonable else 'НЕ ПРОЙДЕН'}\n")
    return k_error_reasonable and b_error_reasonable

def analyze_error_sources():
    """Анализ возможных источников ошибок в МНК"""
    print("\n=== АНАЛИЗ ВОЗМОЖНЫХ ИСТОЧНИКОВ ОШИБОК ===")
    
    sources = [
        "1. Неправильная формула для взвешенного МНК",
        "2. Некорректная обработка нулевых погрешностей", 
        "3. Проблемы с численной устойчивостью при маленьких determinant",
        "4. Ошибки в расчете ковариационной матрицы",
        "5. Неправильная обработка вырожденных случаев",
        "6. Проблемы с преобразованием типов данных",
        "7. Ошибки в расчете весов",
        "8. Накопление ошибок округления в цепочках вычислений",
        "9. Неправильная обработка массивов с разными размерами",
        "10. Ошибки в формулах для погрешностей коэффициентов"
    ]
    
    for source in sources:
        print(source)
    
    print("\nРекомендуется:")
    print("- Проверить формулы в EnhancedLeastSquares._weighted_least_squares_y")
    print("- Убедиться в корректности расчета весов в ErrorProcessor")
    print("- Протестировать на синтетических данных с известным ответом")
    print("- Проверить обработку граничных случаев (1 точка, 2 точки)")
    print("- Сравнить с реализацией МНК из scipy или numpy")

if __name__ == "__main__":
    # Запуск всех тестов
    results = run_mnk_tests()
    
    # Анализ возможных проблем
    if sum(results) < len(results):
        analyze_error_sources()
        
        # Дополнительная диагностика
        print("\n=== ДОПОЛНИТЕЛЬНАЯ ДИАГНОСТИКА ===")
        print("Запустите отладку на конкретных примерах для выявления проблем.")
        print("Рекомендуется начать с тестов 1, 2, 4 которые должны давать точные результаты.")
