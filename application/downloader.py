import os
import time
from datetime import datetime

import requests
from tqdm import tqdm

from application.ext import session
from application.models import Video
from config import (
    local_videos_dir, local_videos4test_dir,
    logger, USER_NAME, TOKEN, VIDEOS_SYNC_ROOT_URI, SLEEP_TIME
)


class Downloader:

    def get_videos2download(self):
        print(f'==============查询待下载视频======{datetime.now()}=============')
        videos = session.query(Video).filter(
            Video.is_deleted == 0,
            Video.status.in_([3, 31])
        ).all()
        return videos

    @staticmethod
    def sleep(t):
        print(f'无待下载视频，程序休眠。。。')
        for i in range(t):
            print(f'休眠剩余{t - i}秒')
            time.sleep(1)

    # @logger.catch()
    def run(self):
        while 1:
            videos2d = self.get_videos2download()
            if not videos2d:
                self.sleep(SLEEP_TIME)
                continue
            for video in videos2d:
                if video.for_test:
                    video_dir = local_videos4test_dir
                else:
                    video_dir = local_videos_dir

                local_path = os.path.join(video_dir, f'{video.vid}.{video.format}')
                if not os.path.exists(local_path) or int(os.path.getsize(local_path)) < int(video.size):
                    self.download(video, local_path=local_path)
                else:
                    self.update_status_32(video)

    def download(self, video, local_path):
        desc = f'{video.vid}.{video.format}'
        chunk_size = 1024
        if not os.path.exists(local_path):
            start_size = 0
            mode = 'wb'
        else:
            start_size = int(os.path.getsize(local_path))
            mode = 'ab'
            if start_size > int(video.size):
                msg = f'视频{local_path}本地大小超过视频size'
                logger.error(msg)
        if video.for_test:
            port = 7000
        else:
            port = 8000
        video_sync_api = f'{VIDEOS_SYNC_ROOT_URI}:{port}/api/toB/video_sync/{video.vid}'
        headers = dict(
            Range=f'{start_size}-{video.size}',
            token=TOKEN,
            chunk_size=str(chunk_size)
        )
        qs = dict(
            user_name=USER_NAME
        )
        self.update_status_31(video=video)
        try:
            r = requests.get(url=video_sync_api, params=qs, headers=headers, stream=True)
            if r.status_code != 200:
                logger.warning(r.text)
                msg = r.json().get('msg')
                self.update_status_34(video=video, error_msg=msg)
                return
            pbar = tqdm(
                total=int(video.size),
                initial=start_size,
                unit_scale=True,
                desc=desc,
                ncols=120
            )

            with open(local_path, mode) as f:
                for chuck in r.iter_content(chunk_size):
                    f.write(chuck)
                    # 手动更新的大小
                    pbar.update(chunk_size)
            pbar.close()
            self.update_status_32(video=video)
            logger.info(f'视频{local_path}已下载')

        except Exception as e:
            msg = f'视频vid_{video.id}.{video.format}下载报错，error:{e}'
            logger.error(msg)
            self.report_sync_error(video=video, error=str(e))

    def status_sync(self, video, status):
        if video.for_test:
            port = 7000
        else:
            port = 8000
        status_sync_api = f'{VIDEOS_SYNC_ROOT_URI}:{port}/api/toB/status_sync/v_{video.vid}/status/{status}'
        headers = dict(
            token=TOKEN,
        )
        data = dict(
            user_name=USER_NAME
        )
        logger.warning(f'status_sync_api:{status_sync_api}')
        r = requests.put(url=status_sync_api, data=data, headers=headers)
        if r.status_code == 200:
            logger.info(r.json().get('msg'))
        else:
            print(f'--------r.text:{r.text}')
            logger.error(r.json().get('msg'))

    def report_sync_error(self, video, error):
        if video.for_test:
            port = 7000
        else:
            port = 8000
        api = f'{VIDEOS_SYNC_ROOT_URI}:{port}/api/report/toB/video_sync_error/{video.vid}'
        headers = dict(
            token=TOKEN,
        )
        data = dict(
            user_name=USER_NAME,
            sync_error=error
        )
        r = requests.put(url=api, data=data, headers=headers)
        if r.status_code == 200:
            logger.info(r.json().get('msg'))
        else:
            logger.error(r.json().get('msg'))
        video.status = 34
        video.error_msg = error
        session.commit()

    def update_status_34(self, video, error_msg):
        self.status_sync(video=video, status=34)
        video.sync_start_time = None
        video.status = 34
        video.error_msg = error_msg
        session.commit()

    def update_status_31(self, video):
        self.status_sync(video=video, status=31)
        video.sync_start_time = datetime.now()
        video.status = 31
        session.commit()

    def update_status_32(self, video):
        self.status_sync(video=video, status=32)
        video.sync_finish_time = datetime.now()
        video.delete_time = datetime.now()
        video.status = 32
        video.is_deleted = 1
        session.commit()


if __name__ == '__main__':
    downloader = Downloader()
    while 1:
        downloader.run()
