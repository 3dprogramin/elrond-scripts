import logging, os, base64

class Log:
    @staticmethod
    def read_current_log(name='debug.log'):
        # create path
        p = os.path.join(os.getcwd(), name)
        if os.path.exists(p):  # check if it exists
            with open(p, 'r') as f:
                txt = f.read()
                txt = '\n'.join(txt.split('\n')[-100000:])
                return txt # return what's been read
        return '' # otherwise, return empty

    @staticmethod
    def setup_custom_logger(name='debug.log'):
        Log.clear_log_file(name)
        formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

        p = os.path.join(os.getcwd(), name)
        handler = logging.FileHandler(p)
        handler.setFormatter(formatter)
        handler2 = logging.StreamHandler()
        handler2.setFormatter(formatter)
        # handler2.setFormatter(formatter)
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.addHandler(handler2)
        return logger

    @staticmethod
    def clear_log_file(name):
        # create path
        p = os.path.join(os.getcwd(), name)
        if os.path.exists(p): # check if it exists
            try: os.remove(p) # remove log
            except Exception as ex:
                raise Exception('cannot clear debug.log details: {}'.format(ex))
