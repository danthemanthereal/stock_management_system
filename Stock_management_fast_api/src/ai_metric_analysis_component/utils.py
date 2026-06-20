def get_satisfied_on_all_three_per_category(
        category_name: str,
        satisfied_by_category_map: dict,
        unsatisfied_by_category_map: dict,
        satisfied_only_reference_value_map: dict,
        unsatisfied_only_reference_value_map: dict,
        satisfied_only_development_map: dict,
        unsatisfied_only_development_map: dict,
    ):
    return (
        satisfied_by_category_map.get(category_name, []),
        unsatisfied_by_category_map.pop(category_name, []),
        satisfied_only_reference_value_map.get(category_name),
        unsatisfied_only_reference_value_map.get(category_name, []),
        satisfied_only_development_map.get(category_name, []),
        unsatisfied_only_development_map.get(category_name, []),
    )

def get_all_considered_category_of_current_request(
    satisfied_by_category_map: dict[str:list]
    )->list[str]:
    return list(satisfied_by_category_map.keys())