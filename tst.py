import pandas as pd
from itertools import groupby
import sys
import os

# подключаем pandana из текущей папки
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import pandana
except ImportError:
    print("Pandana не найдена. Установите её: pip install pandana")
    sys.exit(1)

def build_and_solve(csv_path: str):
    # 1) Чтение и приведение типов
    df = pd.read_csv(csv_path, sep=',', dtype=str, encoding='utf-8-sig')
    df.columns = df.columns.str.strip()
    num_cols = [
        'arc_sequence','from_node_id','to_node_id',
        'from_node_lat','from_node_lng',
        'to_node_lat','to_node_lng',
        'length','trip_id'
    ]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 2) Проверка обязательных колонок
    required = [
        'trip_id','arc_sequence',
        'from_node_id','from_node_lat','from_node_lng',
        'to_node_id','to_node_lat','to_node_lng',
        'length'
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Отсутствуют столбцы: {missing}")

    # 3) Собираем уникальные узлы
    df_from = df[['from_node_id','from_node_lat','from_node_lng']].rename(
        columns={'from_node_id':'id','from_node_lat':'lat','from_node_lng':'lng'}
    )
    df_to = df[['to_node_id','to_node_lat','to_node_lng']].rename(
        columns={'to_node_id':'id','to_node_lat':'lat','to_node_lng':'lng'}
    )
    df_nodes = pd.concat([df_from, df_to], ignore_index=True)
    df_nodes = df_nodes.drop_duplicates(subset='id').set_index('id')

    # 4) Собираем все рёбра с trip_id
    edges = df.rename(columns={
        'from_node_id':'from',
        'to_node_id':'to',
        'length':'weight'
    })[['from','to','weight','trip_id']]
    edges = edges.drop_duplicates(subset=['from','to'], keep='first')

    # 5) Строим граф
    net = pandana.Network(
        df_nodes['lng'], df_nodes['lat'],
        edges['from'], edges['to'], edges[['weight']],
        twoway=False, out=False
    )
    net.set_trip_ids(edges['trip_id'].values)

    # 6) Определяем старт и финиш из edges
    origin = int(edges.iloc[0]['from'])
    destination = int(edges.iloc[-1]['to'])

    # 7) Кратчайший путь
    node_path = list(net.shortest_paths([origin], [destination])[0])
    trip_path = net.shortest_paths([origin], [destination], trip_id=True)[0]

    # 8) Сжимаем последовательность trip_id
    trip_changes = [tid for tid, _ in groupby(trip_path)]

    print(f"\nКратчайший путь по узлам ({origin} → {destination}):")
    print(node_path)
    print("\nПолная последовательность trip_id:")
    print(trip_path)
    print("\nУникальные изменения trip_id:")
    print(trip_changes)

    paths_nodes = net.shortest_paths([origin], [destination])
    paths_trips = net.shortest_paths([origin], [destination], trip_id=True)
    print("\nПроверка типов:")
    print(type(paths_nodes[0]))
    print(type(paths_trips[0]))

if __name__ == '__main__':
    csv_file = 'C:/dev/projects/test2/df.csv'
    with open(csv_file, "r", encoding='utf-8') as f:
        build_and_solve(f)
