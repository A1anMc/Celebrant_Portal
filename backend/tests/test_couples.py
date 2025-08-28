"""
Tests for couple management functionality.
Tests both service layer and API endpoints.
"""

import pytest
from fastapi import status
from datetime import datetime, timedelta

from app.services.couple_service import CoupleService
from app.core.exceptions import CoupleNotFoundException, ValidationException


def test_create_couple_success(authenticated_client, test_user):
    """Test successful couple creation."""
    couple_data = {
        "partner1_name": "John Doe",
        "partner1_email": "john@example.com",
        "partner2_name": "Jane Smith",
        "partner2_email": "jane@example.com",
        "wedding_date": "2025-12-25T10:00:00",
        "venue": "St. Patrick's Cathedral",
        "ceremony_type": "Wedding",
        "status": "Booked"
    }
    
    response = authenticated_client.post("/api/v1/couples/", json=couple_data)
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    assert data["partner1_name"] == "John Doe"
    assert data["partner2_name"] == "Jane Smith"
    assert data["venue"] == "St. Patrick's Cathedral"
    assert data["celebrant_id"] == test_user.id


def test_create_couple_validation_error(authenticated_client, test_user):
    """Test couple creation with validation errors."""
    # Test with past wedding date
    couple_data = {
        "partner1_name": "John Doe",
        "partner1_email": "john@example.com",
        "partner2_name": "Jane Smith",
        "partner2_email": "jane@example.com",
        "wedding_date": "2020-01-01T10:00:00",  # Past date
        "venue": "St. Patrick's Cathedral"
    }
    
    response = authenticated_client.post("/api/v1/couples/", json=couple_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_couples_success(authenticated_client, test_user, test_couple):
    """Test getting couples list."""
    response = authenticated_client.get("/api/v1/couples/")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["partner1_name"] == test_couple.partner1_name


def test_get_couples_with_filters(authenticated_client, test_user, test_couple):
    """Test getting couples with filters."""
    # Test search filter
    response = authenticated_client.get("/api/v1/couples/?search=John")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    
    # Test status filter
    response = authenticated_client.get("/api/v1/couples/?status=Booked")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    
    # Test empty search
    response = authenticated_client.get("/api/v1/couples/?search=nonexistent")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 0


def test_get_couple_by_id_success(authenticated_client, test_user, test_couple):
    """Test getting a specific couple."""
    response = authenticated_client.get(f"/api/v1/couples/{test_couple.id}")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["id"] == test_couple.id
    assert data["partner1_name"] == test_couple.partner1_name


def test_get_couple_by_id_not_found(authenticated_client, test_user):
    """Test getting a non-existent couple."""
    response = authenticated_client.get("/api/v1/couples/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_couple_success(authenticated_client, test_user, test_couple):
    """Test updating a couple."""
    update_data = {
        "venue": "Updated Venue",
        "notes": "Updated notes"
    }
    
    response = authenticated_client.put(f"/api/v1/couples/{test_couple.id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["venue"] == "Updated Venue"
    assert data["notes"] == "Updated notes"


def test_update_couple_not_found(authenticated_client, test_user):
    """Test updating a non-existent couple."""
    update_data = {"venue": "Updated Venue"}
    
    response = authenticated_client.put("/api/v1/couples/999", json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_couple_success(authenticated_client, test_user, test_couple):
    """Test deleting a couple."""
    response = authenticated_client.delete(f"/api/v1/couples/{test_couple.id}")
    assert response.status_code == status.HTTP_200_OK
    
    # Verify couple is deleted
    response = authenticated_client.get(f"/api/v1/couples/{test_couple.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_couple_not_found(authenticated_client, test_user):
    """Test deleting a non-existent couple."""
    response = authenticated_client.delete("/api/v1/couples/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_couple_statistics(authenticated_client, test_user, test_couple):
    """Test getting couple statistics."""
    response = authenticated_client.get("/api/v1/couples/statistics/")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "total_couples" in data
    assert "inquiries" in data
    assert "booked" in data
    assert "completed" in data
    assert "upcoming_weddings" in data


def test_search_couples(authenticated_client, test_user, test_couple):
    """Test searching couples."""
    response = authenticated_client.get("/api/v1/couples/search/?q=John")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["partner1_name"] == test_couple.partner1_name


def test_search_couples_no_results(authenticated_client, test_user):
    """Test searching couples with no results."""
    response = authenticated_client.get("/api/v1/couples/search/?q=nonexistent")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert len(data) == 0


# Service layer tests
def test_couple_service_get_couples(db_session, test_user, test_couple):
    """Test CoupleService.get_couples method."""
    couples = CoupleService.get_couples(db_session, test_user.id)
    assert len(couples) == 1
    assert couples[0].id == test_couple.id


def test_couple_service_get_couple_by_id(db_session, test_user, test_couple):
    """Test CoupleService.get_couple_by_id method."""
    couple = CoupleService.get_couple_by_id(db_session, test_couple.id, test_user.id)
    assert couple.id == test_couple.id
    assert couple.partner1_name == test_couple.partner1_name


def test_couple_service_get_couple_by_id_not_found(db_session, test_user):
    """Test CoupleService.get_couple_by_id with non-existent couple."""
    with pytest.raises(CoupleNotFoundException):
        CoupleService.get_couple_by_id(db_session, 999, test_user.id)


def test_couple_service_create_couple(db_session, test_user):
    """Test CoupleService.create_couple method."""
    from app.schemas import CoupleCreate
    
    couple_data = CoupleCreate(
        partner1_name="New Partner 1",
        partner1_email="partner1@example.com",
        partner2_name="New Partner 2",
        partner2_email="partner2@example.com",
        wedding_date=datetime.now() + timedelta(days=30),
        venue="Test Venue"
    )
    
    couple = CoupleService.create_couple(db_session, couple_data, test_user.id)
    assert couple.partner1_name == "New Partner 1"
    assert couple.celebrant_id == test_user.id


def test_couple_service_create_couple_past_date(db_session, test_user):
    """Test CoupleService.create_couple with past wedding date."""
    from app.schemas import CoupleCreate
    
    couple_data = CoupleCreate(
        partner1_name="New Partner 1",
        partner1_email="partner1@example.com",
        partner2_name="New Partner 2",
        partner2_email="partner2@example.com",
        wedding_date=datetime.now() - timedelta(days=30),  # Past date
        venue="Test Venue"
    )
    
    with pytest.raises(ValidationException):
        CoupleService.create_couple(db_session, couple_data, test_user.id)


def test_couple_service_get_statistics(db_session, test_user, test_couple):
    """Test CoupleService.get_couple_statistics method."""
    stats = CoupleService.get_couple_statistics(db_session, test_user.id)
    
    assert stats["total_couples"] == 1
    assert "inquiries" in stats
    assert "booked" in stats
    assert "completed" in stats
    assert "upcoming_weddings" in stats


def test_couple_service_search_couples(db_session, test_user, test_couple):
    """Test CoupleService.search_couples method."""
    results = CoupleService.search_couples(db_session, test_user.id, "John")
    assert len(results) == 1
    assert results[0].partner1_name == test_couple.partner1_name
