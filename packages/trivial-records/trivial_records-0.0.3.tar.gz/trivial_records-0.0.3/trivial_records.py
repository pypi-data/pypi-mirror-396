
import io

from typing import Any, cast, Generator

RecordDictionary = dict[str, dict[str, Any]]


def stream_to_record_dictionary(obj: Any) -> RecordDictionary:
    if not isinstance(obj, io.TextIOBase):
        raise ValueError("not an io.TextIOBase stream")

    stream = cast(io.TextIOBase, obj)

    result: RecordDictionary = {}
    read_record_name = True
    current_record_name = None
    while line := stream.readline():
        line = line.strip()
        if not line:
            read_record_name = True
            current_record_name = None
        else:
            if read_record_name:
                current_record_name = line
                result[current_record_name] = {}
                read_record_name = False
            else:
                key, value = line.split(maxsplit=1)
                assert current_record_name is not None
                result[current_record_name][key] = value
    return result


def string_to_record_dictionary(obj: Any) -> RecordDictionary:
    if not isinstance(obj, str):
        raise ValueError("argument must be a string")

    string = cast(str, obj)
    return stream_to_record_dictionary(io.StringIO(string))


def validate_record_dictionary(obj: Any):
    def all_are_instances(t: type, items: list) -> bool:
        return all([isinstance(i, t) for i in items])

    def all_are_strings(items: list) -> bool:
        return all_are_instances(str, items)

    def all_keys_are_strings(d: dict) -> bool:
        return all_are_strings(list(d.keys()))

    def all_values_are_dicts(d: dict) -> bool:
        return all_are_instances(dict, list(d.values()))

    if not isinstance(obj, dict):
        raise ValueError("object must be a dictionary")

    if not all_keys_are_strings(obj):
        raise ValueError("dictionary's keys must be strings")

    if not all_values_are_dicts(obj):
        raise ValueError("dictionary's values must be dicts")

    for r in obj.values():
        if not all_keys_are_strings(r):
            raise ValueError("record's keys must be strings: {}".format(r))


def record_dictionary_to_string_generator(
        obj: Any
) -> Generator[str, None, None]:
    validate_record_dictionary(obj)
    record_dictionary = cast(RecordDictionary, obj)

    separator = False
    for record_name, record in record_dictionary.items():
        if separator:
            yield "\n"
        separator = True
        yield record_name + "\n"
        for key, value in record.items():
            yield key + " " + str(value) + "\n"


def record_dictionary_to_string(obj: Any) -> str:
    generator = record_dictionary_to_string_generator(obj)
    return "".join(list(generator))
