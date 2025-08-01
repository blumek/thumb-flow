# Build stage
FROM public.ecr.aws/lambda/python:3.12 AS builder
WORKDIR /tmp
COPY pyproject.toml ./
COPY src/ ./src/
RUN pip install --upgrade pip && \
    pip install build && \
    python -m build

# Final stage
FROM public.ecr.aws/lambda/python:3.12
WORKDIR ${LAMBDA_TASK_ROOT}
COPY --from=builder /tmp/dist/*.whl /tmp/
COPY src/ /tmp/src/
RUN pip install /tmp/*.whl && \
    cp -r /tmp/src/* ${LAMBDA_TASK_ROOT}/ && \
    rm -rf /tmp/src /tmp/*.whl
CMD [ "dev_blumek_thumbnail_generator.bootstrap.handler.lambda_handler" ]
