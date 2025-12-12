#!/bin/sh

pip install ./*.whl
pip install --upgrade "muck_out>=0.3.15"
uvicorn --factory cattle_grid:create_app --host 0.0.0.0 --port 80 --reload