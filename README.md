# bai_1_backend
Instrukcje wydawane w command window w celu uruchomienia serwera.
W pierwszej kolejności należy przejść do folderu pobranego repozytorium, następnie uruchomic serwer.
cd 'ścieżka do repozytorium'
set FLASK_APP=hello.py
set FLASK_ENV=development
flask run

W przypadku PowerShell zmienne należy ustawić poleceniami:
$env:FLASK_APP = "hello.py"
$env:FLASK_ENV = "development"
