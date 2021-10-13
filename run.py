#<
# run.py
# primary server run python module.
# called by gunicorn to start
# gunicorn -c config.py run:app > /dev/null 2>&1 &
# app variable is set in the .bashrc of the app account.
# gunicorn handles all web interface and api calls.
# lives in parent folder of cdfService.
#>
from cdfService import create_app

app = create_app()

# Run Server
if __name__ == '__main__':
    app.run(debug=True)
