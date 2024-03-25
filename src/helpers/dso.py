from typing import Tuple, Union

import numpy as np
from pyongc import ongc

from helpers import uid


def ra_time_to_hours(time_input: Union[str, np.ndarray]) -> Tuple[bool, Union[float, str]]:
    """Turn RA time such as `20:59:17.14` or array such as `array([20.  , 59.  , 17.14])` into RA hours such as `20.9881`.

    Args:
        time_input (Union[str, np.ndarray]): RA time as H:M:S string or array

    Returns:
        Tuple[bool, Union[float, str]]: Bool is success, float is RA hours, if str means error
    """
    try:
        if isinstance(time_input, str):
            hours, minutes, seconds = map(float, time_input.split(":"))
        elif isinstance(time_input, np.ndarray):
            if len(time_input) != 3:
                raise ValueError("Input array must have three elements (H, M, S).")
            hours, minutes, seconds = time_input
        else:
            raise TypeError("Input must be a string or a numpy array.")
        
        total_hours = hours + (minutes / 60) + (seconds / 3600)
        return (True, total_hours)
    except Exception as e:
        return (False, str(e))


def declination_to_degrees(
    declination_input: Union[str, np.ndarray],
) -> Tuple[bool, Union[np.ndarray, str]]:
    """Converts declination of format type (+44:31:43.6) or array([44. , 31. , 43.6]) to decimal degrees.

    Args:
        declination_input (Union[str, np.ndarray]): Declination in sexagesimal format as string or array

    Returns:
        Tuple[bool, Union[np.ndarray, str]]: Bool is success, float is decimal degrees, if str means error
    """
    try:
        if isinstance(declination_input, str):
            degrees, minutes, seconds = declination_input.split(":")
            sign_multiplier = 1 if degrees[0] == "+" else -1
            degrees = float(degrees)
            minutes = float(minutes)
            seconds = float(seconds)
        elif isinstance(declination_input, np.ndarray):
            if len(declination_input) != 3:
                raise ValueError("Input array must have three elements (D, M, S).")
            sign_multiplier = np.where(declination_input[0] >= 0, 1, -1)
            degrees, minutes, seconds = declination_input
        else:
            raise TypeError("Input must be a string or a numpy array.")

        total_degrees = sign_multiplier * (
            np.abs(degrees) + (minutes / 60) + (seconds / 3600)
        )
        return (True, total_degrees)
    except Exception as e:
        return (False, str(e))


def object_name_to_coordinates(
    name: str,
) -> tuple[bool, float, float, Union[str, None]]:
    """Gets the ra houts, dec degrees coordinates of a DSO object.

    Args:
        name (str): Name of the deep space object.

    Returns:
        tuple[bool, float, float, Union[str, None]]: success, ra hours, dec degrees, error if any
    """
    dso = ongc.get(name)
    if dso is None:
        return (False, 0.0, 0.0, f"DSO '{name}' was not found.")

    coords = dso.coords
    # RA: HMS
    # Dec: DMS

    ra = ra_time_to_hours(coords[0])
    dec = declination_to_degrees(coords[1])

    return (True, ra, dec)


def get_object_image_from_coords(fov: float, ra_hours: float, dec: float) -> str:
    """Get a URL to an image of the ra hours, dec coordinates.

    Args:
        fov (float): FOV
        ra_hours (float): RA in hours
        dec (float): Dec in decimal degrees

    Returns:
        str: The URL to the image
    """
    discord_cache_bypass = uid.gen()
    return f"http://www.sky-map.org/imgcut?survey=DSS2&img_id=all&angle={fov}&ra={ra_hours}&de={dec}&width=800&height=800&projection=tan&interpolation=bicubic&jpeg_quality=.8&{discord_cache_bypass}={discord_cache_bypass}"
