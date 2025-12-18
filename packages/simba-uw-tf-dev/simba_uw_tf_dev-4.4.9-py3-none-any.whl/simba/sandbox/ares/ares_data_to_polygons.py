import os
from typing import Union, Optional
import numpy as np
from simba.utils.read_write import read_pickle
from simba.utils.checks import check_valid_dict, check_int
from simba.mixins.geometry_mixin import GeometryMixin


class Ares2Polygons:

    def __init__(self,
                 data: Union[dict, str, os.PathLike],
                 parallel_offset: Optional[int] = 1):

        if isinstance(data, (str, os.PathLike)):
            self.data = read_pickle(data_path=data, verbose=False)
        else:
            check_valid_dict(x=data, valid_key_dtypes=(str,), valid_values_dtypes=(dict,))
            self.data = data
        check_int(name=f'{self.__class__.__name__} parallel_offset', value=parallel_offset, min_value=1)
        self.track_cnt, self.parallel_offset = len(self.data.keys()), parallel_offset

    def run(self):
        self.results = {}
        for track_cnt, (track_id, track_data) in enumerate(self.data.items()):
            track_points = [list(frame.values()) for frame in track_data.values()]
            max_bp_len = max([len(row) for row in track_points])
            padded = [row + [row[-1]] * (max_bp_len - len(row)) for row in track_points]
            track_arr = np.array([[[p.x, p.y] for p in row] for row in padded], dtype=np.int32)
            self.results[track_id] = GeometryMixin().bodyparts_to_polygon(data=track_arr, parallel_offset=self.parallel_offset)

x = Ares2Polygons(data=r'C:\projects\simba\simba\simba\sandbox\ares\ProcessedTracks.pkl')
x.run()