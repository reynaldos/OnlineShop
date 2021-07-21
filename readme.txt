

How To Run Application on macOS:
1. Activate Virtual Environment
    - Command: 'source shop/venv/bin/activate'

2. Set Flask Environment to 'development'
    - Command: 'export FLASK_ENV=development'

3. Run Flask Application
    - Command: 'python3 main.py'


If changes to models are made:
    1. Command: 'python3 -m flask db migrate'
    2. Command: 'python3 -m flask db upgrade'

Admin Account:
Email: admin@usf.edu
password: 12345
UserId: 1
