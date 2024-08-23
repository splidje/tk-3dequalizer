import tde4
from vl_sdv import rot3d, mat3d, VL_APPLY_ZXY

from ._3d_model import TDE3DModel


#######
# POINT


class TDEPoint(object):
    def __init__(self, group, point_id):
        self._group = group
        self._point_id = point_id

    @property
    def id_(self):
        return self._point_id

    @property
    def name(self):
        return tde4.getPointName(self._group.id_, self._point_id)

    @name.setter
    def name(self, val):
        tde4.setPointName(self._group.id_, self._point_id, val)

    @property
    def is_calculated_3d(self):
        return tde4.isPointCalculated3D(self._group.id_, self._point_id)

    @property
    def calc_position_3d(self):
        return tde4.getPointCalcPosition3D(self._group.id_, self._point_id)

    def get_mo_cap_calc_position_3d(self, cam, frame):
        return tde4.getPointMoCapCalcPosition3D(
            self._group.id_, self._point_id, cam.id_, frame
        )

    def get_as_dict(self, cams):
        return dict(
            id=self.id_,
            name=self.name,
            is_calculated_3d=self.is_calculated_3d,
            calc_position_3d=self.calc_position_3d,
            mo_cap_calc_positions_3d={
                c.id_: [
                    self.get_mo_cap_calc_position_3d(c, f)
                    for f in range(1, c.frame_count + 1)
                ]
                for c in cams
            },
        )


#############
# POINT GROUP


class TDEPointGroup(object):
    def __init__(self, pg_id):
        self._pg_id = pg_id

    @property
    def id_(self):
        return self._pg_id

    @property
    def type_(self):
        return tde4.getPGroupType(self._pg_id)

    @property
    def name(self):
        return tde4.getPGroupName(self._pg_id)

    @name.setter
    def name(self, val):
        tde4.setPGroupName(self._pg_id, val)

    def get_position_3d(self, cam, frame):
        return tde4.getPGroupPosition3D(self._pg_id, cam.id_, frame)

    def get_rotation_3d(self, cam, frame):
        return tde4.getPGroupRotation3D(self._pg_id, cam.id_, frame)

    def get_rotation_3d_zxy(self, cam, frame):
        return rot3d(mat3d(self.get_rotation_3d(cam, frame))).angles(VL_APPLY_ZXY)

    @property
    def scale_3d(self):
        return tde4.getPGroupScale3D(self._pg_id)

    def get_as_dict(self, cams):
        return dict(
            id=self.id_,
            type=self.type_,
            name=self.name,
            scale_3d=self.scale_3d,
            positions_3d={
                c.id_: [self.get_position_3d(c, f) for f in range(1, c.frame_count + 1)]
                for c in cams
            },
            rotations_3d={
                c.id_: [self.get_rotation_3d(c, f) for f in range(1, c.frame_count + 1)]
                for c in cams
            },
            rotations_3d_zxy={
                c.id_: [
                    self.get_rotation_3d_zxy(c, f) for f in range(1, c.frame_count + 1)
                ]
                for c in cams
            },
            points=[p.get_as_dict(cams) for p in self.iter_points()],
        )

    @property
    def is_selected(self):
        return tde4.getPGroupSelectionFlag(self._pg_id) > 0

    @staticmethod
    def iter_selected():
        return (pg for pg in TDEPointGroup.iter_all() if pg.is_selected)

    def iter_points(self):
        return (TDEPoint(self, p) for p in tde4.getPointList(self._pg_id))

    def iter_3d_models(self):
        return (TDE3DModel(self, i) for i in tde4.get3DModelList(self._pg_id))

    def create_3d_model(self):
        return TDE3DModel.create(self)

    @staticmethod
    def iter_all():
        return (TDEPointGroup(i) for i in tde4.getPGroupList())

    @staticmethod
    def create():
        return TDEPointGroup(tde4.createPGroup("OBJECT"))
