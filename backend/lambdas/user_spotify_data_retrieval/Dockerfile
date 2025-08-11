# Default architecture value
ARG ARCHITECTURE="arm64"

# Start from lambda Python3.13 image
FROM public.ecr.aws/lambda/python:3.13-${ARCHITECTURE}

# Copy the lambda code, together with its requirements
COPY requirements.txt ${LAMBDA_TASK_ROOT}
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Install postgresql-devel in your image
RUN dnf install -y gcc postgresql-devel

# install the requirements for the Lambda code
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Command can be overwritten by providing a different command in the template directly.
CMD ["lambda_function.handler"]
