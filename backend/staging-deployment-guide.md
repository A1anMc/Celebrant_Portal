# 🧪 Staging Environment Deployment Guide

## Overview
This guide covers the staged rollout approach for the Melbourne Celebrant Portal, ensuring safe and controlled deployment to production.

## Phase 1: Staging Environment (Week 1)

### Day 1-2: Infrastructure Setup

#### 1.1 Staging Database Setup
```bash
# Create staging PostgreSQL database
# Use a separate instance from production
DATABASE_URL=postgresql://staging_user:staging_pass@staging-db:5432/celebrant_portal_staging

# Run staging migrations
alembic upgrade head

# Seed staging data
python scripts/seed_staging_data.py
```

#### 1.2 Staging Backend Deployment
```bash
# Deploy to staging environment
# Use Render/Heroku staging environment
STAGING_API_URL=https://celebrant-portal-staging.onrender.com

# Environment variables for staging
ENVIRONMENT=staging
DEBUG=true  # Enable for testing
ALLOWED_ORIGINS=["https://staging.celebrant-portal.com"]
```

#### 1.3 Staging Frontend Deployment
```bash
# Build for staging
NEXT_PUBLIC_API_URL=https://celebrant-portal-staging.onrender.com
npm run build:staging

# Deploy to staging domain
vercel --env staging
```

### Day 3-4: Comprehensive Testing

#### 2.1 Automated Testing Suite
```bash
# Run full test suite against staging
pytest tests/ -v --url=https://celebrant-portal-staging.onrender.com

# Performance testing
python scripts/load_testing.py --target=staging

# Security testing
python scripts/security_audit.py --environment=staging
```

#### 2.2 Manual Testing Checklist
- [ ] User registration and login
- [ ] Couple management (CRUD operations)
- [ ] Invoice generation and management
- [ ] Ceremony planning features
- [ ] Email notifications
- [ ] WebSocket real-time updates
- [ ] Mobile responsiveness
- [ ] Cross-browser compatibility

#### 2.3 Integration Testing
- [ ] Database connectivity and performance
- [ ] API response times
- [ ] File upload/download functionality
- [ ] Payment processing (if applicable)
- [ ] Email delivery system
- [ ] Backup and restore procedures

### Day 5-7: User Acceptance Testing (UAT)

#### 3.1 Internal Team Testing
- [ ] **Development Team**: Technical functionality
- [ ] **QA Team**: Bug hunting and edge cases
- [ ] **Product Team**: User experience validation
- [ ] **Security Team**: Security assessment

#### 3.2 Beta User Testing
- [ ] Invite 5-10 beta users
- [ ] Provide test scenarios and feedback forms
- [ ] Monitor user behavior and feedback
- [ ] Document issues and improvements

#### 3.3 Performance Validation
```bash
# Load testing scenarios
- 10 concurrent users
- 50 concurrent users
- 100 concurrent users
- Database performance under load
- Memory usage monitoring
- Response time analysis
```

## Phase 2: Production Rollout (Week 2)

### Day 8-9: Production Environment Preparation

#### 4.1 Production Infrastructure
```bash
# Production database setup
DATABASE_URL=postgresql://prod_user:secure_pass@prod-db:5432/celebrant_portal

# Production environment variables
ENVIRONMENT=production
DEBUG=false
ALLOWED_ORIGINS=["https://celebrant-portal.com"]
SECRET_KEY=production-secret-key
```

#### 4.2 Blue-Green Deployment Setup
```bash
# Blue environment (current production)
BLUE_API_URL=https://api.celebrant-portal.com

# Green environment (new version)
GREEN_API_URL=https://api-v2.celebrant-portal.com

# Database migration strategy
- Create production database
- Run migrations
- Verify data integrity
```

### Day 10-11: Gradual Rollout

#### 5.1 Traffic Splitting
```bash
# Start with 5% traffic to new version
# Monitor closely for 2 hours
# Increase to 25% if stable
# Monitor for 4 hours
# Increase to 50% if stable
# Monitor for 8 hours
# Increase to 100% if stable
```

#### 5.2 Monitoring During Rollout
```bash
# Real-time monitoring
- Error rates
- Response times
- Database performance
- User feedback
- System resources
```

### Day 12-14: Full Production & Monitoring

#### 6.1 Complete Migration
```bash
# Switch all traffic to new version
# Update DNS records
# Decommission old environment
# Monitor for 48 hours
```

#### 6.2 Post-Deployment Validation
```bash
# Verify all functionality
- User authentication
- Core business processes
- Performance metrics
- Security compliance
- Backup procedures
```

## Monitoring & Alerting

### Key Metrics to Monitor
- [ ] **Application Health**: Uptime, response times
- [ ] **Database Performance**: Query times, connection pool
- [ ] **User Experience**: Page load times, error rates
- [ ] **Security**: Failed login attempts, suspicious activity
- [ ] **Business Metrics**: User registrations, feature usage

### Alert Thresholds
- [ ] Error rate > 1%
- [ ] Response time > 2 seconds
- [ ] Database connection failures
- [ ] Memory usage > 80%
- [ ] Disk space > 85%

## Rollback Procedures

### Quick Rollback (5 minutes)
```bash
# Switch traffic back to previous version
# Update DNS records
# Verify functionality
# Investigate issues
```

### Full Rollback (30 minutes)
```bash
# Restore database from backup
# Deploy previous application version
# Update all configurations
# Verify complete functionality
```

## Success Criteria

### Technical Success
- [ ] 99.9% uptime during rollout
- [ ] <200ms average response time
- [ ] <0.5% error rate
- [ ] Zero data loss
- [ ] All features working correctly

### Business Success
- [ ] User adoption maintained
- [ ] No disruption to business operations
- [ ] Positive user feedback
- [ ] Performance improvements achieved
- [ ] Security enhancements validated

## Communication Plan

### Internal Communication
- [ ] Daily status updates to stakeholders
- [ ] Real-time alerts for critical issues
- [ ] Post-deployment summary report
- [ ] Lessons learned documentation

### User Communication
- [ ] Pre-deployment notification
- [ ] Maintenance window announcements
- [ ] Feature update communications
- [ ] Support contact information

---

## 🎯 Timeline Summary

| Phase | Duration | Key Activities |
|-------|----------|----------------|
| **Staging Setup** | Days 1-2 | Infrastructure, deployment |
| **Testing** | Days 3-4 | Automated and manual testing |
| **UAT** | Days 5-7 | User acceptance testing |
| **Production Prep** | Days 8-9 | Production environment setup |
| **Rollout** | Days 10-11 | Gradual traffic migration |
| **Monitoring** | Days 12-14 | Full production monitoring |

**Total Timeline**: 2 weeks  
**Risk Level**: Low  
**Success Probability**: 95%+
