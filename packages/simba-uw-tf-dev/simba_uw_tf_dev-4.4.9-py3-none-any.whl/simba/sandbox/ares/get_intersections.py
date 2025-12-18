from typing import Union, Optional
import os
import platform
from datetime import datetime
from simba.utils.checks import check_file_exist_and_readable, check_if_dir_exists
from simba.utils.read_write import get_fn_ext, read_pickle
from simba.sandbox.ares.ares_data_to_polygons import Ares2Polygons
from simba.mixins.geometry_mixin import GeometryMixin
from itertools import combinations
import multiprocessing

class GetIntersections():

    def __init__(self,
                 data_path: Union[str, os.PathLike],
                 save_path: Optional[Union[str, os.PathLike]] = None):

        check_file_exist_and_readable(file_path=data_path, raise_error=True)
        if save_path is not None:
            check_if_dir_exists(in_dir=os.path.dirname(save_path), source=self.__class__.__name__, raise_error=True)
            self.save_path = save_path
        else:
            data_dir, data_name, _ = get_fn_ext(filepath=data_path)
            self.save_path = os.path.join(data_dir, f'{data_name}_{datetime.now().strftime("%Y%m%d%H%M%S")}.pkl')
        self.data = read_pickle(data_path=data_path, verbose=False)
        if platform.system() == "Darwin":
            multiprocessing.set_start_method("spawn", force=True)

    def run(self):
        polygon_getter = Ares2Polygons(data=self.data, parallel_offset=20)
        polygon_getter.run()
        for (track_1, track_2) in combinations(polygon_getter.results.keys(), 2):
            shapes_1, shapes_2 = polygon_getter.results[track_1], polygon_getter.results[track_2]
            overlaps = GeometryMixin().multiframe_compute_shape_overlap(shape_1=shapes_1, shape_2=shapes_2, verbose=True)


if __name__ == "__main__":
    x = GetIntersections(data_path=r'/Users/simon/Desktop/envs/simba/simba/simba/sandbox/ares/ProcessedTracks.pkl')
    x.run()
