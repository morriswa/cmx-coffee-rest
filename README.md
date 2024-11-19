# CMX eCommerce Coffee

## Contributors
- William Morris [morriswa] morris.william@ku.edu
- Kevin Rivers [Kabuto1357] kevin.rivers14832@ku.edu
- Timothy Holmes [TimoHolmes] t338h273@home.ku.edu
- Makenna Loewenherz
- Rahul Bhattachan

## Project Setup Guide
- Install python 3.12 https://www.python.org/downloads/
- Open project root directory in terminal
- Install Project environment

      python3.12 -m venv .
- Activate Project environment
    - Mac/Linux

          source bin/activate
        - NOTE: to deactivate project environment

              deactivate
        - NOTE: to reset project environment 

              rm -rf bin include lib pyvenv.cfg
    - Windows Powershell

          .\Scripts\activate
        - NOTE: to deactivate project environment

              .\Scripts\deactivate.bat
        - NOTE: to reset project environment 

              rm -r include
              rm -r lib 
              rm -r scripts
              rm -r pyvenv.cfg
- Install project in development mode and dependencies with PIP 

      pip install -e .
- Create local app environment file 'secrets.properties' in project root directory
- Include values in secrets.properties

      DB_HOST=host_here
      DB_NAME=database_name_here
      DB_USER=database_username_here
      DB_PASSWORD=database_password_here
      SECRET_KEY=a_bunch_of_nonsense
- Setup development database

      python manage.py migrate
- Run on local machine http://localhost:8000
      
      python manage.py runserver

## Test Setup Guide
- Log into postgres console on your machine with admin credential 
and run following commands

      create role testuser with createdb login password 'testpassword';
- Run test script
      
      python test.py
- Install coverage library

      pip install coverage
- Run test script with coverage
      
      coverage run test.py
      coverage report -m

## Django Migrate Guide
please note all database scripts are located in src/core/migrations 
and all sql commands are stored in src/*/daos.py 

- Reset app database

      python manage.py migrate core zero
- Migrate app database to specific version 
  (replace xxxx with migration code eg 0001, 0002, etc) 

      python manage.py migrate core xxxx

- Migrate app database to latest version

      python manage.py migrate 
