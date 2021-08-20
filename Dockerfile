FROM python:3.5.9-stretch

RUN apt-get -y update
RUN apt-get install -y libsqlite3-dev
RUN apt-get install -y sqlite
RUN apt-get install -y vim

# Create app directory
RUN mkdir -p /app
WORKDIR /app

COPY . /app

WORKDIR /app/PROJ
RUN ./configure --prefix=/usr/local && make && make install


WORKDIR /app/GDAL
RUN ./configure --prefix=/usr/local --with-proj=/usr/local && make && make install

WORKDIR /app/GDAL/swig/python
RUN python setup.py build && python setup.py install

WORKDIR /app
RUN cp /app/usr-libs.conf  /etc/ld.so.conf.d/
RUN ldconfig

# Install app dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple


CMD [ "python", "autoGDAL.py" ]
