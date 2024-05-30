FROM python:3.10

RUN apt-get -y update
RUN apt install fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 libcups2 libdbus-1-3 libdrm2 \
    libgbm1 libgtk-3-0 libgtk-4-1 libnspr4 libnss3 libu2f-udev libu2f-udev libvulkan1 libxcomposite1 \
    libxcomposite1 libxdamage1 libxfixes3 libxkbcommon0 libxrandr2 xdg-utils -y
RUN apt install unzip
RUN mkdir /code
COPY . /code
WORKDIR /code
RUN wget http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_125.0.6422.76-1_amd64.deb
RUN wget https://storage.googleapis.com/chrome-for-testing-public/125.0.6422.76/linux64/chromedriver-linux64.zip
RUN unzip chromedriver-linux64.zip
RUN cp chromedriver-linux64/chromedriver /code
RUN rm chromedriver-linux64.zip
RUN rm -R chromedriver-linux64
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt --no-cache-dir
