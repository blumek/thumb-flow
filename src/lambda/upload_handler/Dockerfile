FROM public.ecr.aws/lambda/python:3.12

WORKDIR /tmp
COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --upgrade pip && \
    pip install build && \
    python -m build && \
    pip install dist/*.whl && \
    cp -r /tmp/src/* ${LAMBDA_TASK_ROOT}/

CMD [ "handler.lambda_handler" ]
