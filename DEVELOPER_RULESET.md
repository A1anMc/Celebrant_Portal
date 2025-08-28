# 🏗️ Professional Developer Ruleset
## Melbourne Celebrant Portal v0.2.0

*This ruleset defines the development standards, best practices, and expectations for all contributors to the Melbourne Celebrant Portal project.*

---

## 📋 **Table of Contents**

1. [Code Quality Standards](#code-quality-standards)
2. [Architecture Principles](#architecture-principles)
3. [Security Requirements](#security-requirements)
4. [Testing Standards](#testing-standards)
5. [Documentation Requirements](#documentation-requirements)
6. [Git Workflow](#git-workflow)
7. [Performance Standards](#performance-standards)
8. [API Design Standards](#api-design-standards)
9. [Database Standards](#database-standards)
10. [Frontend Standards](#frontend-standards)
11. [DevOps Standards](#devops-standards)
12. [Code Review Process](#code-review-process)

---

## 🎯 **Code Quality Standards**

### **Python (Backend)**
```python
# ✅ GOOD
class CoupleService:
    """Service class for couple management operations."""
    
    @staticmethod
    async def create_couple(db: Session, couple_data: CoupleCreate, user_id: int) -> Couple:
        """Create a new couple for a celebrant.
        
        Args:
            db: Database session
            couple_data: Couple creation data
            user_id: ID of the celebrant
            
        Returns:
            Created couple object
            
        Raises:
            ValidationException: If data validation fails
        """
        try:
            # Validate wedding date
            if couple_data.wedding_date < datetime.now():
                raise ValidationException("Wedding date cannot be in the past")
            
            couple = Couple(**couple_data.dict(), celebrant_id=user_id)
            db.add(couple)
            db.commit()
            db.refresh(couple)
            return couple
            
        except ValidationException:
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseException(f"Failed to create couple: {str(e)}")

# ❌ BAD
def create_couple(db, data, user_id):
    couple = Couple(data=data, user=user_id)
    db.add(couple)
    db.commit()
    return couple
```

#### **Python Rules**
- **Type Hints**: All functions must have complete type annotations
- **Docstrings**: Every function, class, and module must have comprehensive docstrings
- **Error Handling**: Use custom exceptions with proper error messages
- **Async/Await**: Use async functions for I/O operations
- **Line Length**: Maximum 88 characters (Black formatter standard)
- **Imports**: Group imports: standard library, third-party, local
- **Naming**: Use snake_case for functions/variables, PascalCase for classes

### **TypeScript/JavaScript (Frontend)**
```typescript
// ✅ GOOD
interface Couple {
  id: number;
  partner1_name: string;
  partner1_email: string;
  partner2_name: string;
  partner2_email: string;
  wedding_date: string;
  venue?: string;
  status: 'Inquiry' | 'Booked' | 'Completed';
  created_at: string;
  updated_at: string;
}

const createCouple = async (coupleData: Omit<Couple, 'id' | 'created_at' | 'updated_at'>): Promise<Couple> => {
  try {
    const response = await apiClient.post<Couple>('/api/v1/couples/', coupleData);
    return response.data;
  } catch (error) {
    throw new ApiError('Failed to create couple', error);
  }
};

// ❌ BAD
const createCouple = async (data) => {
  const response = await fetch('/api/couples', {
    method: 'POST',
    body: JSON.stringify(data)
  });
  return response.json();
};
```

#### **TypeScript Rules**
- **Strict Mode**: Always use `strict: true` in tsconfig
- **Type Definitions**: Define interfaces for all data structures
- **Error Handling**: Use custom error classes with proper typing
- **Async/Await**: Prefer async/await over Promises
- **Component Props**: Define prop interfaces for all React components
- **State Management**: Use TypeScript for Redux/Context state

---

## 🏛️ **Architecture Principles**

### **1. Separation of Concerns**
```python
# ✅ Service Layer Pattern
class CoupleService:
    @staticmethod
    async def create_couple(db: Session, couple_data: CoupleCreate, user_id: int) -> Couple:
        # Business logic here
        pass

# ✅ API Layer
@router.post("/", response_model=CoupleSchema)
async def create_couple(
    couple: CoupleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await CoupleService.create_couple(db, couple, current_user.id)
```

### **2. Dependency Injection**
```python
# ✅ Use FastAPI's dependency injection
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def get_couples(db: Session = Depends(get_db)):
    return await CoupleService.get_couples(db)
```

### **3. Repository Pattern**
```python
# ✅ Abstract database operations
class CoupleRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, couple: Couple) -> Couple:
        self.db.add(couple)
        self.db.commit()
        self.db.refresh(couple)
        return couple
```

---

## 🔒 **Security Requirements**

### **Authentication & Authorization**
```python
# ✅ JWT Token Validation
@router.get("/protected")
async def protected_endpoint(current_user: User = Depends(get_current_active_user)):
    return {"message": f"Hello {current_user.email}"}

# ✅ Role-Based Access Control
def require_admin(user: User = Depends(get_current_active_user)):
    if not user.is_admin:
        raise AuthorizationException("Admin access required")
    return user
```

### **Input Validation**
```python
# ✅ Pydantic Models
class CoupleCreate(BaseModel):
    partner1_name: str = Field(..., min_length=1, max_length=100)
    partner1_email: EmailStr
    partner2_name: str = Field(..., min_length=1, max_length=100)
    partner2_email: EmailStr
    wedding_date: datetime
    venue: Optional[str] = Field(None, max_length=200)
    
    @validator('wedding_date')
    def validate_wedding_date(cls, v):
        if v < datetime.now():
            raise ValueError('Wedding date cannot be in the past')
        return v
```

### **SQL Injection Prevention**
```python
# ✅ Use SQLAlchemy ORM (prevents SQL injection)
couples = db.query(Couple).filter(Couple.celebrant_id == user_id).all()

# ❌ NEVER use raw SQL with string formatting
# couples = db.execute(f"SELECT * FROM couples WHERE celebrant_id = {user_id}")
```

### **XSS Prevention**
```typescript
// ✅ Sanitize user input
import DOMPurify from 'dompurify';

const sanitizeInput = (input: string): string => {
  return DOMPurify.sanitize(input);
};

// ✅ Use React's built-in XSS protection
const UserInput = ({ content }: { content: string }) => {
  return <div>{content}</div>; // React automatically escapes content
};
```

---

## 🧪 **Testing Standards**

### **Test Structure**
```python
# ✅ Comprehensive test structure
class TestCoupleService:
    def test_create_couple_success(self, db_session, test_user):
        """Test successful couple creation."""
        couple_data = CoupleCreate(
            partner1_name="John Doe",
            partner1_email="john@example.com",
            partner2_name="Jane Smith",
            partner2_email="jane@example.com",
            wedding_date=datetime.now() + timedelta(days=30)
        )
        
        couple = CoupleService.create_couple(db_session, couple_data, test_user.id)
        
        assert couple.partner1_name == "John Doe"
        assert couple.celebrant_id == test_user.id
    
    def test_create_couple_past_date(self, db_session, test_user):
        """Test couple creation with past wedding date."""
        couple_data = CoupleCreate(
            partner1_name="John Doe",
            partner1_email="john@example.com",
            partner2_name="Jane Smith",
            partner2_email="jane@example.com",
            wedding_date=datetime.now() - timedelta(days=30)  # Past date
        )
        
        with pytest.raises(ValidationException):
            CoupleService.create_couple(db_session, couple_data, test_user.id)
```

### **Test Coverage Requirements**
- **Unit Tests**: 90%+ coverage for business logic
- **Integration Tests**: All API endpoints
- **E2E Tests**: Critical user journeys
- **Performance Tests**: Load testing for production endpoints

### **Test Data Management**
```python
# ✅ Use fixtures for test data
@pytest.fixture
def test_couple(db_session, test_user):
    couple = Couple(
        partner1_name="John Doe",
        partner1_email="john@example.com",
        partner2_name="Jane Smith",
        partner2_email="jane@example.com",
        celebrant_id=test_user.id
    )
    db_session.add(couple)
    db_session.commit()
    db_session.refresh(couple)
    return couple
```

---

## 📚 **Documentation Requirements**

### **Code Documentation**
```python
"""
Couple service layer for business logic operations.
Handles all couple-related business operations and data validation.

This module provides a service layer abstraction for couple management,
including CRUD operations, validation, and business logic enforcement.

Example:
    >>> couple_data = CoupleCreate(partner1_name="John", partner1_email="john@example.com")
    >>> couple = await CoupleService.create_couple(db, couple_data, user_id)
    >>> print(couple.partner1_name)
    'John'
"""

class CoupleService:
    """Service class for couple management operations.
    
    This class encapsulates all business logic related to couple management,
    providing a clean interface for the API layer to interact with.
    
    Attributes:
        None (static methods only)
    
    Methods:
        create_couple: Create a new couple
        get_couples: Retrieve couples with filtering
        update_couple: Update existing couple
        delete_couple: Delete a couple
    """
```

### **API Documentation**
```python
@router.post("/", response_model=CoupleSchema, status_code=status.HTTP_201_CREATED)
async def create_couple(
    couple: CoupleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new couple for the current celebrant.
    
    This endpoint allows celebrants to create new couple records in the system.
    The couple will be automatically associated with the authenticated celebrant.
    
    Args:
        couple: Couple creation data validated by Pydantic
        db: Database session injected by FastAPI
        current_user: Authenticated user injected by FastAPI
        
    Returns:
        CoupleSchema: The created couple with all fields populated
        
    Raises:
        HTTPException 422: If validation fails
        HTTPException 500: If database operation fails
        
    Example:
        POST /api/v1/couples/
        {
            "partner1_name": "John Doe",
            "partner1_email": "john@example.com",
            "partner2_name": "Jane Smith",
            "partner2_email": "jane@example.com",
            "wedding_date": "2024-12-25T10:00:00",
            "venue": "St. Patrick's Cathedral"
        }
    """
```

---

## 🔄 **Git Workflow**

### **Branch Naming Convention**
```
feature/couple-management
feature/user-authentication
bugfix/login-validation
hotfix/security-patch
chore/update-dependencies
docs/api-documentation
```

### **Commit Message Format**
```
feat: add couple search functionality

- Implement full-text search across partner names and venue
- Add search endpoint with pagination support
- Include comprehensive test coverage

Closes #123
```

### **Commit Types**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### **Pull Request Requirements**
1. **Title**: Clear, descriptive title
2. **Description**: Detailed description of changes
3. **Tests**: All tests must pass
4. **Coverage**: Maintain or improve test coverage
5. **Documentation**: Update relevant documentation
6. **Review**: Minimum 2 approvals required

---

## ⚡ **Performance Standards**

### **Database Performance**
```python
# ✅ Optimized queries
# Use select() for specific columns
couples = db.query(Couple.id, Couple.partner1_name).filter(
    Couple.celebrant_id == user_id
).all()

# ✅ Use indexes
class Couple(Base):
    __tablename__ = "couples"
    
    id = Column(Integer, primary_key=True, index=True)
    celebrant_id = Column(Integer, ForeignKey("users.id"), index=True)
    wedding_date = Column(DateTime, index=True)
    
    __table_args__ = (
        Index('idx_celebrant_status', 'celebrant_id', 'status'),
    )
```

### **API Performance**
```python
# ✅ Pagination
@router.get("/", response_model=List[CoupleSchema])
async def get_couples(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    return await CoupleService.get_couples(db, skip=skip, limit=limit)

# ✅ Caching
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

@router.get("/statistics/")
@cache(expire=300)  # Cache for 5 minutes
async def get_statistics(db: Session = Depends(get_db)):
    return await CoupleService.get_statistics(db)
```

### **Frontend Performance**
```typescript
// ✅ Lazy loading
const CoupleList = lazy(() => import('./components/CoupleList'));

// ✅ Memoization
const MemoizedCoupleCard = memo(({ couple }: { couple: Couple }) => {
  return <CoupleCard couple={couple} />;
});

// ✅ Virtual scrolling for large lists
import { FixedSizeList as List } from 'react-window';

const VirtualizedCoupleList = ({ couples }: { couples: Couple[] }) => (
  <List
    height={400}
    itemCount={couples.length}
    itemSize={100}
    itemData={couples}
  >
    {CoupleRow}
  </List>
);
```

---

## 🌐 **API Design Standards**

### **RESTful Endpoints**
```
GET    /api/v1/couples/          # List couples
POST   /api/v1/couples/          # Create couple
GET    /api/v1/couples/{id}      # Get specific couple
PUT    /api/v1/couples/{id}      # Update couple
DELETE /api/v1/couples/{id}      # Delete couple
GET    /api/v1/couples/search/   # Search couples
GET    /api/v1/couples/stats/    # Get statistics
```

### **Response Format**
```json
{
  "data": {
    "id": 1,
    "partner1_name": "John Doe",
    "partner1_email": "john@example.com"
  },
  "message": "Couple created successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### **Error Response Format**
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Data validation failed",
  "details": {
    "field_errors": {
      "wedding_date": "Wedding date cannot be in the past"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### **HTTP Status Codes**
- `200 OK`: Successful GET, PUT, PATCH
- `201 Created`: Successful POST
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation errors
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

---

## 🗄️ **Database Standards**

### **Schema Design**
```python
# ✅ Proper relationships
class Couple(Base):
    __tablename__ = "couples"
    
    id = Column(Integer, primary_key=True, index=True)
    celebrant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    partner1_name = Column(String(100), nullable=False)
    partner1_email = Column(String(255), nullable=False)
    partner2_name = Column(String(100), nullable=False)
    partner2_email = Column(String(255), nullable=False)
    wedding_date = Column(DateTime, nullable=True)
    venue = Column(String(200), nullable=True)
    status = Column(Enum('Inquiry', 'Booked', 'Completed'), default='Inquiry')
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    celebrant = relationship("User", back_populates="couples")
    ceremonies = relationship("Ceremony", back_populates="couple", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="couple", cascade="all, delete-orphan")
```

### **Migration Standards**
```python
# ✅ Alembic migrations
"""Add couple status enum

Revision ID: 001_add_couple_status
Revises: 000_initial
Create Date: 2024-01-15 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create enum type
    couple_status = postgresql.ENUM('Inquiry', 'Booked', 'Completed', name='couple_status')
    couple_status.create(op.get_bind())
    
    # Add column with default value
    op.add_column('couples', sa.Column('status', sa.Enum('Inquiry', 'Booked', 'Completed', name='couple_status'), nullable=False, server_default='Inquiry'))

def downgrade():
    op.drop_column('couples', 'status')
    op.execute('DROP TYPE couple_status')
```

---

## 🎨 **Frontend Standards**

### **Component Structure**
```typescript
// ✅ Functional components with hooks
interface CoupleCardProps {
  couple: Couple;
  onEdit: (couple: Couple) => void;
  onDelete: (id: number) => void;
}

const CoupleCard: React.FC<CoupleCardProps> = ({ couple, onEdit, onDelete }) => {
  const [isLoading, setIsLoading] = useState(false);
  
  const handleDelete = async () => {
    setIsLoading(true);
    try {
      await onDelete(couple.id);
    } catch (error) {
      console.error('Failed to delete couple:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Card className="couple-card">
      <CardHeader>
        <CardTitle>{couple.partner1_name} & {couple.partner2_name}</CardTitle>
        <CardSubtitle>{couple.venue}</CardSubtitle>
      </CardHeader>
      <CardContent>
        <p>Wedding Date: {formatDate(couple.wedding_date)}</p>
        <Badge variant={getStatusVariant(couple.status)}>
          {couple.status}
        </Badge>
      </CardContent>
      <CardFooter>
        <Button onClick={() => onEdit(couple)}>Edit</Button>
        <Button 
          variant="destructive" 
          onClick={handleDelete}
          disabled={isLoading}
        >
          {isLoading ? 'Deleting...' : 'Delete'}
        </Button>
      </CardFooter>
    </Card>
  );
};
```

### **State Management**
```typescript
// ✅ Custom hooks for state management
const useCouples = () => {
  const [couples, setCouples] = useState<Couple[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const fetchCouples = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get<Couple[]>('/api/v1/couples/');
      setCouples(response.data);
    } catch (err) {
      setError('Failed to fetch couples');
    } finally {
      setLoading(false);
    }
  };
  
  const createCouple = async (coupleData: CoupleCreate) => {
    try {
      const response = await apiClient.post<Couple>('/api/v1/couples/', coupleData);
      setCouples(prev => [...prev, response.data]);
      return response.data;
    } catch (err) {
      throw new Error('Failed to create couple');
    }
  };
  
  return { couples, loading, error, fetchCouples, createCouple };
};
```

---

## 🚀 **DevOps Standards**

### **Docker Configuration**
```dockerfile
# ✅ Multi-stage build
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Environment Configuration**
```bash
# ✅ Environment-specific configs
# .env.development
DATABASE_URL=postgresql://postgres:password@localhost:5432/celebrant_portal_dev
DEBUG=true
LOG_LEVEL=DEBUG

# .env.production
DATABASE_URL=postgresql://user:pass@prod-db:5432/celebrant_portal
DEBUG=false
LOG_LEVEL=INFO
```

### **CI/CD Pipeline**
```yaml
# ✅ GitHub Actions workflow
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

---

## 👥 **Code Review Process**

### **Review Checklist**
- [ ] **Functionality**: Does the code work as intended?
- [ ] **Security**: Are there any security vulnerabilities?
- [ ] **Performance**: Is the code efficient and scalable?
- [ ] **Testing**: Are there adequate tests?
- [ ] **Documentation**: Is the code well-documented?
- [ ] **Standards**: Does the code follow our standards?
- [ ] **Accessibility**: Is the UI accessible?
- [ ] **Error Handling**: Are errors handled properly?

### **Review Comments**
```python
# ✅ Constructive feedback
# Consider using a more descriptive variable name here
# Current: data
# Suggested: couple_creation_data

# ✅ Suggest improvements
# This could be optimized by using a single query with joins
# instead of multiple database calls

# ✅ Security concerns
# This input should be validated to prevent XSS attacks
```

### **Review Guidelines**
1. **Be Respectful**: Focus on the code, not the person
2. **Be Specific**: Provide concrete examples and suggestions
3. **Be Constructive**: Offer solutions, not just problems
4. **Be Timely**: Respond within 24 hours
5. **Be Thorough**: Check all aspects of the code

---

## 📊 **Quality Metrics**

### **Code Quality Targets**
- **Test Coverage**: 90%+ for business logic
- **Code Complexity**: Cyclomatic complexity < 10
- **Code Duplication**: < 5%
- **Documentation Coverage**: 100% for public APIs
- **Security Scan**: 0 critical/high vulnerabilities

### **Performance Targets**
- **API Response Time**: < 200ms for 95th percentile
- **Database Query Time**: < 100ms for 95th percentile
- **Frontend Load Time**: < 2 seconds for initial load
- **Bundle Size**: < 500KB for main bundle

### **Monitoring Requirements**
- **Error Rate**: < 1% for production
- **Uptime**: 99.9% availability
- **Security Incidents**: 0 per month
- **Performance Degradation**: Alert on > 20% increase

---

## 🎯 **Compliance & Legal**

### **Data Protection**
- **GDPR Compliance**: All personal data handling must comply with GDPR
- **Data Encryption**: All sensitive data must be encrypted at rest and in transit
- **Data Retention**: Implement proper data retention policies
- **User Consent**: Obtain explicit consent for data processing

### **Accessibility**
- **WCAG 2.1 AA**: All UI components must meet WCAG 2.1 AA standards
- **Screen Reader Support**: All interactive elements must be accessible
- **Keyboard Navigation**: Full keyboard navigation support
- **Color Contrast**: Minimum 4.5:1 contrast ratio

### **Licensing**
- **Open Source Compliance**: All third-party libraries must be compatible with our license
- **License Attribution**: Proper attribution for all used libraries
- **Commercial License**: Ensure all components can be used commercially

---

## 📞 **Support & Escalation**

### **Development Support**
- **Technical Questions**: Use project Slack/Teams channel
- **Architecture Decisions**: Create ADR (Architecture Decision Record)
- **Security Issues**: Immediate escalation to security team
- **Production Issues**: Follow incident response procedure

### **Escalation Path**
1. **Developer** → **Tech Lead** → **Engineering Manager** → **CTO**
2. **Security Issues**: Direct escalation to security team
3. **Production Issues**: Immediate escalation to DevOps team

---

**Last Updated**: January 15, 2024  
**Version**: 1.0.0  
**Next Review**: March 15, 2024

---

*This ruleset is a living document that will be updated as the project evolves and new best practices emerge. All contributors are expected to follow these standards and suggest improvements when appropriate.*
