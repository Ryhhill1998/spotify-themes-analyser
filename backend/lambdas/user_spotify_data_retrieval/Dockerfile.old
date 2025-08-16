ARG ARCHITECTURE="arm64"

FROM public.ecr.aws/lambda/python:3.13-${ARCHITECTURE}

COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN dnf install -y gcc postgresql-devel

RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY lambda_function.py ${LAMBDA_TASK_ROOT}

CMD ["lambda_function.handler"]
