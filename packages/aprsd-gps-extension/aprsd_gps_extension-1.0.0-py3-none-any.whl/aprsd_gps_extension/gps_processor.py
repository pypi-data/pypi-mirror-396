"""
GPS data processing module for APRS smart beaconing.

This module implements logic to determine when to send position reports
based on movement thresholds and time windows.

GPS data is expected to be in gpsdclient dict format (TPV messages).
"""

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Position:
    """Represents a GPS position with timestamp."""

    latitude: float
    longitude: float
    altitude: Optional[float] = None
    timestamp: Optional[datetime] = None


class SmartBeaconProcessor:
    """
    Processes GPS data for APRS smart beaconing.

    Implements the logic: only report position if there has been
    more than the configured distance threshold of movement within
    the configured time window. Thresholds are configurable via
    constructor parameters or per-call overrides.
    """

    def __init__(
        self, distance_threshold_feet: float = 20.0, time_window_minutes: float = 5.0
    ):
        """
        Initialize the smart beacon processor.

        Args:
            distance_threshold_feet: Minimum distance change in feet to trigger beacon
            time_window_minutes: Time window in minutes for checking movement
        """
        self.distance_threshold_feet = distance_threshold_feet
        self.time_window_minutes = time_window_minutes
        self.last_reported: Optional[Position] = None

    def haversine_distance_feet(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """
        Calculate the distance between two points on Earth using Haversine formula.

        Args:
            lat1, lon1: First point (latitude, longitude in degrees)
            lat2, lon2: Second point (latitude, longitude in degrees)

        Returns:
            Distance in feet
        """
        # Earth's radius in feet
        R = 20902231.0  # Earth radius in feet (approximately 3959 miles * 5280)

        # Convert latitude and longitude from degrees to radians
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        # Haversine formula
        a = (
            math.sin(delta_phi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # Distance in feet
        distance_feet = R * c
        return distance_feet

    def extract_position(self, gps_data: dict) -> Optional[Position]:
        """
        Extract position from GPS data.

        Expects gpsdclient dict format (TPV message from GPSD).

        Args:
            gps_data: GPS data dict from gpsdclient (TPV message format).
                     Expected keys: 'lat', 'lon', optionally 'alt', 'time'

        Returns:
            Position object or None if position data is unavailable
        """
        try:
            if not isinstance(gps_data, dict):
                return None

            lat = gps_data.get("lat")
            lon = gps_data.get("lon")

            if lat is not None and lon is not None:
                return Position(
                    latitude=lat,
                    longitude=lon,
                    altitude=gps_data.get("alt"),
                    timestamp=gps_data.get("time"),
                )
        except (KeyError, TypeError):
            pass

        return None

    def should_beacon(
        self,
        gps_data: dict,
        distance_threshold_feet: Optional[float] = None,
        time_window_minutes: Optional[float] = None,
    ) -> tuple[bool, Optional[float]]:
        """
        Determine if a position should be reported based on smart beaconing logic.

        Returns True if:
        - Position has moved more than distance_threshold_feet
        - AND it's been less than time_window_minutes since last report

        Args:
            gps_data: GPS data dict from gpsdclient (TPV message format)
            distance_threshold_feet: Minimum distance change in feet to trigger beacon.
                                    If None, uses the value from __init__ (default: None)
            time_window_minutes: Time window in minutes for checking movement.
                                If None, uses the value from __init__ (default: None)

        Returns:
            Tuple of (should_beacon: bool, distance_feet: Optional[float])
            distance_feet is None if position is unavailable
        """
        # Use provided parameters or fall back to instance defaults
        distance_threshold = (
            distance_threshold_feet
            if distance_threshold_feet is not None
            else self.distance_threshold_feet
        )
        time_window = (
            time_window_minutes
            if time_window_minutes is not None
            else self.time_window_minutes
        )

        current_position = self.extract_position(gps_data)

        if current_position is None:
            return False, None

        # No previous position - always report the first one
        if self.last_reported is None:
            self.last_reported = current_position
            return True, 0.0

        # Calculate distance from last reported position
        distance_feet = self.haversine_distance_feet(
            self.last_reported.latitude,
            self.last_reported.longitude,
            current_position.latitude,
            current_position.longitude,
        )

        # Get current time (use timestamp from GPS data if available, otherwise now)
        current_time = current_position.timestamp or datetime.now()
        last_time = self.last_reported.timestamp or datetime.now()

        # Calculate time difference
        time_diff = current_time - last_time
        time_diff_minutes = time_diff.total_seconds() / 60.0

        # Check if we should beacon:
        # 1. Distance threshold met
        # 2. Within time window (less than time_window_minutes since last report)
        should_beacon = (
            distance_feet >= distance_threshold and time_diff_minutes <= time_window
        )

        # If we're beaconing, update last reported position
        if should_beacon:
            self.last_reported = current_position

        return should_beacon, distance_feet

    def reset(self):
        """Reset the processor (clear last reported position)."""
        self.last_reported = None


# Convenience function for easy use
def should_beacon_position(
    gps_data: dict, distance_threshold_feet: float, time_window_minutes: float
) -> tuple[bool, Optional[float]]:
    """
    Convenience function to check if position should be beaconed.

    Note: This creates a new processor instance for each call.
    For stateful processing across multiple calls, use SmartBeaconProcessor directly
    or get_smart_beacon_processor().

    Args:
        gps_data: GPS data dict from gpsdclient (TPV message format)
        distance_threshold_feet: Minimum distance change in feet (required)
        time_window_minutes: Time window in minutes (required)

    Returns:
        Tuple of (should_beacon: bool, distance_feet: Optional[float])
    """
    processor = SmartBeaconProcessor(
        distance_threshold_feet=distance_threshold_feet,
        time_window_minutes=time_window_minutes,
    )
    return processor.should_beacon(gps_data)


# For use with persistent processor instance
_global_processor: Optional[SmartBeaconProcessor] = None
_global_distance_threshold: Optional[float] = None
_global_time_window: Optional[float] = None


def get_smart_beacon_processor(
    distance_threshold_feet: float,
    time_window_minutes: float,
    force_reset: bool = False,
) -> SmartBeaconProcessor:
    """
    Get or create a global smart beacon processor instance.

    This maintains state across multiple calls, tracking the last
    reported position over time. If parameters differ from the existing
    instance, a new instance will be created (unless force_reset=False).

    Args:
        distance_threshold_feet: Minimum distance change in feet (required)
        time_window_minutes: Time window in minutes (required)
        force_reset: If True, always create a new processor (default: False)

    Returns:
        SmartBeaconProcessor instance
    """
    global _global_processor, _global_distance_threshold, _global_time_window

    # Check if we need to create a new processor
    if (
        force_reset
        or _global_processor is None
        or _global_distance_threshold != distance_threshold_feet
        or _global_time_window != time_window_minutes
    ):
        _global_processor = SmartBeaconProcessor(
            distance_threshold_feet=distance_threshold_feet,
            time_window_minutes=time_window_minutes,
        )
        _global_distance_threshold = distance_threshold_feet
        _global_time_window = time_window_minutes

    return _global_processor


def reset_global_processor():
    """Reset the global smart beacon processor instance."""
    global _global_processor, _global_distance_threshold, _global_time_window
    _global_processor = None
    _global_distance_threshold = None
    _global_time_window = None
