from sqlalchemy import Column, String, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Video(Base):
    __tablename__ = 'videos'
    id = Column(Integer, primary_key=True)
    date_created = Column(DateTime, default=func.current_timestamp())
    date_modified = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    vid = Column(Integer, index=True)
    for_test = Column(Integer, index=True)  # 0或1
    size = Column(String(255))
    format = Column(String(16))
    status = Column(Integer, index=True)
    sync_start_time = Column(DateTime, index=True)
    sync_finish_time = Column(DateTime, index=True)
    is_deleted = Column(Integer, index=True, default=0)  # 0或1
    delete_time = Column(DateTime, index=True)


if __name__ == '__main__':
    pass
    # DB_init.create_all_tables()
    # DB_init.drop_all_tables()
    # DB_init.create_table(WebMonitor)
    # DB_init.drop_table(WebMonitor)
