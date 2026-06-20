def get_all_used_categories_for_eval(category_satisfied_map: dict[str, list])->list[str]:
    if isinstance(category_satisfied_map, dict):
        return list(category_satisfied_map.keys())
    elif isinstance(category_satisfied_map, list) and all(isinstance(i, tuple) for i in category_satisfied_map):
        return [item[0] for item in category_satisfied_map]
    else:
        raise TypeError("Unsupported type")


def get_each_metrics_list_by_category(
        category : str,
        category_satisfied_map: dict[str, list],
                                    category_unsatisfied_map: dict[str, list],
                                    category_satisfied_only_reference_value_map: dict[str, list],
                                    category_unsatisfied_only_reference_value_map: dict[str, list],
                                    category_satisfied_only_development_map: dict[str, list],
                                    category_unsatisfied_development_map: dict[str, list],
                                      )->(list[str],
                                                                                 list[str],
                                                                                 list[str],
                                                                                 list[str],
                                                                                 list[str],
                                                                                 list[str]):
    return (
        category_satisfied_map.get(category, []),
        category_unsatisfied_map.get(category, []),
        category_satisfied_only_reference_value_map.get(category, []),
        category_unsatisfied_only_reference_value_map.get(category, []),
        category_satisfied_only_development_map.get(category, []),
        category_unsatisfied_development_map.get(category, []),
    )