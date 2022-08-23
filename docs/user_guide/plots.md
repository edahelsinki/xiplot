# Scatterplot

In &chi;iplot, scatterplots are playing the key role. They are connected to most of the other plots either directly (by hovering or clicking) or
indirectly (by drawing clusters).

## Control of scatterplots

There are four dropdowns and one slider in the control of the scatterplots.

The first two dropdowns change the axes of the scatterplot. The dropdowns have only columns, whose datatypes are numerical (e.g. a column weight is
numerical but a column car-name is not numerical).

![scatterplot_axes](https://github.com/edahelsinki/xiplot/blob/main/documents/images/scatterplot_init.png)

The latter two dropdowns modify the color or the shape of the points of the scatterplot. The default value of the color dropdown is "Clusters".
(The scatterplot's color on the above image has not changed, since clusters are not created yet)

![scatterplot_coloring](https://github.com/edahelsinki/xiplot/blob/main/documents/images/scatterplot_coloring.png)

The slider in the bottom is for jittering. Jittering seperates the points from each other, so that overlapped points can be recognized.

![scatterplot_jitter](https://github.com/edahelsinki/xiplot/blob/main/documents/images/scatterplot_jittering.png)

## Hovering over points

If the dataset has a column for SMILES strings, the user can display stick structure of the molecule on the SMILES plot by hovering over points on
scatterplots. The dropdown value of the SMILES plot should be "hover".

![scatterplot_hover](https://github.com/edahelsinki/xiplot/blob/main/documents/images/scatterplot_hover.png)

## Click on points

As with the hovering, if the dataset has a column for SMILES strings, the stick structure is displayable by clicking on the points of the scatterplot.
The dropdown value of the SMILES plot should be "click".

In addition, when the user clicks a point on a scatterplot, the corresponding row on data tables is marked as selected and brought to 
the top of the data table. Clicked points are displayed larger than the other points and they are black.

![scatterplot_click](https://github.com/edahelsinki/xiplot/blob/main/documents/images/scatterplot_click.png)

## Clustering

See the ![clustering.md](https://github.com/edahelsinki/xiplot/blob/main/documents/user_guide/clustering.md)


