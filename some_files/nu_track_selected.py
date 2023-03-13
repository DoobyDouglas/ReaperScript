import reapy

project = reapy.Project()
project.add_track(1)
project.unselect_all_tracks()
project.tracks[1].select()
