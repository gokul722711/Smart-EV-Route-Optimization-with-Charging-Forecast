import heapq
from typing import Dict, Tuple, List


def dijkstra(graph: Dict, start: str, end: str):
    """
    Dijkstra's algorithm using priority queue.
    Graph format:
    {
        node: {
            neighbor: weight,
            ...
        }
    }
    """

    priority_queue = [(0, start)]
    distances = {node: float("inf") for node in graph}
    distances[start] = 0
    previous = {node: None for node in graph}

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_node == end:
            break

        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

    # Reconstruct path
    path = []
    node = end

    while node:
        path.insert(0, node)
        node = previous[node]

    return path, distances[end]

def astar(graph, start, end, heuristic):
    """
    A* search algorithm.
    """

    priority_queue = [(0, start)]
    g_cost = {node: float("inf") for node in graph}
    g_cost[start] = 0
    previous = {node: None for node in graph}

    while priority_queue:
        current_f, current_node = heapq.heappop(priority_queue)

        if current_node == end:
            break

        for neighbor, weight in graph[current_node].items():
            tentative_g = g_cost[current_node] + weight

            if tentative_g < g_cost[neighbor]:
                g_cost[neighbor] = tentative_g
                f_cost = tentative_g + heuristic(neighbor)
                heapq.heappush(priority_queue, (f_cost, neighbor))
                previous[neighbor] = current_node

    path = []
    node = end

    while node:
        path.insert(0, node)
        node = previous[node]

    return path, g_cost[end]

def astar_state_search(
    nodes,
    get_distance_func,
    start_node,
    end_node,
    max_range,
    initial_battery,
    vehicle_efficiency,
    get_charger_power,
    heuristic
):
    """
    A* search over (node, battery_remaining) state space.
    Returns full reconstructed path.
    """

    import heapq

    # (priority_cost, actual_cost, node, battery_remaining)
    pq = [(0, 0, start_node, initial_battery)]

    visited = {}
    parent = {}

    while pq:
        priority_cost, actual_cost, current_node, battery_left = heapq.heappop(pq)

        state_key = (current_node, round(battery_left, 2))

        if state_key in visited:
            continue

        visited[state_key] = actual_cost

        if current_node == end_node:
            # Reconstruct path
            path = []
            state = state_key

            while state in parent:
                path.append(state)
                state = parent[state]

            path.append((start_node, initial_battery))
            path.reverse()

            return {
                "path": path,
                "total_cost": actual_cost
            }

        # Travel transitions
        for next_node in nodes:
            if next_node == current_node:
                continue

            distance_km, duration_min = get_distance_func(
                nodes[current_node],
                nodes[next_node]
            )

            if distance_km <= battery_left:
                new_battery = round(battery_left - distance_km, 2)
                new_cost = actual_cost + duration_min

                next_state = (next_node, new_battery)

                if next_state not in visited:
                    parent[next_state] = state_key

                    heapq.heappush(
                        pq,
                        (
                            new_cost + heuristic(next_node),
                            new_cost,
                            next_node,
                            new_battery
                        )
                    )

        # Charging transition
        if current_node != start_node and current_node != end_node:
            charger_power = get_charger_power(current_node)

            energy_needed = (max_range - battery_left) / vehicle_efficiency
            charging_time = (energy_needed / charger_power) * 60

            new_cost = actual_cost + charging_time
            new_battery = max_range

            next_state = (current_node, new_battery)

            if next_state not in visited:
                parent[next_state] = state_key

                heapq.heappush(
                    pq,
                    (
                        new_cost,
                        new_cost,
                        current_node,
                        new_battery
                    )
                )

    return None
