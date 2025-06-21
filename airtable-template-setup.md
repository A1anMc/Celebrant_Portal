# Airtable Template Setup Instructions

## Quick Start
Template URL: [Media Project Management Template](https://airtable.com/shrTEMPLATEID)
1. Click "Use Template" to duplicate to your workspace
2. Customize fields and views as needed

## Manual Setup Instructions
If you prefer to set up the template manually or can't access the template, follow these detailed instructions.

### 1. Project Overview Base

#### Projects Table Setup
```
Table Name: Projects
Fields:
[Single Line Text]    Name: Project Name
[Single Select]       Name: Status
                     Options: 
                     - Planning {color: blue}
                     - In Progress {color: yellow}
                     - Review {color: orange}
                     - Complete {color: green}
[Long Text]          Name: Problem Statement
[Long Text]          Name: Vision Statement
[Long Text]          Name: Mission Statement
[Date]              Name: Start Date
[Date]              Name: Target Completion
[Single Line Text]   Name: Project Lead
[Multiple Select]    Name: Key Stakeholders
[Currency]          Name: Budget {Precision: 2}
[URL]               Name: Links to Documents
```

#### Value Propositions Table Setup
```
Table Name: Value Propositions
Fields:
[Link]              Name: Project
                    Link to: Projects
[Long Text]         Name: Unique Elements
[Multiple Select]   Name: Target Audience
[Long Text]         Name: Market Gap
[Long Text]         Name: Competitive Advantage
[Long Text]         Name: Distribution Strategy
[Long Text]         Name: Success Metrics
```

### 2. Audience & Market Analysis Base

#### Target Audiences Table Setup
```
Table Name: Target Audiences
Fields:
[Single Line Text]  Name: Segment Name
[Single Select]     Name: Type
                    Options:
                    - Primary {color: green}
                    - Secondary {color: blue}
[Single Line Text]  Name: Age Range
[Multiple Select]   Name: Geographic Location
[Long Text]         Name: Demographics
[Long Text]         Name: Behaviors
[Long Text]         Name: Needs/Pain Points
[Multiple Select]   Name: Platform Preferences
                    Options:
                    - Social Media
                    - Website
                    - Mobile App
                    - TV
                    - Radio
                    - Print
[Rating]           Name: Engagement Level {Max: 5}
```

#### Competitor Analysis Table Setup
```
Table Name: Competitor Analysis
Fields:
[Single Line Text]  Name: Competitor Name
[Single Select]     Name: Project Type
[Link]             Name: Target Audience
                   Link to: Target Audiences
[Long Text]        Name: Key Strengths
[Long Text]        Name: Limitations
[Percent]         Name: Market Share
[Multiple Select]  Name: Platform Presence
[Date]            Name: Last Updated
[Long Text]        Name: Notes
```

### 3. Goals & Metrics Base

#### Objectives Table Setup
```
Table Name: Objectives
Fields:
[Single Line Text]  Name: Objective Name
[Single Select]     Name: Type
                    Options:
                    - Creative {color: purple}
                    - Audience {color: blue}
                    - Impact {color: green}
                    - Strategic {color: red}
[Long Text]         Name: Description
[Date]             Name: Target Date
[Single Select]     Name: Status
                    Options:
                    - Not Started {color: gray}
                    - In Progress {color: yellow}
                    - At Risk {color: orange}
                    - Complete {color: green}
[Single Line Text]  Name: Owner
[Single Select]     Name: Priority
                    Options:
                    - High {color: red}
                    - Medium {color: yellow}
                    - Low {color: blue}
[Link]             Name: Related Project
                   Link to: Projects
```

#### Key Results Table Setup
```
Table Name: Key Results
Fields:
[Link]             Name: Objective
                   Link to: Objectives
[Single Line Text] Name: Metric Name
[Number]          Name: Target Value
[Number]          Name: Current Value
[Formula]         Name: Progress
                  Formula: {Current Value} / {Target Value} * 100
[Date]            Name: Last Updated
[Single Line Text] Name: Data Source
[Long Text]        Name: Notes
```

### 4. Content Production Base

#### Content Calendar Table Setup
```
Table Name: Content Calendar
Fields:
[Single Line Text] Name: Content Title
[Single Select]    Name: Type
                   Options:
                   - Video
                   - Article
                   - Social Post
                   - Podcast
                   - Event
[Single Select]    Name: Status
                   Options:
                   - Planning {color: gray}
                   - In Production {color: yellow}
                   - Review {color: orange}
                   - Published {color: green}
[Date]            Name: Due Date
[Single Line Text] Name: Assigned To
[Multiple Select]  Name: Platform
[Link]            Name: Target Audience
                  Link to: Target Audiences
[Long Text]       Name: Brief
[Multiple Select] Name: Assets Required
[Single Select]   Name: Review Status
```

## View Configurations

### Projects Base Views
```
View: Project Overview (Grid)
Filters:
- Status is not "Complete"
Group By:
- Status
Sort By:
- Target Completion

View: Project Timeline (Calendar)
Calendar Field:
- Target Completion
```

### Audience Base Views
```
View: Audience Segments (Grid)
Group By:
- Type
Sort By:
- Engagement Level

View: Audience Profiles (Gallery)
Cards:
- Primary Field: Segment Name
- Fields Shown:
  - Demographics
  - Behaviors
  - Platform Preferences
```

### Goals Base Views
```
View: OKR Dashboard (Grid)
Group By:
- Type
Sort By:
- Priority
Fields Shown:
- Objective Name
- Status
- Progress
- Target Date

View: Timeline (Timeline)
Timeline Field:
- Target Date
```

## Automation Scripts

### Status Update Automation
```javascript
let table = base.getTable('Key Results');
let record = input.config();
let objective = await table.selectRecordAsync(record.id);

if (objective.getCellValue('Current Value') >= objective.getCellValue('Target Value')) {
    let objectivesTable = base.getTable('Objectives');
    await objectivesTable.updateRecordAsync(objective.id, {
        'Status': 'Complete'
    });
}
```

### Deadline Notification
```javascript
let table = base.getTable('Content Calendar');
let today = new Date();
let dueDate = record.getCellValue('Due Date');
let daysDiff = (dueDate - today) / (1000 * 60 * 60 * 24);

if (daysDiff <= 3) {
    await sendEmail({
        to: record.getCellValue('Assigned To'),
        subject: `Deadline Approaching: ${record.getCellValue('Content Title')}`,
        body: `Your content piece is due in ${daysDiff} days.`
    });
}
```

## Custom Formulas

### Progress Calculation
```
IF(Target Value > 0,
  ROUND(Current Value / Target Value * 100, 0) & "%",
  "No Target Set"
)
```

### Days Until Due
```
IF(Due Date,
  IF(IS_BEFORE(TODAY(), Due Date),
    DATETIME_DIFF(TODAY(), Due Date, 'days'),
    "Overdue"
  ),
  "No Due Date"
)
```

## Getting Started Steps

1. Create a new workspace in Airtable
2. Create each base using the configurations above
3. Copy and paste the field configurations for each table
4. Set up the recommended views
5. Configure the automations
6. Add sample data to test the setup
7. Customize the fields and views as needed

## Tips for Customization

1. **Field Modifications**:
   - Add custom fields as needed
   - Modify select options to match your terminology
   - Adjust formulas for your metrics

2. **View Adjustments**:
   - Create additional filtered views for specific teams
   - Customize grouping and sorting
   - Add conditional formatting

3. **Automation Customization**:
   - Modify notification thresholds
   - Add additional conditions
   - Customize notification messages

4. **Integration Setup**:
   - Configure Slack notifications
   - Set up Google Drive links
   - Connect analytics tools 