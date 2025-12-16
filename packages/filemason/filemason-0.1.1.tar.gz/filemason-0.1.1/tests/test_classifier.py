import pytest


from filemason.services.reader import Reader


@pytest.fixture
def read_data_with_no_correct_bucket(basic_dir):
    return Reader().read_directory(basic_dir)


def test_unclassified_file(classifier, read_data_with_no_correct_bucket):

    classified_list, unclassified_list = classifier.classify(
        read_data_with_no_correct_bucket[0]
    )

    assert len(unclassified_list) == 2
    assert unclassified_list[0].extension == "toml"
    assert unclassified_list[0].tags == []
    assert classified_list == []


def test_classified_file(classifier, read_data_with_bucket):

    classified_list, unclassified_list = classifier.classify(read_data_with_bucket[0])

    assert len(classified_list) > 0
    assert classified_list[0].extension == "png"
    assert len(unclassified_list) == 1
    assert classified_list[0].tags == ["images"]
