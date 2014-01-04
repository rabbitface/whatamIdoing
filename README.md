To install the application for the first time:
```bash
# while in /var/www/
git clone https://github.com/rabbitface/whatamIdoing.git
cd whatamIdoing/
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

To run application:
```bash
source env/bin/activate
python flaskr.py
```

