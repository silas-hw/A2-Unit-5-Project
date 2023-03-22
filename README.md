# A2 Computer Science Project

## Running

To run this website, you need to install the required modules and software and then either attach the program to
a HTTP server with WSGI or run it in a developmental environment with Python (the latter is easier and is what
I will go over how to do).

It is likely you're using Windows to assess this project, although alternative instructions have been provided for other operating systems when required. It is suggested
that you follow these instructions in a virtual environment (e.g. Pyenv), although I will not provide instructions on how to do so. This project relies on the correct
versions of modules and interpreters to be used, which the use of a virtual environment ensures. If you choose to continue without a virtual environment, I can
not promise that the system will work the same for you as it does for me.

#### Step 1: Install Python

Install a version of Python between 3.8.x to 3.10.x

#### Step 2: Installing modules

run the following command in the same directory as this file to install the required Python modules

```cmd
pip install -r requirements.txt
```

If this doesn't work, it is possible you have not setup PATH correctly. Try the following command instead:

```cmd
python -m pip install -r requirements.txt
```

#### Step 3: Setting environment variables

Flask relies on environment variables to run this application. In the same command prompt, run the following commands (windows):

```cmd
set FLASK_APP=flaskr
```

or the following command (linux):

```bash
export FLASK_APP=flaskr
```

#### Step 4: Running the program

Run the following command in the same command prompt to start the application

```cmd
flask run
```

The website should now be accessible at http://localhost:5000 or http://127.0.0.1:5000

## Test Account Details

Username: Test1
E-mail: test@test.com
Password: Password123
