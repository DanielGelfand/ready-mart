# ready-mart 
*M*ai Rachlevsky, *A*mit Narang, *R*ay Onishi, *T*heodore Peters 

# Dependencies: 
Runs with python3, flask, wheel.
Also runs SQLite3, which comes installed with python3.

Uses [passlib](https://passlib.readthedocs.io/en/stable/ "passlib documentation"), a library of password hashing functions.
Storing user passwords as plaintext is a massive security vunerability and should be avoided, but implementing password hashing ourselves was not viable given time constraints. Passlib is used to enter hashed passwords into database when users register, and check passwords when users try to login.

# To run our project:
1. Clone our repo
```
$ git clone git@github.com:anotherLostKitten/ready-mart.git 
```
2. Create & activate your virtual environment
```
$ python3 -m venv h
$ . h/bin/activate
```
3. In your virtual environment, run the following to install the necessary packages:
```
(h) $ pip3 install wheel

(h) $ pip3 install flask

(h) $ pip3 install passlib
```
4. Go to the project directory
```
(h) $ cd ready-mart
```
5. Run app.py
```
(h) $ python3 app.py 
```
6. Navigate to `localhost:5000` on your web browser
