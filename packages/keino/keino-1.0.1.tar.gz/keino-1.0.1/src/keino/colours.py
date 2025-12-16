# Various colourmaps and related utilities.
# Copyright (C) 2025 Dan Crawford
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

try:
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap, ListedColormap, to_rgb, rgb_to_hsv, hsv_to_rgb
    cont = True
except:
    cont = False


default = {
        "blue":         "#193ce6",
        "orange":       "#ff8000",
        "green":        "#29a366",
        "red":          "#ff4e33",
        "violet":       "#bb99ff",
        "brown":        "#8e4b25",
        "pink":         "#ff9999",
        "yellow":       "#e5e51a",
        "lightblue":    "#b1dfe5",
        "mediumblue":   "#267399",
        "greyblue":     "#40b1bf",
        "black":        "#000000",
        "white":        "#fffaf0",
        "purple":       "#6619ff",
}
spectral = {
        "red":          "#ff4e33",
        "orange":       "#ff8000",
        "yellow":       "#e5e51a",
        "lightblue":    "#b1dfe5",
        "blue":         "#193ce6",
        "green":        "#29a366",
        "violet":       "#bb99ff",
}

if cont:
    def hsv_to_html(h, s, v):
        """Convert HSV representation to HTML representation"""
        # Convert HSV to RGB (values between 0 and 1)
        r, g, b = hsv_to_rgb((h, s, v))
        
        # Scale RGB to 0–255
        r = int(round(r * 255))
        g = int(round(g * 255))
        b = int(round(b * 255))
        
        # Format as HTML hex color
        return f'#{r:02X}{g:02X}{b:02X}'

    def hue_interp(h1, h2, n):
        """shortest signed angular distance"""
        dh = ((h2 - h1 + 0.5) % 1.0) - 0.5
        return (h1 + np.linspace(0, dh, n)) % 1.0

    def RGB(l):
        """Convert HTML representation to RGB representation"""
        return [to_rgb(c) for c in l]

    def white_gradient(base_colour):
        """Create a gradient from base_colour to white"""
        h, s, v = rgb_to_hsv(to_rgb(base_colour))
        cmap = [hsv_to_html(h, i, v) for i in np.arange(0, 1.1, 0.1)]
        return cmap

    def black_gradient(base_colour):
        """Create a gradient from base_colour to black"""
        h, s, v = rgb_to_hsv(to_rgb(base_colour))
        cmap = [hsv_to_html(h, i, i) for i in np.arange(0, 1.1, 0.1)]
        return cmap

    def cream_gradient(base_colour):
        """Create a gradient from base_colour to cream"""
        h, s, v = rgb_to_hsv(to_rgb(base_colour))
        cmap = [hsv_to_html(h, i, v) for i in np.arange(0, 1.1, 0.1)]
        cmap[0] = default["white"]
        return cmap

    def black_white_gradient(base_colour):
        """Create a gradient from black to base colour to white"""
        h, s, v = rgb_to_hsv(to_rgb(base_colour))
        cmap1 = [hsv_to_html(h, i, i) for i in np.arange(0, 1.1, 0.1)]
        cmap2 = [hsv_to_html(h, i, v) for i in np.arange(0, 1.1, 0.1)]
        cmap = cmap1 + list(reversed(cmap2))
        return cmap

    def black_cream_gradient(base_colour):
        """Create a gradient from black to base colour to cream"""
        h, s, v = rgb_to_hsv(to_rgb(base_colour))
        cmap1 = [hsv_to_html(h, i, i) for i in np.arange(0, 1.1, 0.1)]
        cmap2 = [hsv_to_html(h, i, v) for i in np.arange(0, 1.1, 0.1)]
        cmap2[0] = default["white"]
        cmap = cmap1 + list(reversed(cmap2))
        return cmap

    def saturation_gradient(base_colour):
        """Create a gradient where the saturation varies"""
        h, s, v = rgb_to_hsv(to_rgb(base_colour))
        cmap = [hsv_to_html(h, i, v) for i in np.arange(0.1, 1.1, 0.1)]
        return cmap

    def value_gradient(base_colour):
        """Create a gradient where the value varies"""
        h, s, v = rgb_to_hsv(to_rgb(base_colour))
        cmap = [hsv_to_html(h, s, i) for i in np.arange(0.1, 1.1, 0.1)]
        return cmap

    def saturation_value_gradient(base_colour):
        """Create a gradient where the value varies, and then the saturation"""
        h, s, v = rgb_to_hsv(to_rgb(base_colour))
        cmap1 = [hsv_to_html(h, i, v) for i in np.arange(0.1, 1, 0.1)]
        cmap2 = [hsv_to_html(h, s, i) for i in np.arange(0.1, 1.1, 0.1)]
        cmap = cmap1 + list(reversed(cmap2))
        return cmap

    def twin_gradient(base_colour1, base_colour2):
        """Create a gradient from one colour, through white, to another colour"""
        h1, s1, v1 = rgb_to_hsv(to_rgb(base_colour1))
        h2, s2, v2 = rgb_to_hsv(to_rgb(base_colour2))

        cmap1 = []
        ss = np.linspace(s1, 0, 10)
        vs = np.linspace(v1, 1, 10)
        for i in range(10):
            cmap1.append(hsv_to_html(h1, ss[i], vs[i]))

        cmap2 = []
        ss = np.linspace(0, s2, 10)
        vs = np.linspace(1, v2, 10)
        for i in range(10):
            cmap2.append(hsv_to_html(h2, ss[i], vs[i]))

        cmap = cmap1 + cmap2

        return cmap

    def twin_cream_gradient(base_colour1, base_colour2):
        """Create a gradient from one colour, through white, to another colour"""
        h1, s1, v1 = rgb_to_hsv(to_rgb(base_colour1))
        h2, s2, v2 = rgb_to_hsv(to_rgb(base_colour2))

        cmap1 = []
        ss = np.linspace(s1, 0.1111, 10)
        vs = np.linspace(v1, 1, 10)
        for i in range(10):
            cmap1.append(hsv_to_html(h1, ss[i], vs[i]))

        cmap2 = []
        ss = np.linspace(0.1111, s2, 10)
        vs = np.linspace(1, v2, 10)
        for i in range(10):
            cmap2.append(hsv_to_html(h2, ss[i], vs[i]))

        cmap = cmap1 + cmap2

        return cmap

    def twin_black_white_gradient(base_colour1, base_colour2):
        """Create a gradient from black, to one colour, to another colour, to white"""
        h1, s1, v1 = rgb_to_hsv(to_rgb(base_colour1))
        h2, s2, v2 = rgb_to_hsv(to_rgb(base_colour2))

        cmap1 = []
        ss = np.linspace(0, s1, 10)
        vs = np.linspace(0, v1, 10)
        for i in range(10):
            cmap1.append(hsv_to_html(h1, ss[i], vs[i]))

        cmap2 = []
        hs = hue_interp(h1, h2, 10)
        ss = np.linspace(s1, s2, 10)
        vs = np.linspace(v1, v2, 10)
        for i in range(10):
            cmap2.append(hsv_to_html(hs[i], ss[i], vs[i]))

        cmap3 = []
        ss = np.linspace(s2, 0, 10)
        vs = np.linspace(v2, 1, 10)
        for i in range(10):
            cmap3.append(hsv_to_html(h2, ss[i], vs[i]))

        cmap = cmap1 + cmap2 + cmap3

        return cmap

    def twin_black_cream_gradient(base_colour1, base_colour2):
        """Create a gradient from black, to one colour, to another colour, to white"""
        h1, s1, v1 = rgb_to_hsv(to_rgb(base_colour1))
        h2, s2, v2 = rgb_to_hsv(to_rgb(base_colour2))

        cmap1 = []
        ss = np.linspace(0, s1, 10)
        vs = np.linspace(0, v1, 10)
        for i in range(10):
            cmap1.append(hsv_to_html(h1, ss[i], vs[i]))

        cmap2 = []
        hs = hue_interp(h1, h2, 10)
        ss = np.linspace(s1, s2, 10)
        vs = np.linspace(v1, v2, 10)
        for i in range(10):
            cmap2.append(hsv_to_html(hs[i], ss[i], vs[i]))

        cmap3 = []
        ss = np.linspace(s2, 0.1111, 10)
        vs = np.linspace(v2, 1, 10)
        for i in range(10):
            cmap3.append(hsv_to_html(h2, ss[i], vs[i]))

        cmap = cmap1 + cmap2 + cmap3

        return cmap

    class Cmap():
        def __init__(self, name, listed=False, gradient="black_white", N=1000, is_reversed=False, callback=None):
            """
            Create a colourmap object

            Parameters
            ----------
            name: str
                name of the base colour to use, drawn from the above default dict.
            listed: bool
                If the colourmap is discrete
            gradient: str
                type of gradient to use
            N: int
                number of colours
            is_reversed: bool
                reverse the colourmap
            callback: function | None
                optional function to generate the colourmap from the base colour

            """
            self.listed = listed
            self.N = N
            self.name = name
            if callback is None:
                match gradient:
                    case "cream":
                        self.colours = cream_gradient(default[name])
                    case "white":
                        self.colours = white_gradient(default[name])
                    case "black":
                        self.colours = black_gradient(default[name])
                    case "black_white":
                        self.colours = black_white_gradient(default[name])
                    case "black_cream":
                        self.colours = black_cream_gradient(default[name])
                    case "saturation":
                        self.colours = saturation_gradient(default[name])
                    case "value":
                        self.colours = value_gradient(default[name])
                    case "saturation_value":
                        self.colours = saturation_value_gradient(default[name])
                    case "twin":
                        self.colours = twin_gradient(default[name[0]], default[name[1]])
                    case "twin_cream":
                        self.colours = twin_cream_gradient(default[name[0]], default[name[1]])
                    case "twin_black_white":
                        self.colours = twin_black_white_gradient(default[name[0]], default[name[1]])
                    case "twin_black_cream":
                        self.colours = twin_black_cream_gradient(default[name[0]], default[name[1]])
                    case _:
                        raise ValueError("Invalid gradient")
            else:
                self.colours = callback(default[name])
            if is_reversed and self.colours is not None:
                self.colours = list(reversed(self.colours))

        def __call__(self):
            if self.listed:
                return ListedColormap(RGB(self.colours), name=f"{self.name}s")
            return LinearSegmentedColormap.from_list(f"{self.name}s", RGB(self.colours), self.N)

        def __getitem__(self, index):
            return self.colours[index]

    # Various colourmaps below

    class Blues(Cmap):
        def __init__(self, **kwargs):
            super().__init__("blue", **kwargs)

    class Oranges(Cmap):
        def __init__(self, **kwargs):
            super().__init__("orange", **kwargs)

    class Greens(Cmap):
        def __init__(self, **kwargs):
            if "gradient" in kwargs:
                if kwargs["gradient"] == "special":
                    kwargs["gradient"] = None
                    kwargs["callback"] = self.special_gradient
            super().__init__("green", **kwargs)

        def special_gradient(self, base_colour):
            h, s, v = rgb_to_hsv(to_rgb(base_colour))
            sats = [0.1265, 0.2638, 0.3616, 0.57, 0.75, 0.7484, 0.7459, 0.7561, 0.7561]
            vals = [0.9607, 0.9215, 0.9215, 0.8392, 0.8, 0.6392, 0.4784, 0.3215, 0.1607]
            cmap = [hsv_to_html(h, i, j) for i, j in zip(sats, vals)]
            return cmap

    class Reds(Cmap):
        def __init__(self, **kwargs):
            super().__init__("red", **kwargs)

    class Violets(Cmap):
        def __init__(self, **kwargs):
            super().__init__("violet", **kwargs)

    class LightBlues(Cmap):
        def __init__(self, **kwargs):
            super().__init__("lightblue", **kwargs)

    class MediumBlues(Cmap):
        def __init__(self, **kwargs):
            super().__init__("mediumblue", **kwargs)

    class GreyBlues(Cmap):
        def __init__(self, **kwargs):
            if kwargs["gradient"] == "special":
                kwargs["gradient"] = None
                kwargs["callback"] = self.special_gradient
            super().__init__("greyblue", **kwargs)

        def special_gradient(self, base_colour):
            h, s, v = rgb_to_hsv(to_rgb(base_colour))
            sats = [0.1033, 0.2183, 0.3548, 0.5, 0.6649, 0.6667, 0.6695, 0.6753, 0.6579]
            vals = [0.949, 0.898, 0.8509, 0.8, 0.7490, 0.6, 0.4509, 0.3019, 0.149]
            cmap = [hsv_to_html(h, i, j) for i, j in zip(sats, vals)]
            return cmap

    class Purples(Cmap):
        def __init__(self, **kwargs):
            kwargs["gradient"] = None
            kwargs["callback"] = lambda c: None
            super().__init__("greyblue", **kwargs)
            self.colours = ["#110033", "#220066", "#330099", "#4400cc", "#5500ff", "#7733ff", "#9966ff", "#bb99ff", "#ddccff"]

    class OrangesPurples(Cmap):
        def __init__(self, **kwargs):
            if "gradient" not in kwargs:
                kwargs["gradient"] = "twin_cream"
            super().__init__(["orange", "purple"], **kwargs)

    class PurplesOranges(Cmap):
        def __init__(self, **kwargs):
            if "gradient" not in kwargs:
                kwargs["gradient"] = "twin_cream"
            super().__init__(["purple", "orange"], **kwargs)

    class RedBlue(Cmap):
        def __init__(self, **kwargs):
            if "gradient" not in kwargs:
                kwargs["gradient"] = "twin_cream"
            super().__init__(["red", "blue"], **kwargs)

    class BlueRed(Cmap):
        def __init__(self, **kwargs):
            if "gradient" not in kwargs:
                kwargs["gradient"] = "twin_cream"
            super().__init__(["blue", "red"], **kwargs)

    class GreenPurple(Cmap):
        def __init__(self, **kwargs):
            if "gradient" not in kwargs:
                kwargs["gradient"] = "twin_cream"
            super().__init__(["green", "purple"], **kwargs)

    class PurpleGreen(Cmap):
        def __init__(self, **kwargs):
            if "gradient" not in kwargs:
                kwargs["gradient"] = "twin_cream"
            super().__init__(["purple", "green"], **kwargs)

    class OrangeLightBlue(Cmap):
        def __init__(self, **kwargs):
            if "gradient" not in kwargs:
                kwargs["gradient"] = "twin_cream"
            super().__init__(["orange", "lightblue"], **kwargs)

    class LightBlueOrange(Cmap):
        def __init__(self, **kwargs):
            if "gradient" not in kwargs:
                kwargs["gradient"] = "twin_cream"
            super().__init__(["lightblue", "orange"], **kwargs)

    class GreenMediumBlue(Cmap):
        def __init__(self, **kwargs):
            if "gradient" not in kwargs:
                kwargs["gradient"] = "twin_cream"
            super().__init__(["green", "mediumblue"], **kwargs)

    class MediumBlueGreen(Cmap):
        def __init__(self, **kwargs):
            if "gradient" not in kwargs:
                kwargs["gradient"] = "twin_cream"
            super().__init__(["mediumblue", "green"], **kwargs)

    def Spectral(N=1000):
        return LinearSegmentedColormap.from_list("Spectral", RGB(spectral.values()), N)
    def BlackWhite(transparent=False):
        if transparent:
            return LinearSegmentedColormap.from_list("BlackWhite", [(0, 0, 0), (1, 1, 1, 0)], 2)
        return LinearSegmentedColormap.from_list("BlackWhite", [(0, 0, 0), (1, 1, 1)], 2)
    def WhiteBlack():
        return LinearSegmentedColormap.from_list("WhiteBlack", [(1, 1, 1), (0, 0, 0)], 2)
    def Pastels(N=1000):
        oranges = Oranges(N=5, gradient="saturation", is_reversed=True)
        oranges = oranges[2::2] + ["#fff3e6"]
        blues = GreyBlues(N=5, gradient="special")
        blues = blues[:5]
        greens = Greens(gradient="special", is_reversed=True)
        greens = greens[4:]
        purples = Purples(N=5)
        purples = purples[::-1][:5]
        return LinearSegmentedColormap.from_list("Pastels", oranges + blues + greens + purples, N)
else:
    class Blues():
        def __init__(self, **kwargs):
            pass

    class Oranges():
        def __init__(self, **kwargs):
            pass

    class Greens():
        def __init__(self, **kwargs):
            pass

    class Reds():
        def __init__(self, **kwargs):
            pass

    class Violets():
        def __init__(self, **kwargs):
            pass

    class LightBlues():
        def __init__(self, **kwargs):
            pass

    class MediumBlues():
        def __init__(self, **kwargs):
            pass

    class GreyBlues():
        def __init__(self, **kwargs):
            pass

    class Purples():
        def __init__(self, **kwargs):
            pass

    class OrangesPurples():
        def __init__(self, **kwargs):
            pass

    class RedBlue():
        def __init__(self, **kwargs):
            pass

    class BlueRed():
        def __init__(self, **kwargs):
            pass

    class GreenPurple():
        def __init__(self, **kwargs):
            pass

    class PurpleGreen():
        def __init__(self, **kwargs):
            pass

    class OrangeLightBlue():
        def __init__(self, **kwargs):
            pass

    class LightBlueOrange():
        def __init__(self, **kwargs):
            pass

    class MediumBlueGreen():
        def __init__(self, **kwargs):
            pass

    class GreenMediumBlue():
        def __init__(self, **kwargs):
            pass

    def Spectral(N=1000):
        pass

    def BlackWhite(transparent=False):
        pass

    def WhiteBlack():
        pass

    def Pastels(N=1000):
        pass


__all__ = ["Cmap", "default",  "RGB", "Blues", "Oranges", "Greens", "Reds", "Violets", "LightBlues", "MediumBlues", "Spectral", "BlackWhite", "WhiteBlack", "RedBlue", "BlueRed", "GreenPurple", "PurpleGreen", "OrangeLightBlue", "LightBlueOrange", "Pastels", "OrangesPurples", "PurplesOranges", "MediumBlueGreen", "GreenMediumBlue"]
