from typing import Tuple, Any, Optional
import numpy as np
import cv2

from bluer_algo.tracker.classes.generic import GenericTracker
from bluer_algo.logger import logger


class KLTTracker(GenericTracker):
    algo = "klt"

    def __init__(
        self,
        with_gui: bool = False,
    ):
        super().__init__(with_gui)

        # Internal state
        self.initialized: bool = False
        self.bbox: Optional[Tuple[float, float, float, float]] = None  # (x, y, w, h)
        self.prev_gray: Optional[np.ndarray] = None
        self.points: Optional[np.ndarray] = None  # Nx1x2 float32

        # Shi–Tomasi corner params
        self.feature_params = dict(
            maxCorners=100,
            qualityLevel=0.01,
            minDistance=7,
            blockSize=7,
        )

        # Lucas–Kanade optical flow params
        self.lk_params = dict(
            winSize=(21, 21),
            maxLevel=3,
            criteria=(
                cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
                30,
                0.01,
            ),
        )

        # If tracked points drop below this, we re-detect
        self.min_points: int = 10

    # ------------------------------------------------------------------ #
    # internal helpers
    # ------------------------------------------------------------------ #

    def _detect_points_in_bbox(
        self,
        gray: np.ndarray,
        bbox: Tuple[float, float, float, float],
    ) -> Optional[np.ndarray]:
        x, y, w, h = [int(v) for v in bbox]
        x = max(x, 0)
        y = max(y, 0)

        roi = gray[y : y + h, x : x + w]
        if roi.size == 0:
            logger.warning("KLTTracker: ROI has zero size in _detect_points_in_bbox.")
            return None

        p = cv2.goodFeaturesToTrack(roi, mask=None, **self.feature_params)
        if p is None:
            logger.warning("KLTTracker: goodFeaturesToTrack found no points.")
            return None

        # Shift ROI coordinates to full-frame coords
        p[:, 0, 0] += x
        p[:, 0, 1] += y
        return p

    def _draw_on_frame(
        self,
        frame: np.ndarray,
        bbox_int: Tuple[int, int, int, int],
    ) -> np.ndarray:
        """
        Draw bbox (and optionally points) on a copy of the frame
        if with_gui=True; otherwise just return the original frame.
        """
        x, y, w, h = bbox_int
        vis = frame.copy()

        for i in range(len(self.history) - 1):
            cv2.line(
                vis,
                self.history[i],
                self.history[i + 1],
                color=(0, 255, 0),
                thickness=2,
            )

        # Draw bbox
        vis = cv2.rectangle(
            vis,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2,
        )

        # Draw tracked points if available
        if self.points is not None and len(self.points) > 0:
            for pt in self.points.reshape(-1, 2):
                cx, cy = int(pt[0]), int(pt[1])
                vis = cv2.circle(vis, (cx, cy), 2, (0, 0, 255), -1)

        return vis

    # ------------------------------------------------------------------ #
    # GenericTracker API
    # ------------------------------------------------------------------ #

    def start(
        self,
        frame: np.ndarray,
        track_window: Tuple[int, int, int, int],
    ):
        """
        Initialize the KLT tracker with an initial frame and track window.
        track_window: (x, y, w, h)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        bbox = tuple(float(v) for v in track_window)

        points = self._detect_points_in_bbox(gray, bbox)
        if points is None:
            logger.error("KLTTracker.start: could not find features in initial window.")
            self.initialized = False
            self.bbox = bbox
            self.prev_gray = gray
            self.points = None
            return

        self.prev_gray = gray
        self.points = points
        self.bbox = bbox
        self.initialized = True

        logger.info(
            f"KLTTracker.start: initialized with {len(points)} points in bbox {bbox}."
        )

    def track(
        self,
        frame: np.ndarray,
        track_window: Tuple[int, int, int, int],
        log: bool = False,
    ) -> Tuple[
        Any,  # here: always None (no extra metadata)
        Tuple[int, int, int, int],  # updated track_window (x, y, w, h)
        np.ndarray,  # full image with track_window rendered
    ]:
        """
        Track the object in the new frame.

        Returns:
            None                      -> placeholder for metadata
            track_window: (x, y, w, h)
            image: full frame (BGR), with track_window rendered if with_gui=True
        """
        if not self.initialized:
            # First call: initialize from given track_window
            self.start(frame, track_window)

        if self.bbox is None:
            # Can't do much; just return the given window and frame
            x, y, w, h = track_window
            out_frame = self._draw_on_frame(frame, (x, y, w, h))
            return None, (x, y, w, h), out_frame

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # If we have no points (e.g., init failed), attempt re-detect
        if self.points is None or len(self.points) == 0:
            logger.info(f"{self.algo}: no points; attempting re-detect.")
            points = self._detect_points_in_bbox(gray, self.bbox)
            if points is None:
                x, y, w, h = [int(v) for v in self.bbox]
                out_frame = self._draw_on_frame(frame, (x, y, w, h))
                return None, (x, y, w, h), out_frame

            self.points = points
            self.prev_gray = gray
            x, y, w, h = [int(v) for v in self.bbox]
            out_frame = self._draw_on_frame(frame, (x, y, w, h))
            return None, (x, y, w, h), out_frame

        # Optical flow
        p1, st, err = cv2.calcOpticalFlowPyrLK(
            self.prev_gray,
            gray,
            self.points,
            None,
            **self.lk_params,
        )
        logger.info(f"optical flow error: {err}")

        if p1 is None or st is None:
            logger.warning(f"{self.algo}: calcOpticalFlowPyrLK returned None.")
            x, y, w, h = [int(v) for v in self.bbox]
            out_frame = self._draw_on_frame(frame, (x, y, w, h))
            return None, (x, y, w, h), out_frame

        st = st.reshape(-1)
        valid_mask = st == 1

        if not np.any(valid_mask):
            logger.info(f"{self.algo}: no valid tracked points.")
            x, y, w, h = [int(v) for v in self.bbox]
            out_frame = self._draw_on_frame(frame, (x, y, w, h))
            return None, (x, y, w, h), out_frame

        # Shapes: (M, 1, 2) -> (M, 2)
        good_new = p1[valid_mask].reshape(-1, 2)
        good_old = self.points[valid_mask].reshape(-1, 2)

        if len(good_new) < self.min_points:
            logger.info(f"{self.algo}: too few points ({len(good_new)}), re-detecting.")
            points = self._detect_points_in_bbox(gray, self.bbox)
            if points is None:
                x, y, w, h = [int(v) for v in self.bbox]
                out_frame = self._draw_on_frame(frame, (x, y, w, h))
                return None, (x, y, w, h), out_frame

            self.points = points
            self.prev_gray = gray
            x, y, w, h = [int(v) for v in self.bbox]
            out_frame = self._draw_on_frame(frame, (x, y, w, h))
            return None, (x, y, w, h), out_frame

        # Compute median motion
        dx = float(np.median(good_new[:, 0] - good_old[:, 0]))
        dy = float(np.median(good_new[:, 1] - good_old[:, 1]))

        x, y, w, h = self.bbox
        x += dx
        y += dy

        # Clamp to frame bounds
        h_img, w_img = gray.shape[:2]
        x = float(max(0, min(x, w_img - w)))
        y = float(max(0, min(y, h_img - h)))

        self.bbox = (x, y, w, h)

        # Store updated points back in (N, 1, 2) format
        self.points = good_new.reshape(-1, 1, 2).astype(np.float32)
        self.prev_gray = gray

        x_i, y_i, w_i, h_i = [int(v) for v in self.bbox]

        self.history.append(
            (
                x_i + w_i // 2,
                y_i + h_i // 2,
            )
        )

        logger.info(
            f"{self.algo}: bbox -> x={x_i}, y={y_i}, w={w_i}, h={h_i}, "
            f"points={len(self.points)}"
        )

        # draw track_window on image
        output_image = np.array([])
        if self.with_gui or log:
            output_image = self._draw_on_frame(frame, (x_i, y_i, w_i, h_i))

        return None, (x_i, y_i, w_i, h_i), output_image
