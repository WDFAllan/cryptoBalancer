from datetime import datetime
from typing import List
from sqlalchemy.orm import Session

from app.domain.models.portfolioValue import PortfolioValue
from app.domain.port.portfolioValuePort import IPortfolioValuePort
from app.infrastructure.models.portfolioValueTable import PortfolioValueTable


class PortfolioValueRepository(IPortfolioValuePort):

    def __init__(self, db: Session):
        self.db = db

    def create(self, userId: int, date: datetime, totalValue: float) -> PortfolioValue:
        entity = PortfolioValueTable(
            userId=userId,
            date=date,
            totalValue=totalValue
        )
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        
        return PortfolioValue(
            id=entity.id,
            userId=entity.userId,
            date=entity.date,
            totalValue=entity.totalValue,
            createdAt=entity.createdAt
        )

    def getByUserId(self, userId: int) -> List[PortfolioValue]:
        entities = (
            self.db.query(PortfolioValueTable)
            .filter(PortfolioValueTable.userId == userId)
            .order_by(PortfolioValueTable.date.asc())
            .all()
        )
        
        return [
            PortfolioValue(
                id=entity.id,
                userId=entity.userId,
                date=entity.date,
                totalValue=entity.totalValue,
                createdAt=entity.createdAt
            )
            for entity in entities
        ]

    def getByUserIdAndDateRange(self, userId: int, startDate: datetime, endDate: datetime) -> List[PortfolioValue]:
        entities = (
            self.db.query(PortfolioValueTable)
            .filter(
                PortfolioValueTable.userId == userId,
                PortfolioValueTable.date >= startDate,
                PortfolioValueTable.date <= endDate
            )
            .order_by(PortfolioValueTable.date.asc())
            .all()
        )
        
        return [
            PortfolioValue(
                id=entity.id,
                userId=entity.userId,
                date=entity.date,
                totalValue=entity.totalValue,
                createdAt=entity.createdAt
            )
            for entity in entities
        ]

    def getLatestByUserId(self, userId: int) -> PortfolioValue | None:
        entity = (
            self.db.query(PortfolioValueTable)
            .filter(PortfolioValueTable.userId == userId)
            .order_by(PortfolioValueTable.date.desc())
            .first()
        )
        
        if not entity:
            return None
        
        return PortfolioValue(
            id=entity.id,
            userId=entity.userId,
            date=entity.date,
            totalValue=entity.totalValue,
            createdAt=entity.createdAt
        )

