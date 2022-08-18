"""
Describe the content of the messages received from LoLas Module

Use a class called MsgElementDescription to standarize the description.
Then declare various instances for each type of message received.

Dictionnaries are then defined to map names, IDs and descritions.
"""

class MsgElementDescription:
    """
    Standard description for each internal element in the messsages

    Attributes
    ----------
    name : string
        name of the element
    nbr_of_bytes : int
        number of bytes representing the element in the raw bytes payload
    signed : bool
        signed or not
    units : string
        units of the element
    """
    def __init__(self, name, nbr_of_bytes, signed, units) -> None:
        self.name = name
        self.nbr_of_bytes = nbr_of_bytes
        self.signed = signed
        self.units = units

# --- (3) STATUS ---
# drone system health word      1 byte      (-)     unsigned
# ground system health word     1 byte      (-)     unsigned
# Time since boot               4 bytes     (ms)    unsigned
# Current mode                  1 byte      (-)     unsigned
# Role                          1 byte      (-)     unsigned
MSG_DESCRIPTION_STATUS = [
    MsgElementDescription("Drone_health", 1, False, "none"),
    MsgElementDescription("Ground_health", 1, False, "none"),
    MsgElementDescription("Time", 4, False, "ms"),
    MsgElementDescription("Mode", 1, False, "none"),
    MsgElementDescription("Role", 1, False, "none")
]

# --- (4) 3D POSITION ---
# X                             4 bytes     (mm)    signed
# Y                             4 bytes     (mm)    signed
# Z                             4 bytes     (mm)    signed
# yaw                           2 bytes     (deg)   unsigned
# Sigma XY                      2 bytes     (mm)    unsigned
# Sigma Z                       2 bytes     (mm)    unsigned
# Sigma yaw                     2 bytes     (mm)    unsigned
# Fusion health word            1 byte      (-)     unsigned
# IMU YAW                       2 bytes     (deg)   unsigned
# Yaw validation                1 byte      (-)     unsigned
MSG_DESCRIPTION_3DPOSITION = [
    MsgElementDescription("X", 4, True, "mm"),
    MsgElementDescription("Y", 4, True, "mm"),
    MsgElementDescription("Z", 4, True, "mm"),
    MsgElementDescription("Yaw", 2, False, "deg"),
    MsgElementDescription("Sigma_XY", 2, False, "mm"),
    MsgElementDescription("Sigma_Z", 2, False, "mm"),
    MsgElementDescription("Sigma_Yaw", 2, False, "mm"),
    MsgElementDescription("Fusion_health", 1, False, "none"),
    MsgElementDescription("IMU_Yaw", 2, False, "deg"),
    MsgElementDescription("Yaw_validation", 1, False, "none")
]

# --- (9) PROXIMITY ---
# weight_on_wheel               1 byte      (-)     unsigned
# proximity distance            2 bytes     (mm)    unsigned
# status                        1 byte      (-)     unsigned
MSG_DESCRIPTION_PROXIMITY = [
    MsgElementDescription("WoW", 1, False, "none"),
    MsgElementDescription("Distance", 2, False, "mm"),
    MsgElementDescription("Prox_status", 1, False, "none")
]

# Dictionary that links msg ID to their description
MSG_ID_TO_DESCRIPTION = {
    3 : MSG_DESCRIPTION_STATUS,
    4 : MSG_DESCRIPTION_3DPOSITION,
    9 : MSG_DESCRIPTION_PROXIMITY
}

# Dictionary that links msg IDs to their names
MSG_ID_TO_NAMES = {
    3 : "Status",
    4 : "3D_Position",
    9 : "Proximity"
}

# Build the reverse dictionary, that links msg names to their IDs
MSG_NAME_TO_IDS = {v: k for k, v in MSG_ID_TO_NAMES.items()}
