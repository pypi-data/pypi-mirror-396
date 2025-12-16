
import pytest
import trivial_records as tr

BOOKS = """
Peopleware
author1 Tom DeMarco
author2 Timothy Lister
publisher Addison Wesley

Fluent Python
author Luciano Ramalho
publisher O'Reilly
"""

CITIES = """
Barcelona
landmark_1 Parc Guell
landmark_2 Sagrada Familia

Amsterdam
landmark_1 Rijksmuseum
landmark_2 Concertgebouw
"""

SPARSE = (
    "record one\n"
    "key1 a value\n"
    "key2 another value\n"
    "\n\n\n"
    "record two\n"
    "key1 a value\n"
    "key2 another value\n"
    "\n\n\n\n\n\n"
    "record three\n"
    "key value\n"
    "\n\n"
)


def test_number_of_records_in_books_fixture() -> None:
    record_dictionary = tr.string_to_record_dictionary(BOOKS)
    assert len(record_dictionary) == 2


def test_first_books_record() -> None:
    record_dictionary = tr.string_to_record_dictionary(BOOKS)
    assert "Peopleware" in record_dictionary
    record = record_dictionary["Peopleware"]
    assert "author1" in record
    assert record["author1"] == "Tom DeMarco"
    assert "author2" in record
    assert record["author2"] == "Timothy Lister"
    assert "publisher" in record
    assert record["publisher"] == "Addison Wesley"


def test_no_spaces_in_keys_record() -> None:
    # Remember to not use spaces in the record's keys.
    record_dictionary = tr.string_to_record_dictionary(CITIES)
    assert "Amsterdam" in record_dictionary
    record = record_dictionary["Amsterdam"]
    assert "landmark_1" in record
    assert record["landmark_1"] == "Rijksmuseum"
    assert "landmark_2" in record
    assert record["landmark_2"] == "Concertgebouw"


def test_sparse() -> None:
    record_dictionary = tr.string_to_record_dictionary(SPARSE)
    assert list(record_dictionary.keys()) == [
        "record one", "record two", "record three"
    ]


def test_not_using_a_string() -> None:
    with pytest.raises(ValueError):
        tr.string_to_record_dictionary(None)


def test_empty_string() -> None:
    assert not tr.string_to_record_dictionary("")


def test_encode_decode() -> None:
    expected = {"one": {"a": "1", "b": "2"}, "two": {"c": "3"}}
    actual = tr.string_to_record_dictionary(
        tr.record_dictionary_to_string(expected)
    )
    assert expected == actual


def test_invalid_record_dictionary() -> None:
    with pytest.raises(ValueError):
        tr.record_dictionary_to_string({True: "bad dict"})


def test_invalid_record() -> None:
    with pytest.raises(ValueError):
        tr.record_dictionary_to_string({"obj": {123: "bad record"}})
