from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric, ForeignKey, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class TravelLog(Base):
    __tablename__ = "travel_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Trip Information
    trip_date = Column(Date, nullable=False, index=True)
    purpose = Column(String(255), nullable=False)
    
    # Location Information
    origin_address = Column(Text, nullable=False)
    destination_address = Column(Text, nullable=False)
    distance_km = Column(Numeric(8, 2))
    
    # Financial Information
    travel_rate = Column(Numeric(5, 2), default=0.68)  # ATO rate per km
    total_cost = Column(Numeric(10, 2))
    additional_expenses = Column(Numeric(10, 2), default=0)  # Parking, tolls, etc.
    
    # Trip Details
    departure_time = Column(String(10))  # HH:MM format
    arrival_time = Column(String(10))
    return_departure_time = Column(String(10))
    return_arrival_time = Column(String(10))
    
    # Vehicle Information
    vehicle_type = Column(String(50), default="personal")  # personal, rental, public_transport
    fuel_cost = Column(Numeric(10, 2))
    
    # Status
    status = Column(String(50), default="completed")  # planned, completed, cancelled
    is_billable = Column(String(20), default="yes")  # yes, no, partial
    
    # Notes
    notes = Column(Text)
    
    # Relationships
    couple_id = Column(Integer, ForeignKey("couples.id"))
    couple = relationship("Couple", back_populates="travel_logs")
    
    ceremony_id = Column(Integer, ForeignKey("ceremonies.id"))
    ceremony = relationship("Ceremony", back_populates="travel_logs")
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="travel_logs")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    @property
    def calculated_travel_cost(self):
        """Calculate travel cost based on distance and rate."""
        if self.distance_km and self.travel_rate:
            return float(self.distance_km) * float(self.travel_rate)
        return 0
    
    @property
    def total_trip_cost(self):
        """Calculate total trip cost including additional expenses."""
        base_cost = self.total_cost or self.calculated_travel_cost
        return base_cost + (self.additional_expenses or 0)
    
    def __repr__(self):
        return f"<TravelLog(id={self.id}, date='{self.trip_date}', purpose='{self.purpose}')>"


# Add relationships to other models
from .couple import Couple
Couple.travel_logs = relationship("TravelLog", back_populates="couple")

from .ceremony import Ceremony
Ceremony.travel_logs = relationship("TravelLog", back_populates="ceremony")

from .user import User
User.travel_logs = relationship("TravelLog", back_populates="user") 