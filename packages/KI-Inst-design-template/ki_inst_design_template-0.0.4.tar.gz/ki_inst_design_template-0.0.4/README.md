# Kiel Institute Design Template
This Design Template allows you to automatically apply the corporate design of the Kiel Institute for the World Economy to Matplotlib charts. It handles custom fonts, specific color palettes, and layout requirements to ensure that visualizations are publication-ready.

## Prerequisites
To use this module effectively, you need to ensure that the following files and libraries are installed.

### 1. Python Libraries
This module requires matplotlib and cycler. If you do not have them installed, run the following command into the terminal or command prompt:

```bash
pip install matplotlib
```

Usually the cycler module is included in matplotlib. If it wasn't installed in the previous step run the following command aswell:

```bash
pip install cycler
```

### 2. Font Files
The Kiel Institute fonts are all from the 'Suisse' font familly. Usually the required fonts should be preinstalled on all Kiel Institute devices. If that is not the case, or if you are using your own device, please install the 'Suisse' fontkit.

### 3. Python Version
It is recomended that you use Python 3.11 for this template. For newer or older versions functionality is not guaranteed.

## Installation
Type the following command into the terminal or command prompt:

```bash
pip install KI_Inst_design_template
```

## Functionalities
This template has three functionalities, that will be introduced and shortly explained in the following.

### 1. Show Kiel Colours
The Colour Pallette of the Kiel Institute Brand Colours can be displayed by calling the show_kiel_institute_colors()-function in a python script:
```python
from KI_Inst_design_template import show_kiel_institute_colors

show_kiel_institute_colors()
```

This opens a window, where the available colors and the names by which they can be accessed are displayed, aswell as their corresponding HEX-codes.

### 2. Initialize Design Template
The corparate design of the Kiel Institute can be applied globally to matplotlib, by calling the init_kiel_institute_theme-function:

```python
from KI_Inst_design_template import init_kiel_institute_theme

init_kiel_institute_theme()
```

This applies the visual theme of the Kiel Institute to your plot.

### 3. Save charts in a file
Figures generated with Matplotlib can be saved in full compliance with the Kiel Institute's official layout guidelines:

```python
from KI_Inst_design_template import save_kiel_institute
import matplotlib as plt
import pandas as pd

save_kiel_institute(fig, ax, filename, title, source, subtitle, description,
                                    footer, "vertical")
```

It is required, that a ==filename==, ==title== and ==source== are passed to the function as arguments in addition to the ==figure== (fig) and ==axes== (ax) objects. Specifying the other arguments is optional.

## Example Usage
This is an example usage of the template with data form the [GREIX](https://greix.de):

```python
from KI_Inst_design_template import *
import matplotlib.pyplot as plt
import pandas as pd

show_kiel_institute_colors()

init_kiel_institute_theme()

df = pd.read_csv("Mietpreisindex_jährlich.csv", sep=";")
df_real = df[df['real_nominal_str'] == 'Real']

# Define a specific color map for the cities using the "KIEL_COLORS" variables
# This ensures consistent branding/coloring across charts
city_color_map = {
    "Berlin": KIEL_COLORS["kiel_blue"],
    "Aachen": KIEL_COLORS["kiel_orange"],
    "Düsseldorf": KIEL_COLORS["kiel_green"],
    "München": KIEL_COLORS["kiel_red"],
    "Hamburg": KIEL_COLORS["kiel_turquoise"],
    "Kiel": KIEL_COLORS["kiel_pink"],
    "Köln": KIEL_COLORS["kiel_purple"]
}
cities = list(city_color_map.keys())

df_filtered = df_real[df_real['Value-Column Titles'].isin(cities)]
df_filtered_pivot = df_filtered.pivot(index='Year', columns='Value-Column Titles', values='Values')

# Initialize the figure and axis for the line plot
fig, ax = plt.subplots()

# Plot the time-series data on the axis using the specific colors defined earlier
df_filtered_pivot.plot(ax=ax, color=city_color_map)

df_filtered_bar = df[df["Year"]==2024]
df_filtered_bar = df_filtered_bar[df_filtered_bar["Value-Column Titles"].isin(cities)]
df_pivot_bar = df_filtered_bar.pivot(index="Value-Column Titles", columns="real_nominal_str",values="Values")

# Initialize the figure and axis for the bar plot
fig_bar, ax_bar = plt.subplots()

# Plot the "Nominal" and "Real" data on top of each other and specify the coloring using "KIEL_COLORS"
b1 = ax_bar.bar(df_pivot_bar.index,df_pivot_bar["Real"], label="Real Index", color=KIEL_COLORS["kiel_blue"])
b1 = ax_bar.bar(df_pivot_bar.index,df_pivot_bar["Nominal"], bottom=df_pivot_bar["Real"], label="Nominal Index", color=KIEL_COLORS["kiel_blue_60"])

# Add a legend to the bar chart if it isn't done automatically
ax_bar.legend()

# Use the save_kiel_institute function to save the charts in a .png file

save_kiel_institute(
    fig_bar,
    ax_bar,
    "bar_plott.png",
    title="Rental Price Index: Nominal vs. Real",
    subtitle="subtitle subtitle subtitle subtitle subtitle subtitle subtitle",
    source="kielinstitut.de",
    description="description description description description description description description description" \
    " description description description description description description description description description description",
    footer="footer footer footer footer footer footer footer"
)

save_kiel_institute(
    fig,
    ax,
    "graph.png",
    title="Rental Price Development In German cities over time",
    subtitle="subtitle subtitle subtitle subtitle subtitle subtitle subtitle",
    source="kielinstitut.de",
    description="description description description description description description description description" \
    " description description description description description description description description description description",
)
```

## Support
If you experience any difficulties with the template's functionality, we encourage you to submit an issue via [GitHub](https://github.com/kielinstitute/kielinstitutPython/issues). We will try to resolve the matter as quickly as possible.

## License
This project is licensed under an All Rights Reserved License. See the LICENSE file for details.