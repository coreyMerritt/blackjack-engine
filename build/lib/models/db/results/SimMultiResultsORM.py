from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.db.Base import Base

class SimMultiResultsORM(Base):
  __tablename__ = "simulation_multi_results"

  id = Column(Integer, primary_key=True, autoincrement=True)
  metadata_id = Column(Integer, ForeignKey("simulation_multi_results_metadata.id"))
  average_id = Column(Integer, ForeignKey("simulation_single_results.id"))

  metadata = relationship("SimMultiResultsMetadataORM", uselist=False)
  average = relationship("SimSingleResultsORM", uselist=False)
