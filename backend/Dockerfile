FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend ./backend
COPY model/reorder_model_tuned.pkl ./model/reorder_model_tuned.pkl
COPY model/restaurant_inventory_with_targets.csv ./model/restaurant_inventory_with_targets.csv

CMD ["backend.main.handler"]

