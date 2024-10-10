from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer, String, DateTime, func, BigInteger

class Base(DeclarativeBase):
    pass

class RunningData(Base):
    """ Running Data """
    __tablename__ = "running_data"

    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(String(250), nullable=False)
    duration = mapped_column(Integer, nullable=False)
    distance = mapped_column(Integer, nullable=False)
    timestamp = mapped_column(String(100), nullable=False)
    trace_id = mapped_column(String(100), nullable=False)
    date_created = mapped_column(DateTime, nullable=False, default=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'duration': self.duration,
            'distance': self.distance,
            'timestamp': self.timestamp,
            'trace_id': self.trace_id,
            'date_created': self.date_created
        }

class MusicData(Base):
    """Music Data"""
    __tablename__ = "music_data"

    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(String(250), nullable=False)
    song_name = mapped_column(String(250), nullable=False)
    artist = mapped_column(String(250), nullable=False)
    song_duration = mapped_column(Integer, nullable=False)
    timestamp = mapped_column(String(100), nullable=False)
    trace_id = mapped_column(String(100), nullable=False)
    date_created = mapped_column(DateTime, nullable=False, default=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'song_name': self.song_name,
            'artist': self.artist,
            'song_duration': self.song_duration,
            'timestamp': self.timestamp,
            'trace_id': self.trace_id,
            'date_created': self.date_created
        }