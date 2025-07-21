FROM 3.11.8
WORKDIR /main
COPY . /main
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "./main.py"]
