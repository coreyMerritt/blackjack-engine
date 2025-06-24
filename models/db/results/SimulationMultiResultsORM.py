from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.db.Base import Base

class SimulationMultiResultsORM(Base):
  __tablename__ = "simulation_multi_results"

  id = Column(Integer, primary_key=True, autoincrement=True)
  metadata_id = Column(Integer, ForeignKey("simulation_multi_results_metadata.id"))
  average_id = Column(Integer, ForeignKey("simulation_single_results.id"))

  metadata = relationship("SimulationMultiResultsMetadataORM", uselist=False)
  average = relationship("SimulationSingleResultsORM", uselist=False)
