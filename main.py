import os

config_file_path = os.path.join(os.path.basename(__file__), 'config.py')
if not os.path.exists(config_file_path):
    print('配置文件config.py缺失，请联系开发者。。。')
    exit()
else:
    from config import 国恒信创采集MQ, dirs, logger

from application.app import MQ_C
from application.downloader import Downloader


class App:

    @classmethod
    def run(cls):
        for dir in dirs:
            if not os.path.exists(dir):
                os.makedirs(dir)
        monitor = MQ_C(国恒信创采集MQ.config)
        monitor.run()
        logger.info(f'vdq监视器已启动')
        downloader = Downloader()
        while 1:
            downloader.run()


if __name__ == '__main__':
    App.run()
