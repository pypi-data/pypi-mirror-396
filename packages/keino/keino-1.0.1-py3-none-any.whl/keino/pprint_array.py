# Prints a matrix nicely in a Jupyter notebook
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
    from IPython.display import HTML, display
    cont = True
except:
    cont = False

if cont:
    def pprint(H):
        display(HTML(
           '<table><tr>{}</tr></table>'.format(
               '</tr><tr>'.join(
                   '<td>{}</td>'.format('</td><td>'.join(str(_) for _ in row)) for row in H)
               )
        ))
else:
    def pprint(H):
        raise NotImplementedError("IPython is not installed")
