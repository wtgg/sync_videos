import json

from application.MQ import Cus
from application.ext import session, GetInsertOrUpdateObj
from application.models import Video
from config import logger, 国恒信创采集MQ


class App:

    def run(self):
        pass


class MQ_C(Cus):

    def __init__(self, *args):
        super().__init__(*args)

    @staticmethod
    def callback(ch, method, properties, body):
        d = json.loads(body.decode())
        vid = int(d.pop('id'))
        data = {}
        data['vid'] = vid
        data.update(d)
        filter_dict = dict(
            vid=data.get('vid'),
            for_test=int(data.get('for_test'))
        )
        video = GetInsertOrUpdateObj(Video, data, filter_dict)
        video_id = video.id
        session.add(video)
        session.flush()
        table_id = video.id
        session.commit()
        if video_id == table_id:
            logger.warning(f'更新数据table_id:{table_id}')
        else:
            logger.warning(f'新增数据table_id:{table_id}')


if __name__ == '__main__':
    consumer = MQ_C(国恒信创采集MQ.config)
    consumer.run()
