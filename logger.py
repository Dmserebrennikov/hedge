import logging


def setup_logger():
    logger_obj = logging.getLogger("logs")
    logger_obj.setLevel(logging.DEBUG)
    main_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(main_format)
    fh = logging.FileHandler("logs.log")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger_obj.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger_obj.addHandler(ch)
    return logger_obj


logger = setup_logger()
