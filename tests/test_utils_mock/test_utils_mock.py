"""
Implement unittest for the utils.py file.
"""
import pytest

from utils import Photo, get_common_face_uids, _get_faces_by_uids, \
    get_best_face


@pytest.fixture
def photo1():
    """
    Create a photo.

    :return: The created photo
    :rtype: Photo
    """
    return Photo(None)


@pytest.fixture
def photo2():
    """
    Create a photo.

    :return: The created photo.
    :rtype: Photo
    """
    return Photo(None)


@pytest.fixture
def mock_face_api(mocker):
    """
    Mock the azure face api.

    :type mocker: pytest_mock.MockFixture
    """
    mocker.patch('utils.cf.face')


@pytest.fixture
def photo_multiple_faces(generator, photo1, photo2):
    """
    :type photo1: Photo
    :type photo2: Photo
    """
    f1 = generator.face(photo=photo1, uid='a')
    f2 = generator.face(photo=photo1, uid='b')
    photo1.uid_to_face = {'a': f1, 'b': f2}

    return photo1


@pytest.mark.usefixtures("mock_face_api")
class TestGetCommonFaceUids:
    """
    test get_common_face_uids
    """
    def test_no_common_face(self, photo1, photo2):
        """
        Make sure that when there is no common face(all the faces
        are different) then the function returns one of them.
        """
        result = get_common_face_uids([photo1, photo2])
        assert result is not None

    def test_happy_flow(self, generator, photo_multiple_faces, photo2):
        """
        Make sure that the function returns the appropriate most common face.
        """
        generator.face(photo=photo2, uid='c')

        faces = get_common_face_uids([photo_multiple_faces, photo2])
        for face in faces:
            assert face.uid in ['a', 'c']

    def test_no_faces(self, photo1, photo2):
        """
        Make sure that when there are no faces detected in the pictures that
        the function will returned `None`.
        """
        assert get_common_face_uids([photo1, photo2]) == []

    def test_no_photos(self):
        """
        Make sure that when no photos given are input to the function that
        None is returned.
        """
        assert get_common_face_uids([]) == []


class TestGetBestFace:
    """
    test get_best_face.
    """
    def test_no_faces(self):
        """
        Make sure that when no faces are given that nothing is returned.
        """
        get_best_face([])

    def test_equal_best(self, generator):
        """
        Test what happens when there are equal best faces - just return
        the first one.

        :type generator: Generator
        """
        face1, face2 = generator.faces('a', 'b')
        photo = generator.photo(face1, face2)
        face1.size = 100
        face2.size = 100
        photo.size = 1000

        result = get_best_face([face1, face2])
        assert result is face1

    def test_happy_flow(self, generator):
        """
        Make sure the function works in normal flow. The face which covers
        the most of the photo should be returned.
        :type generator: Generator
        """
        face1, face2 = generator.faces('a', 'b')
        photo = generator.photo(face1, face2)
        face1.size = 100
        face2.size = 500
        photo.size = 1000

        result = get_best_face([face1, face2])
        assert result is face2


@pytest.mark.parametrize("generated_uids, required_uids, expected_uids",
                         [
                             # happy-flow
                             (["a", "b", "c"], ["a", "b"], ["a", "b"]),
                             # empty flow
                             (["a", "b", "c"], [], []),
                             # invalid call, don't throw an exception
                             ([], ["a"], [])
                         ]
                         )
def test_get_faces_by_uids(generator, generated_uids, required_uids, expected_uids):
    """
    Test that the get_faces_by_uids returns the proper Face objects.
    """
    faces = generator.faces(*generated_uids)
    uids = required_uids

    faces = _get_faces_by_uids(uids, faces)

    for face in faces:
        assert face.uid in expected_uids

