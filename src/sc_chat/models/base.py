from sqlalchemy import Column, DateTime, Integer, func


class TimestampMixin:
    """
    Timestamping Mixin for SQLAlchemy models.
    This mixin adds id, created_at and updated_at fields to the model.
    - id: Unique identifier for the record.
    - created_at: Timestamp of when the record was created.
    - updated_at: Timestamp of when the record was last updated.
    """

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
