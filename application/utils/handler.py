from flask import current_app
import sys
import logging
from sqlalchemy import exc
import gc

logging.basicConfig(
    stream=sys.stdout, 
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s - %(message)s',
)
env = current_app.config.get('ENV')

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    logging.error(*args)

class AppMessageException(Exception):
    pass

def exception_handler(e, res_code=500, default_data={}, message='something went wrong', services='defaultservices'):
    # print('err: ', sys.exc_info())
    # print('err: ', type(e).__name__)
    eprint('{}: {}'.format(services, str(e)))

    context = {
        'status': { }
    }

    message = str(e)

    try:
        raise e
    except exc.SQLAlchemyError:
        if env == 'development':
            pass
        else:
            message = '-- prod redacted, please contact admin --'
    except:
        if env == 'development':
            pass
        else:
            message = '-- prod redacted, please contact admin --'

    context['status']['message'] = message
    context['status']['success'] = False

    gc.collect()

    return context

def success_handler(results, res_code=200, message='ok'):
    context = {
        'data': results,
        'success': True
    }

    # context = {
    #     'gis': {
    #         'status': {
    #             'message': message,
    #             'status_code': res_code,
    #             'error_message': 'no error',
    #             'error_code': -1
    #         },
    #         'results': results
    #     }
    # }

    gc.collect()

    return context