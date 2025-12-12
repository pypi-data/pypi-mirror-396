# Getting started

This directory contains Python code, NOMAD plugins, and other artifacts
to facilitate end-to-end testing. It also provides you with plugins, schemas,
data to run the GUI against.

This is how you run NOMAD, upload some data, and start using the GUI with it:

1. Get a python environment with NOMAD installed.
   From the gui project root folder:

```sh
python3.11 -m venv .venv
source .venv/bin/activate
pip install uv
uv pip install --upgrade pip
uv pip install -e infra \
    --extra-index-url https://gitlab.mpcdf.mpg.de/api/v4/projects/2187/packages/pypi/simple \
    --pre
```

2. (optional) Replace nomad-lab with a local clone

```sh
uv pip install -e ../nomad[parsing,infrastructure]
```

3. (optional) To enable the `simulation` examples, you need to install the simulation-workflow plugin using:

```sh
uv pip install git+https://github.com/nomad-coe/nomad-schema-plugin-simulation-workflow.git
```

4. Run NOMAD. Run from this directory it has the necessary `nomad.yaml` file:

```sh
cd infra
nomad admin run appworker
```

5. Upload some data. Again, mind the directory. Run from `infra`.

```sh
nomad client upload --upload-name ui-demonstration --ignore-path-prefix src/nomad_gui/example_uploads/ui_demonstration
nomad client upload --upload-name upload-navigation data/upload-navigation.zip
```

6. Run the gui with the right `.env.local`. This one is not part of git. By
   default `.env` is set to use the synthetic "fake" api. Overwrite with your
   `.env.local` to use the real api. This one has to be at the root of
   the project. Therefore, from the `infra` dir you could do:

```sh
echo "VITE_USE_MOCKED_API=false" > ../.env.local
```
