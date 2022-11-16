FROM public.ecr.aws/lambda/python:3.6

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

ADD ./corpus/ ${LAMBDA_TASK_ROOT}/corpus/
ADD ./idx/ ${LAMBDA_TASK_ROOT}/idx/
COPY config.toml ${LAMBDA_TASK_ROOT}
COPY index_builder.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "index_builder.lambda_handler" ]