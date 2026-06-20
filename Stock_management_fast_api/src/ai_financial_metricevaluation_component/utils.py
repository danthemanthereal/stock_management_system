from typing import Union, List, Tuple, Any


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

    print("get a cat map ")
    print(category_satisfied_map)
    return (
        convert_into_dictionary_if_necessary(category_satisfied_map).get(category, []),
        convert_into_dictionary_if_necessary(category_unsatisfied_map).get(category, []),
        convert_into_dictionary_if_necessary(category_satisfied_only_reference_value_map).get(category, []),
        convert_into_dictionary_if_necessary(category_unsatisfied_only_reference_value_map).get(category, []),
        convert_into_dictionary_if_necessary(category_satisfied_only_development_map).get(category, []),
        convert_into_dictionary_if_necessary(category_unsatisfied_development_map).get(category, []),
    )

def convert_into_dictionary_if_necessary(maybe_dict: Union[dict, List[Tuple[Any, Any]]]) -> dict:
    if isinstance(maybe_dict, dict):
        return maybe_dict
    if isinstance(maybe_dict, list):
        try:
            return dict(maybe_dict)
        except Exception as e:
            raise TypeError(f"List cannot be converted to dict: {e}")
    raise TypeError(f"Expected dict or list of tuples, got {type(maybe_dict)}")