from nicegui import ui

from . import static_files
from .theme import TGZRTheme


class TGZRVisId:
    def __init__(self) -> None:
        static_files.register()
        self.logo_svg = static_files.get_asset_content("tgzr", "tgzr_logo.svg")
        self.theme = TGZRTheme()
        self._install()

    def _install(self):
        self._install_theme()
        self._install_css()
        self._install_anim()

    def _install_theme(self):
        ui.query(".nicegui-content").classes("p-0")
        ui.dark_mode().enable()

        ui.add_head_html(
            """
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Advent+Pro:ital,wght@0,100..900;1,100..900&family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap" rel="stylesheet">
        """
        )
        for type in (
            ui.label,
            ui.markdown,
            ui.link,
            ui.menu_item,
            ui.timeline,
            ui.item_label,
            ui.button,
            ui.tab,
        ):
            type.default_style(add='font-family: "Advent Pro";')
            type.default_classes("text-T tracking-widest")

        self.theme.apply()

    def _install_css(self):
        # font-awesome:
        ui.add_head_html(
            '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">'
        )

        # TGZR logo + logo_anim:
        logo_css = static_files.get_asset_ref("tgzr", "tgzr_logo.css")
        ui.add_head_html(
            # '<link rel="stylesheet" type="text/css" href="assets/tgzr/tgzr_logo.css"/>'
            f'<link rel="stylesheet" type="text/css" href="{logo_css}"/>'
        )
        logo_anim_css = static_files.get_asset_ref("tgzr", "tgzr_logo_anim.css")
        ui.add_head_html(
            # '<link rel="stylesheet" type="text/css" href="assets/tgzr/tgzr_logo_anim.css"/>'
            f'<link rel="stylesheet" type="text/css" href="{logo_anim_css}"/>'
        )

    def _install_anim(self):
        js = """
const containers = document.getElementsByClassName('tgzr_logo_container');
for (let container of containers) {
    // console.log(container);
    container.addEventListener('mousemove', (e) => {
        const elements = document.elementsFromPoint(e.clientX, e.clientY);
        
        // Remove hover from all
        document.querySelectorAll('.glow').forEach(el => {
            el.classList.remove('hovered');
        });
        
        // Add hover to all under cursor
        elements.forEach(el => {
            // console.log('-----');
            if (el.classList.contains('glow')) {
                el.classList.add('hovered');
                // console.log(el);
            }
        });
    });

    container.addEventListener('mouseleave', () => {
        // console.log('REMOVE');
        document.querySelectorAll('.glow').forEach(el => {
            el.classList.remove('hovered');
        });
    });
};
    """
        ui.run_javascript(js)

    def logo(self, classes="w-12"):
        ui.html(self.logo_svg, sanitize=False).classes(classes)

    def front_logo(self, w="800px", h="600px"):
        if w.endswith("px"):
            w = f"[{w}]"

        if h.endswith("px"):
            h = f"[{h}]"

        with ui.row(align_items="center").classes(f"w-{w} h-{h} bg-B"):
            ui.space()
            with ui.row(align_items="end").classes("w-full xh-2/3 xborder"):
                ui.space()
                ui.html(self.logo_svg, sanitize=False).classes("w-[500px] -m-[75px]")
                ui.space()

            with ui.row().classes("w-full"):
                with ui.column(align_items="center").classes("w-full"):
                    with ui.row(align_items="center").classes(
                        "h-1/20 content-center -mt-14"
                    ):
                        ui.label("TGZR").classes(
                            "ml-[1.3em] tracking-[1.3em] text-7xl text-nowrap font-thin"
                        )
                    with ui.row(align_items="start").classes("xw-full h-1/20"):
                        ui.label("collaboration platform").classes(
                            "mt-[1em] ml-[1em] tracking-[1em] text-xl text-nowrap font-thin"
                        )
            ui.space()

    def icon(self, w="32px", h="32px"):
        if w.endswith("px"):
            w = f"[{w}]"

        if h.endswith("px"):
            h = f"[{h}]"

        with ui.column(align_items="center").classes(
            f"w-{w} h-{h} place-content-center bg-B"
        ):
            ui.html(self.logo_svg, sanitize=False).classes("w-12")

    def profile_pict(self, w="350px", h="350px"):
        if w.endswith("px"):
            w = f"[{w}]"

        if h.endswith("px"):
            h = f"[{h}]"

        with ui.column(align_items="center").classes(f"w-{w} h-{h} bg-B"):
            ui.html(self.logo_svg, sanitize=False).classes("w-[500px] -m-[75px]")

    def banner_1(self, w="1400px", h="350px"):
        if w.endswith("px"):
            w = f"[{w}]"

        if h.endswith("px"):
            h = f"[{h}]"

        with ui.column(align_items="center").classes(f"w-{w} h-{h} bg-B"):
            ui.html(self.logo_svg, sanitize=False).classes("w-[500px] -m-[75px]")

    def banner_2(self, w="1400px", h="350px"):
        if w.endswith("px"):
            w = f"[{w}]"

        if h.endswith("px"):
            h = f"[{h}]"

        with ui.row(wrap=False, align_items="center").classes(f"w-{w} h-{h} bg-B"):
            ui.space()
            with ui.column(align_items="center"):
                ui.html(self.logo_svg, sanitize=False).classes("w-[500px] -m-[75px]")
            ui.space()
            with ui.column().classes("w-[1/3] "):
                ui.label("TGZR").classes(
                    "tracking-[1.3em] text-9xl text-nowrap font-thin "
                )
                ui.label("collaboration platform").classes(
                    "mt-[1em] ml-[1em] tracking-[1.07em] text-2xl text-nowrap font-thin"
                )
            ui.space()
