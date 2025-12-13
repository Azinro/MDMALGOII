def binary_search(sorted_list, target, key_func):
    low = 0
    high = len(sorted_list) - 1
    target_lower = target.lower()

    while low <= high:
        mid = (low + high) // 2
        mid_value = key_func(sorted_list[mid]).lower()

        if mid_value == target_lower:
            return mid
        elif mid_value < target_lower:
            low = mid + 1
        else:
            high = mid - 1
    return -1