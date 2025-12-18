import dataclasses

from nicegui import ui


@dataclasses.dataclass
class Theme:
    primary: str = "#5898d4"
    secondary: str = "#26a69a"
    accent: str = "#9c27b0"
    dark: str = "#1d1d1d"
    dark_page: str = "#121212"
    positive: str = "#21ba45"
    negative: str = "#c10015"
    info: str = "#31ccec"
    warning: str = "#f2c037"

    C: str = "#00FFFF"
    M: str = "#FF00FF"
    Y: str = "#FFFF00"
    W: str = "#DEEDEE"
    B: str = dark_page
    T: str = "#b7b7b7"

    def apply(self):
        self.B = self.dark_page
        colors = ui.colors(
            primary=self.primary,
            secondary=self.secondary,
            accent=self.accent,
            dark=self.dark,
            dark_page=self.dark_page,
            positive=self.positive,
            negative=self.negative,
            info=self.info,
            warning=self.warning,
            C=self.C,
            M=self.M,
            Y=self.Y,
            W=self.W,
            B=self.B,
            T=self.T,
        )
        # print(f"{colors._props['primary']=}")
        # print(f"{colors._props['secondary']=}")
        # print(f"{colors._props['accent']=}")
        # print(f"{colors._props['dark']=}")
        # print(f"{colors._props['dark_page']=}")
        # print(f"{colors._props['positive']=}")
        # print(f"{colors._props['negative']=}")
        # print(f"{colors._props['info']=}")
        # print(f"{colors._props['warning']=}")
        # print(f"{colors._props['customColors']=}")

    def cycled_color_name(self, index: int) -> str:
        colors = ["C", "M", "Y"]  # [self.C, self.M, self.Y]
        return colors[index % len(colors)]


class TGZRTheme(Theme):
    def __init__(self):
        super().__init__(dark_page="#222222")
