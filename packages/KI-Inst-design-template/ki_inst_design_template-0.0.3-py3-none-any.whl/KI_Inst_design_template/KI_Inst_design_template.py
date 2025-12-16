import matplotlib.pyplot as plt
from cycler import cycler
import os
import matplotlib.image as mpimg
import matplotlib.transforms as transform
import textwrap
from pathlib import Path
from matplotlib import font_manager
import warnings
import sys
from importlib.resources import files

# Add Suisse Fonts
user_home = os.path.expanduser("~")
search_dirs = []

if sys.platform.startswith("win"):
    search_dirs = [
        os.path.join(os.getenv('LOCALAPPDATA'), "Microsoft", "Windows", "Fonts"),
        r"C:\Windows\Fonts"
    ]
elif sys.platform.startswith("linux"):
    search_dirs = [
        os.path.join(user_home, ".local", "share", "fonts"),
        os.path.join(user_home, ".fonts"),
        "/usr/share/fonts"
    ]
elif sys.platform == "darwin":
    search_dirs = [
        os.path.join(user_home, "Library", "Fonts"),
        "/Library/Fonts",
        "/System/Library/Fonts"
    ]

def find_path(filename):
    for d in search_dirs:
        p = Path(d)
        if p.exists():
            # rglob handles nested folders (Linux) and flats (Windows)
            matches = list(p.rglob(filename))
            if matches: return matches[0]
    return Path(filename) # Fallback to current dir

intl_medium_path = find_path("SuisseIntl-Medium.ttf")
mono_regular_path = find_path("SuisseIntlMono-Regular.ttf")
intl_regular_path = find_path("SuisseIntl-Regular.ttf")

intl_medium_font_big = font_manager.FontProperties(fname=intl_medium_path, size=15)
intl_medium_font_small = font_manager.FontProperties(fname=intl_medium_path, size=7)
mono_regular_font = font_manager.FontProperties(fname=mono_regular_path, size=5)
intl_regular_font = font_manager.FontProperties(fname=intl_regular_path, size=7)

# === Kiel Institute COLOR PALETTE ===================

KIEL_BRAND_COLORS = {
    "kiel_blue": "#194ABB",    
    "kiel_orange": "#FF6A00",  
}

KIEL_BLUE_TINTS = {
    "kiel_blue_80": "#4169C3",  
    "kiel_blue_60": "#9BADD5",  
    "kiel_blue_40": "#C8CFDE",  
    "kiel_blue_20": "#DFE0E3"   
}

KIEL_ORANGE_TINTS = {
    "kiel_orange_80": "#FAAE74",  
    "kiel_orange_60": "#F7CFAD",  
    "kiel_orange_40": "#F6E0CA",  
    "kiel_orange_20": "#F6E9D9"   
}

KIEL_BLUE_SPECTRUM = {
    "kiel_blue_01": "#304DC3",  
    "kiel_blue_02": "#43A1FF",  
    "kiel_blue_03": "#32C2FF",  
    "kiel_blue_04": "#3083C3",  
    "kiel_blue_05": "#43D9FF",  
    "kiel_blue_06": "#43F2FF",  
    "kiel_blue_07": "#1B48FF",  
    "kiel_blue_08": "#2E89FF",  
    "kiel_blue_09": "#4372FF",  
    "kiel_blue_10": "#0032FF",  
    "kiel_blue_11": "#007FFF",  
    "kiel_blue_12": "#00CCFF"   
}

KIEL_SECONDARY_COLORS = {
    "kiel_red": "#CC3333",       
    "kiel_green": "#33CC3D",    
    "kiel_turquoise": "#33C9CC", 
    "kiel_purple": "#7033CC",    
    "kiel_pink": "#CC339C"       
}

# Create a single master dictionary for lookup
KIEL_COLORS = {
    **KIEL_BRAND_COLORS,
    **KIEL_BLUE_TINTS,
    **KIEL_ORANGE_TINTS,
    **KIEL_BLUE_SPECTRUM,
    **KIEL_SECONDARY_COLORS
}

# Define the default order for the matplotlib cycler
DEFAULT_COLOR_ORDER = [
    "kiel_blue",
    "kiel_orange",
    "kiel_turquoise", 
    "kiel_red",
    "kiel_green",
    "kiel_purple",
    "kiel_pink"
]

def show_kiel_institute_colors():
    """
    Displays all available Kiel Institute color palettes in a plot.
    """
    palettes = {
        "Brand Colors": KIEL_BRAND_COLORS,
        "Blue Tints": KIEL_BLUE_TINTS,
        "Orange Tints": KIEL_ORANGE_TINTS,
        "Blue Spectrum": KIEL_BLUE_SPECTRUM,
        "Secondary Colors": KIEL_SECONDARY_COLORS,
    }
    
    # Use the theme's font settings if available
    
    fig, axs = plt.subplots(nrows=len(palettes), figsize=(12, len(palettes) * 1.4), 
                            constrained_layout=True)
    fig.suptitle('Kiel Institute Color Pallette',
                 fontproperties=intl_medium_font_big) # Title 

    for i, (title, colors) in enumerate(palettes.items()):
        ax = axs[i]
        n = len(colors)
        ax.set_title(title, loc='left', fontproperties=intl_medium_font_big) # Palette titles
        
        for j, (name, hex_code) in enumerate(colors.items()):
            # Add color patch
            ax.add_patch(plt.Rectangle((j, 0.3), 1, 0.7, color=hex_code))
            # Add name
            ax.text(j + 0.5, 0.15, name, ha='center', va='top', 
                    fontproperties=intl_medium_font_small) # Names 
            # Add hex code
            ax.text(j + 0.5, 0.0, hex_code, ha='center', va='top', 
                    fontproperties=mono_regular_font) # Hex 
        
        ax.set_xlim(0, n)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
    plt.show()

def palette_kiel_institute(color_names=None, n=None):
    """
    Returns a list of hex codes from the Kiel Institute palette.

    Args:
        color_names (list, optional): 
            A list of color names (e.g., ["blue", "red", "blau_01"]).
            If None, uses the DEFAULT_COLOR_ORDER.
        n (int, optional): 
            The total number of colors desired. If n is greater than
            the number of colors in the list, the list will be repeated.
    """
    base_colors_hex = []
    
    if color_names is None:
        base_colors_hex = [KIEL_COLORS[name] for name in DEFAULT_COLOR_ORDER]
    else:
        for name in color_names:
            hex_code = KIEL_COLORS.get(name)
            if hex_code:
                base_colors_hex.append(hex_code)
            else:
                print(f"Warning: Color '{name}' not in KIEL_COLORS. Skipping.")

    if not base_colors_hex:
        print("Error: No valid colors specified. Returning default blue.")
        base_colors_hex = [KIEL_COLORS["blue"]]

    if n is None:
        return base_colors_hex
    else:
        repeats = (n + len(base_colors_hex) - 1) // len(base_colors_hex)
        return (base_colors_hex * repeats)[:n]


# === Kiel Institute MATPLOTLIB THEME ==========================================

def init_kiel_institute_theme():
    """
    Apply the Kiel Institute theme to matplotlib globally.
    """
    print("Applying Kiel Institute visual theme for matplotlib...")
    
    BG_COLOR = "#F5F1E7"
    TEXT_COLOR = "#000000"

    font_manager.fontManager.addfont(mono_regular_path)
    prop = font_manager.FontProperties(fname=mono_regular_path)
    FONT = prop.get_name()

    plt.rcParams.update({
        # --- Figure ---
        "figure.facecolor": BG_COLOR,
        "figure.figsize": (8, 6),
        "figure.autolayout": False,

        # --- Colors & grids ---
        "axes.prop_cycle": cycler(color=palette_kiel_institute()),
        "axes.facecolor": BG_COLOR,
        "axes.edgecolor": TEXT_COLOR,
        "axes.grid": True,
        "grid.color": TEXT_COLOR,
        "grid.linestyle": "-",
        "grid.linewidth": 0.5,

        # --- Spines ---
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": True,
        "axes.spines.bottom": True,

        # --- Fonts & text ---
        "font.family": FONT, # Default for all text
        "font.size": 15,
        "text.color": TEXT_COLOR,
        
        # --- CHANGE ---
        # Set plot titles and labels to bold
        # They will use the default font 
        "axes.titleweight": "bold", 
        "axes.labelweight": "bold", 
        
        "axes.titlesize": 15,
        "axes.titlecolor": TEXT_COLOR,
        "axes.labelsize": 15,
        "axes.labelcolor": TEXT_COLOR,
        "xtick.color": TEXT_COLOR,
        "ytick.color": TEXT_COLOR,
        "xtick.labelsize": 15,
        "ytick.labelsize": 15,

        # --- Lines & markers ---
        "lines.linewidth": 2,
        "lines.markersize": 6,

        # --- Legend ---
        "legend.frameon": True,
        "legend.framealpha": 1.0,
        "legend.edgecolor": TEXT_COLOR,
        "legend.facecolor": BG_COLOR,
        "legend.loc": "best",
        "legend.fancybox": False,

        # --- Save settings ---
        "savefig.facecolor": BG_COLOR,
        "savefig.dpi": 150
    })

    print("Kiel Institute matplotlib theme applied successfully.")


# === OPTIONAL: SAVE FUNCTION WITH HEADER/FOOTER ============================

def save_kiel_institute(fig, ax, filename, title, source, logo="KIEL Wortbildmarke black.png", subtitle=None, description=None,
                                    footer=None, grid="horizontal", figsize=(2000, 2182)):
    """
    Save a matplotlib figure with Kiel Institute-style header, footer, and logo.
    """
    print(f"Saving Kiel Institute-styled figure: {filename}...")

    fig.set_size_inches(max(figsize[0],2000)/150,max(figsize[1],2182)/150)
    ax.set_axisbelow(True)

    font_manager.fontManager.addfont(intl_medium_path)
    prop_title = font_manager.FontProperties(fname=intl_medium_path)
    FONT_DEFAULT = prop_title.get_name()                      # Font for the title, subtitle and source
    font_manager.fontManager.addfont(mono_regular_path)
    prop_footer = font_manager.FontProperties(fname=mono_regular_path)
    FONT_FOOTER = prop_footer.get_name()                    # Font for the footer
    font_manager.fontManager.addfont(intl_regular_path)
    prop_desc = font_manager.FontProperties(fname=intl_regular_path)
    FONT_DESCRIPTION = prop_desc.get_name()                 # Font for the description

    fig.patch.set_facecolor("#F5F1E7")

    if grid=="vertical":
        ax.grid(visible=False, axis="y")
    else:
        ax.grid(visible=False, axis="x")

    transform_title = transform.offset_copy(        #Set the location of the title
        fig.transFigure, fig= fig,
        x = 0.9*72,
        y = -0.9*72,
        units="points"
    )
    wrapped_title = textwrap.fill(title, width=int(fig.get_figwidth() * 2.85))
    title = fig.text(0, 1, wrapped_title, ha="left", va="top",
                fontsize=45, color="#000000", 
                family=FONT_DEFAULT,fontweight="bold", transform=transform_title)
    
    fig.canvas.draw()
    title_box = title.get_window_extent()
    title_box_percent = title_box.transformed(fig.transFigure.inverted())

    if subtitle:
        transform_subtitle = transform.offset_copy(
        fig.transFigure, fig= fig,
        x = 0.9*72,
        y = (title_box.y0/fig.dpi)*72 - 0.15748*72,
        units="points"
        )
        wrapped_subtitle = textwrap.fill(subtitle, width=int(fig.get_figwidth() * 6.0))
        subtitle = fig.text(0, 0, wrapped_subtitle, ha="left", va="top",
                 fontsize=21, color="#000000", 
                 family=FONT_DEFAULT, fontweight="bold", transform=transform_subtitle)
        fig.canvas.draw()
        subtitle_box = subtitle.get_window_extent()
        subtitle_box_percent = subtitle_box.transformed(fig.transFigure.inverted())
    
    if footer:
        transform_footer = transform.offset_copy(
        fig.transFigure, fig= fig,
        x = -0.9*72,
        y = 0.9*72,
        units="points"
        )
        footer = fig.text(1, 0, footer, ha="right", va="bottom",
                    color="#000000", fontsize=15, 
                    family=FONT_FOOTER, transform=transform_footer)
        fig.canvas.draw()
        footer_box = footer.get_window_extent()

    transform_source = transform.offset_copy(
        fig.transFigure, fig= fig,
        x = 0.9*72,
        y = 0.9*72,
        units="points"
    )

    if footer:
        max_width = min(int(fig.get_figwidth() * 4.35),int(((footer_box.x0 / fig.dpi) - 0.9) * (130/21)))
        if max_width <= 0:
            print("Error: The footer is too long! Please use a shorter footer or adjust figure width.")
            return
        wrapped_source = textwrap.fill(source,width=max_width)
    else:
        wrapped_source = textwrap.fill(source,width=int(fig.get_figwidth() * 4.35))
    source = fig.text(0, 0, wrapped_source, ha="left", va="bottom",
                fontsize=21, color="#000000",
                family=FONT_DEFAULT, fontweight="bold", transform=transform_source)
    fig.canvas.draw()
    source_box = source.get_window_extent()


    logo = str(files("KI_Inst_design_template").joinpath(logo))
    logo = mpimg.imread(logo)
    if footer:
        ax_logo = fig.add_axes([0.73, 0.02, 0.21, 0.21], zorder=10)
    else:
        ax_logo = fig.add_axes([0.73, -0.01, 0.21, 0.21], zorder=10)
    ax_logo.imshow(logo)
    ax_logo.axis("off")
    logo_percent = ax_logo.get_position()


    if description:
        transform_description = transform.offset_copy(
            fig.transFigure, fig= fig,
            x = 0.9*72,
            y = (source_box.y1/fig.dpi)*72 + 0.9*72,
            units="points"
        )
        wrapped_description = textwrap.fill(description, width=int(fig.get_figwidth() * 4.35))
        description = fig.text(0, 0, wrapped_description, ha="left", va="bottom",
                 color="#000000", fontsize=21,
                 family=FONT_DESCRIPTION, transform=transform_description)
        fig.canvas.draw()
        description_box = description.get_window_extent()
        description_box_percent = description_box.transformed(fig.transFigure.inverted())

    if description:
        bottom_gap = description_box_percent.y1 + 0.04
    else:
        bottom_gap = logo_percent.y1 + 0.01
    if subtitle:
        top_gap = (subtitle_box_percent.y0-0.04)
    else:
        top_gap = (title_box_percent.y0-0.04)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        fig.tight_layout(rect=[0.05, bottom_gap, 0.95, top_gap])
        
    fig.savefig(filename, dpi=150, facecolor="#F5F1E7")
    print(f"Saved {filename}")
    plt.close(fig)