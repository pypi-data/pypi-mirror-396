import sys

from boosty_api import BoostyApi
from boosty_api.exceptions import AuthError


if len(sys.argv) < 2:
    print(f'Usage: python {sys.argv[0]} LOGIN', file=sys.stderr)
    sys.exit(1)


api = BoostyApi(
    login=sys.argv[1],
    user_input_handler=lambda: input('Enter code from SMS: '),
    user_agent='VLC/3.0.21 LibVLC/3.0.21',
)
# api.logger.setLevel(logging.INFO)
# api.logger.addHandler(logging.StreamHandler())

try:
    api.auth()
except AuthError as err:
    print(err)
    sys.exit(1)

print(api)
print(api.current_user)
