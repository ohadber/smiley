"""
Non-mock tests for the utils module.
"""
import pytest
from utils import get_best_most_common_face, init_azure_client, Face


@pytest.fixture(autouse=True)
def init_client():
    """
    Initialize the azure client for each test.
    :return:
    """
    init_azure_client()


@pytest.fixture
def c_open(image_dir):
    """
    Create a custom open function.

    :type image_dir: pathlib.Path
    :return: The created function.
    :rtype: function
    """
    def open_func(*pic_names):
        """
        Custom open function to ease up the file opening. Automatically searches
        the image directory.

        :param pic_names: The picture names in the image directory.
        :return: The opened files.
        :rtype: list
        """
        files = []
        for name in pic_names:
            files.append(open(f'{image_dir}\\{name}', 'rb'))
        return files
    return open_func


class TestGetBestMostCommonFace:
    """
    Test the GetBestMostCommonFace function.
    """
    def test_no_photos(self):
        """
        Make sure that None is returned when the function is activated
        with an empty list as a parameter.
        """
        result = get_best_most_common_face([])
        assert result is None

    def test_single_photo(self, c_open):
        """
        Test the function with a single photo.
        """
        files = c_open("gadot.png")

        face = get_best_most_common_face(files)
        assert isinstance(face, Face)

    def test_multiple_photos(self, c_open):
        """
        Make sure that the function can handle multiple photos correctly.
        """
        files = c_open("gadot.png", "cage.png", "gadot2.png")

        face = get_best_most_common_face(files)
        assert isinstance(face, Face)
        assert face.gender == 'female'

    def test_all_different_people(self, c_open):
        """
        Make sure that the function can handle different people correctly.
        The function should select a random person because every appears
        the same.
        """
        files = c_open("gadot.png", "cage.png")

        face = get_best_most_common_face(files)
        assert isinstance(face, Face)

    def test_no_people(self, c_open):
        """
        Make sure that there are no people in the picture, None is returned.
        """
        files = c_open("mountain.png")

        face = get_best_most_common_face(files)
        assert face is None

