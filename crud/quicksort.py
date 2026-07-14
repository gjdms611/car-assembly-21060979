def quicksort(items, key):
    if len(items) <= 1:
        return list(items)

    pivot = items[len(items) // 2][key]
    less = [item for item in items if item[key] < pivot]
    equal = [item for item in items if item[key] == pivot]
    greater = [item for item in items if item[key] > pivot]

    return quicksort(less, key) + equal + quicksort(greater, key)
