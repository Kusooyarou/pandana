# Руководство по установке и использованию trip_id в Pandana

## Установка

### Предварительные требования

1. **Python 3.7+**
2. **NumPy < 2.0** (для совместимости с Pandana)
3. **C++ компилятор** (для сборки Cython/C++ кода)

### Шаг 1: Клонирование репозитория
```bash
git clone <repository-url>
cd pdna
```

### Шаг 2: Создание виртуального окружения
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Шаг 3: Установка зависимостей
```bash
# Установка NumPy < 2.0
pip install "numpy<2.0"

# Установка Pandana в режиме разработки
pip install -e .
```

### Шаг 4: Проверка установки
```python
import pandana
print(f"Pandana version: {pandana.__version__}")

# Проверка доступности trip_id функциональности
network = pandana.Network([0], [0], [0], [0], [[1.0]])
print(hasattr(network, 'set_trip_ids'))  # Должно быть True
```

## Использование

### Базовый пример

```python
import pandana as pdna
import pandas as pd
import numpy as np

# Создание простой сети
nodes = pd.DataFrame({
    'x': [0, 1, 2, 3],
    'y': [0, 0, 0, 0]
}, index=[1, 2, 3, 4])

edges = pd.DataFrame({
    'from': [1, 2, 3],
    'to': [2, 3, 4],
    'distance': [1.0, 1.0, 1.0],
    'trip_id': [101, 102, 103]
})

# Создание сети
network = pdna.Network(
    nodes['x'], nodes['y'],
    edges['from'], edges['to'],
    edges[['distance']]
)

# Установка trip_ids
network.set_trip_ids(edges['trip_id'])

# Получение кратчайшего пути в виде trip_ids
trip_paths = network.shortest_paths([1], [4], trip_id=True)
print(f"Trip path: {trip_paths[0]}")  # [101, 102, 103]
```

### Продвинутый пример

```python
# Создание более сложной сети
nodes = pd.DataFrame({
    'x': [0, 1, 2, 3, 4, 5],
    'y': [0, 1, 0, 1, 0, 1]
}, index=[1, 2, 3, 4, 5, 6])

edges = pd.DataFrame({
    'from': [1, 2, 3, 4, 5, 1, 3, 5],
    'to': [2, 3, 4, 5, 6, 3, 5, 6],
    'distance': [1.0, 1.0, 1.0, 1.0, 1.0, 1.5, 1.5, 1.5],
    'trip_id': [101, 102, 103, 104, 105, 201, 202, 203]
})

network = pdna.Network(
    nodes['x'], nodes['y'],
    edges['from'], edges['to'],
    edges[['distance']]
)

# Установка trip_ids
network.set_trip_ids(edges['trip_id'])

# Множественные пути
origins = [1, 1, 2]
destinations = [6, 4, 6]

# Обычные пути (узлы)
node_paths = network.shortest_paths(origins, destinations)
print("Node paths:", node_paths)

# Trip_id пути
trip_paths = network.shortest_paths(origins, destinations, trip_id=True)
print("Trip paths:", trip_paths)
```

### Работа с реальными данными

```python
# Загрузка данных из файла
import pandas as pd

# Загрузка узлов
nodes_df = pd.read_csv('nodes.csv')
nodes_df.set_index('node_id', inplace=True)

# Загрузка рёбер с trip_ids
edges_df = pd.read_csv('edges.csv')

# Создание сети
network = pdna.Network(
    nodes_df['x'], nodes_df['y'],
    edges_df['from_node'], edges_df['to_node'],
    edges_df[['distance']]
)

# Установка trip_ids
network.set_trip_ids(edges_df['trip_id'])

# Анализ путей
origins = [1001, 1002, 1003]
destinations = [2001, 2002, 2003]

trip_paths = network.shortest_paths(origins, destinations, trip_id=True)

# Анализ результатов
for i, (origin, dest) in enumerate(zip(origins, destinations)):
    print(f"Path {origin} -> {dest}: {trip_paths[i]}")
```

## Обработка ошибок

### Проверка установки trip_ids

```python
# Проверка наличия trip_ids
if network.trip_ids is None:
    print("Trip IDs not set")
else:
    print(f"Trip IDs set for {len(network.trip_ids)} edges")

# Безопасное использование
try:
    trip_paths = network.shortest_paths([1], [5], trip_id=True)
except ValueError as e:
    print(f"Error: {e}")
    # Установить trip_ids или использовать обычный режим
    node_paths = network.shortest_paths([1], [5])
```

### Валидация данных

```python
def validate_trip_ids(network, trip_ids):
    """Проверка корректности trip_ids"""
    if len(trip_ids) != len(network.edges_df):
        raise ValueError(f"Expected {len(network.edges_df)} trip_ids, got {len(trip_ids)}")
    
    if not all(isinstance(tid, (int, np.integer)) for tid in trip_ids):
        raise ValueError("All trip_ids must be integers")
    
    return True

# Использование
trip_ids = [101, 102, 103, 104]
validate_trip_ids(network, trip_ids)
network.set_trip_ids(trip_ids)
```

## Тестирование

### Запуск тестов

```bash
# Простой тест
python test_simple_trip_id.py

# Полный тест
python test_trip_id.py
```

### Создание собственных тестов

```python
import unittest
import pandana as pdna
import pandas as pd

class TestTripId(unittest.TestCase):
    
    def setUp(self):
        """Создание тестовой сети"""
        self.nodes = pd.DataFrame({
            'x': [0, 1, 2], 'y': [0, 0, 0]
        }, index=[1, 2, 3])
        
        self.edges = pd.DataFrame({
            'from': [1, 2], 'to': [2, 3],
            'distance': [1.0, 1.0], 'trip_id': [101, 102]
        })
        
        self.network = pdna.Network(
            self.nodes['x'], self.nodes['y'],
            self.edges['from'], self.edges['to'],
            self.edges[['distance']]
        )
    
    def test_set_trip_ids(self):
        """Тест установки trip_ids"""
        self.network.set_trip_ids(self.edges['trip_id'])
        self.assertIsNotNone(self.network.trip_ids)
        self.assertEqual(len(self.network.trip_ids), 2)
    
    def test_shortest_paths_trip_id(self):
        """Тест получения путей в виде trip_ids"""
        self.network.set_trip_ids(self.edges['trip_id'])
        trip_paths = self.network.shortest_paths([1], [3], trip_id=True)
        self.assertEqual(trip_paths[0], [101, 102])
    
    def test_error_no_trip_ids(self):
        """Тест ошибки при отсутствии trip_ids"""
        with self.assertRaises(ValueError):
            self.network.shortest_paths([1], [3], trip_id=True)

if __name__ == '__main__':
    unittest.main()
```

## Производительность

### Бенчмарки

```python
import time
import numpy as np

def benchmark_trip_id(network, origins, destinations, iterations=100):
    """Тест производительности trip_id функциональности"""
    
    # Обычные пути
    start_time = time.time()
    for _ in range(iterations):
        node_paths = network.shortest_paths(origins, destinations)
    node_time = time.time() - start_time
    
    # Trip_id пути
    start_time = time.time()
    for _ in range(iterations):
        trip_paths = network.shortest_paths(origins, destinations, trip_id=True)
    trip_time = time.time() - start_time
    
    print(f"Node paths: {node_time:.4f}s")
    print(f"Trip paths: {trip_time:.4f}s")
    print(f"Overhead: {((trip_time - node_time) / node_time * 100):.2f}%")

# Использование
origins = np.random.choice(network.node_ids, 100)
destinations = np.random.choice(network.node_ids, 100)
benchmark_trip_id(network, origins, destinations)
```

## Устранение неполадок

### Проблема: "trip_id=True requires trip_ids to be set"

**Решение:**
```python
# Убедитесь, что trip_ids установлены
network.set_trip_ids(your_trip_ids)

# Проверьте, что trip_ids установлены
print(network.trip_ids is not None)
```

### Проблема: Неправильные trip_ids в результатах

**Решение:**
```python
# Проверьте соответствие trip_ids количеству рёбер
print(f"Edges: {len(network.edges_df)}")
print(f"Trip IDs: {len(your_trip_ids)}")

# Убедитесь, что trip_ids соответствуют порядку рёбер
for i, (edge, trip_id) in enumerate(zip(network.edges_df.itertuples(), your_trip_ids)):
    print(f"Edge {i}: {edge.from}->{edge.to}, Trip ID: {trip_id}")
```

### Проблема: Ошибки компиляции

**Решение:**
```bash
# Пересборка Pandana
pip uninstall pandana
pip install -e .

# Проверка версии NumPy
pip show numpy  # Должно быть < 2.0
```

## Заключение

Функциональность `trip_id` в Pandana предоставляет мощный инструмент для анализа транспортных сетей с реальными идентификаторами маршрутов. Следуя этому руководству, вы сможете:

1. ✅ Установить и настроить функциональность
2. ✅ Использовать API для получения trip_id путей
3. ✅ Обрабатывать ошибки и граничные случаи
4. ✅ Тестировать и оптимизировать производительность
5. ✅ Устранять возможные проблемы

Эта функциональность особенно полезна для анализа общественного транспорта, где важно работать с реальными идентификаторами маршрутов вместо абстрактных узлов сети. 