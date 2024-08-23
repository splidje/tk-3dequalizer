import tde4


class TDE3DModel(object):
    def __init__(self, point_group, _3d_model_id):
        self._point_group = point_group
        self._3d_model_id = _3d_model_id

    @property
    def id_(self):
        return self._3d_model_id

    @property
    def name(self):
        return tde4.get3DModelName(self._3d_model_id)

    @name.setter
    def name(self, value):
        tde4.set3DModelName(self._point_group.id_, self._3d_model_id, value)

    @property
    def path(self):
        return tde4.get3DModelFilepath(self._point_group.id_, self._3d_model_id)

    def import_obj(self, path):
        tde4.importOBJ3DModel(self._point_group.id_, self._3d_model_id, path)

    @property
    def rotate_scale_matrix(self):
        return tde4.get3DModelRotationScale3D(self._point_group.id_, self._3d_model_id)

    @rotate_scale_matrix.setter
    def rotate_scale_matrix(self, value):
        return tde4.set3DModelRotationScale3D(
            self._point_group.id_, self._3d_model_id, value
        )

    @property
    def survey_flag(self):
        return tde4.get3DModelSurveyFlag(self._point_group.id_, self._3d_model_id)

    @survey_flag.setter
    def survey_flag(self, value):
        tde4.set3DModelSurveyFlag(self._point_group.id_, self._3d_model_id, value)

    @property
    def vertex_count(self):
        return tde4.get3DModelNoVertices(self._point_group.id_, self._3d_model_id)

    def add_vertex(self, vertex):
        tde4.add3DModelVertex(self._point_group.id_, self._3d_model_id, list(vertex))

    def add_face(self, vertex_indices):
        tde4.add3DModelFace(self._point_group.id_, self._3d_model_id, vertex_indices)

    def add_line(self, vertex_indices):
        tde4.add3DModelLine(self._point_group.id_, self._3d_model_id, vertex_indices)

    @staticmethod
    def create(point_group):
        _3d_model_id = tde4.create3DModel(point_group.id_)
        return TDE3DModel(point_group, _3d_model_id)
