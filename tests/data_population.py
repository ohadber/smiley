"""
Data population utilities. Should be used for testing.
"""
from utils import Photo, Face


class Generator:
    """
    Helper class for test objects creation.
    """
    def __init__(self, mocker):
        """
        :param mocker: pytest's mocker(the same one that is given as a fixture).
        :type mocker: pytest_mock.MockFixture
        """
        self.mocker = mocker

    def face(self, photo=None, data=None, uid=None):
        """
        Generate a face.

        :param photo: The photo that will be attached to the face.
        :param data: The data that will be given to the face.
        :param uid: The UID of the newly created face.
        :return: The created face.
        :rtype: Face
        """
        photo = photo or self.mocker.MagicMock()
        data = data or self.mocker.MagicMock()
        f = Face(data, photo)
        if uid is not None:
            f.uid = uid
        photo.uid_to_face[uid] = f
        return f

    def faces(self, *uids):
        """
        Generate faces.

        :param list of str uids: the UIDs of the faces.
        :return: The created faces.
        :rtype: list
        """
        return [self.face(uid=uid) for uid in uids]

    def photo(self, *faces):
        """
        Generate photos.
        :param list of Face faces: The faces that will be attached to
            the photos
        :return: The created photos.
        :rtype: list of Photo
        """
        photo = Photo(None)
        photo.uid_to_face = {face.uid: face for face in faces}
        for face in faces:
            face.photo = photo
        return photo
