# &chi;iplot

&chi;iplot, pronounced like "kaiplot"[^1], is a web-first visualisation platform for multidimensional data, implemented in the `xiplot` Python package.

[^1]: Pronouncing &chi;iplot like "xaiplot" is also recognised.

## Description

&chi;iplot is built on top of the [`dash`](https://github.com/plotly/dash) framework. The goal of the &chi;iplot is to explore new insights from the collected data and to make data exploring user-friendly and intuitive.
&chi;iplot can be used without installation with the [WASM-based browser version](https://edahelsinki.fi/xiplot).

You can find more details in the [user guide](docs/user_guide/README.md) and in the paper:

> Tanaka, A., Tyree, J., Björklund, A., Mäkelä, J., Puolamäki, K. (2023).  
> __&chi;iplot: Web-First Visualisation Platform for Multidimensional Data.__  
> Machine Learning and Knowledge Discovery in Databases: Applied Data Science and Demo Track, Lecture Notes in Computer Science, pp. 335-339. [DOI: 10.1007/978-3-031-43430-3_26](https://doi.org/10.1007/978-3-031-43430-3_26)

For a quick demonstration, see [the video](https://helsinkifi-my.sharepoint.com/:v:/g/personal/tanakaki_ad_helsinki_fi/EcIIGy0bfP5FlW-0Lr4AMEYBbKoyuo6u7px3zu_K5Vk4xw?e=TPGGf8&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZyIsInJlZmVycmFsQXBwUGxhdGZvcm0iOiJXZWIiLCJyZWZlcnJhbE1vZGUiOiJ2aWV3In19) or try the [WASM version](https://edahelsinki.fi/xiplot).

## Screenshot

![Screenshot of xiplot](docs/images/cluster_by_drawing.png#gh-light-mode-only)
![Screenshot of xiplot](docs/images/dark_mode.png#gh-dark-mode-only)

## Installation free

You can try out the installation free WASM version of &chi;iplot at [edahelsinki.fi/xiplot](https://edahelsinki.fi/xiplot). Note that all data processing happens locally in **your** browser nothing is sent to a server.

Please refer to the [wasm](https://github.com/edahelsinki/xiplot/tree/wasm#readme) branch for more information on how the WASM version is implemented

## Installation

&chi;iplot can also be installed locally with: `pip install xiplot`.
To start the local server run `xiplot` in a terminal (with same Python environment venv/conda/... in the PATH).

Or to use the latest, in-development, version clone this repository.
To install the dependencies run `pip install -e .` or `pip install -r requirements.txt`.
To start the local server run `python -m xiplot`.

For more options run `xiplot --help`.

## Funding

The `xiplot` application was created by [Akihiro Tanaka](https://github.com/TanakaAkihiro) and [Juniper Tyree](https://github.com/juntyr) as part of their summer internships in Kai Puolamäki's [Exploratory Data Analysis group](https://github.com/edahelsinki) at the University of Helsinki.

Akihiro's internpship was paid for by the Academy of Finland (decision 346376) with funding associated with the VILMA Centre of Excellence. Juniper's internship was paid for by "Future Makers Funding Program 2018 of the Technology Industries of Finland Centennial Foundation, and the Jane and Aatos Erkko Foundation", with funding associated with the Atmospheric AI programme of the Finnish Center for Artificial Intelligence.

## License

The `main` branch of the `xiplot` repository is licensed under the MIT License ([`LICENSE-MIT`](LICENSE-MIT) or http://opensource.org/licenses/MIT).

## Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in the work by you shall be licensed as described above, without any additional terms or conditions.
