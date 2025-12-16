from typing import Tuple, Union

from bluer_algo.tracker.classes.generic import GenericTracker
from bluer_algo.tracker.classes.camshift import CamShiftTracker
from bluer_algo.tracker.classes.klt import KLTTracker
from bluer_algo.tracker.classes.meanshift import MeanShiftTracker
from bluer_algo.logger import logger

LIST_OF_TRACKER_ALGO = sorted(
    [
        CamShiftTracker.algo,
        KLTTracker.algo,
        MeanShiftTracker.algo,
    ]
)


def get_tracker_class(algo: str) -> Tuple[
    bool,
    Union[type[GenericTracker], None],
]:
    if algo == "camshift":
        return True, CamShiftTracker

    if algo == "klt":
        return True, KLTTracker

    if algo == "meanshift":
        return True, MeanShiftTracker

    logger.error(f"algo: {algo} not found.")
    return False, None
