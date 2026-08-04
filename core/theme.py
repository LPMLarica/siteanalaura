from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:

    BACKGROUND = "#F8F6F8"

    SIDEBAR = "#FFFDFE"

    PRIMARY = "#D98CA8"

    PRIMARY_HOVER = "#C97896"

    PRIMARY_LIGHT = "#F7DDE7"

    SECONDARY = "#EADFE5"

    CARD = "#FFFFFF"

    TEXT = "#404040"

    SUBTITLE = "#6E6E73"

    SUCCESS = "#A8D5BA"

    WARNING = "#FFE3A9"

    ERROR = "#F3B4B4"

    BORDER = "#E9E4E7"

    SHADOW = "rgba(90,90,90,0.08)"


theme = Theme()