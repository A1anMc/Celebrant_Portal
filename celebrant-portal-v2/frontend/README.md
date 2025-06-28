# Melbourne Celebrant Portal - Frontend

This is the frontend application for the Melbourne Celebrant Portal, built with Next.js 15, TypeScript, and Tailwind CSS.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Backend API running on http://localhost:8000

### Development Setup
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## 🎨 Melbourne Celebrant Styling

### Brand Colors
- Primary: #D4A373 (warm gold)
- Secondary: #F7E6D7 (cream)
- Accent: #E9C9D1 (soft pink)
- Background: #FEFCF9 (off-white)

### Typography
- Headers: Playfair Display (serif)
- Body: Inter (sans-serif)

### Styling System
- **Framework**: Tailwind CSS with custom configuration
- **Components**: Card, Button, Input with Melbourne Celebrant branding
- **Global Styles**: `app/globals.css` with custom classes and utilities
- **Config**: `tailwind.config.ts` with custom colors and fonts

## 📁 Project Structure

```
frontend/
├── app/                          # Next.js App Router
│   ├── layout.tsx                # Root layout with fonts
│   ├── page.tsx                  # Landing page
│   ├── globals.css               # Melbourne Celebrant styling
│   ├── login/                    # Authentication
│   ├── dashboard/                # Main dashboard
│   ├── couples/                  # Couple management
│   ├── ceremonies/               # Ceremony tracking
│   ├── legal-forms/              # NOIM compliance
│   ├── invoices/                 # Financial management
│   ├── templates/                # Ceremony templates
│   ├── reports/                  # Business analytics
│   └── settings/                 # User preferences
├── src/                          # Source code
│   ├── components/               # Reusable UI components
│   ├── contexts/                 # React contexts (AuthContext)
│   ├── services/                 # API clients
│   ├── types/                    # TypeScript definitions
│   └── lib/                      # Utility functions
├── public/                       # Static assets
├── package.json                  # Dependencies
├── tailwind.config.ts            # Tailwind configuration
├── next.config.js                # Next.js configuration
└── vercel.json                   # Vercel deployment config
```

## 🔧 Key Features

- **Authentication**: Secure login/logout with JWT tokens
- **Dashboard**: Business metrics and overview
- **Couple Management**: Add, edit, search couples
- **Ceremony Tracking**: Schedule and manage ceremonies
- **Legal Compliance**: NOIM tracking and deadlines
- **Financial Management**: Invoice creation and tracking
- **Templates**: Ceremony script management
- **Reports**: Business analytics and insights
- **Settings**: User preferences and configuration

## 🌐 Environment Variables

Create `.env.local` in the frontend directory:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_APP_NAME=Melbourne Celebrant Portal
NEXT_PUBLIC_APP_VERSION=2.0.0
```

## 🚀 Deployment

### Vercel (Recommended)
1. Connect your GitHub repository to Vercel
2. Set root directory to `frontend`
3. Add environment variables in Vercel dashboard
4. Deploy automatically on git push

### Manual Build
```bash
npm run build
npm start
```

## 🛠️ Development

### Adding New Pages
1. Create page in `app/` directory
2. Follow Next.js App Router conventions
3. Apply Melbourne Celebrant styling classes
4. Add navigation link in `DashboardLayout.tsx`

### Styling Guidelines
- Use Melbourne Celebrant color classes: `bg-primary`, `text-primary-dark`
- Apply consistent card styling: `card`, `card-header`, `card-content`
- Use serif fonts for headers: `font-serif`
- Include hover effects and animations

### API Integration
- Use services in `src/services/` for API calls
- Handle authentication with `AuthContext`
- Implement proper error handling and loading states

## 📚 Documentation

For complete project documentation, see the main README in the project root: `../README.md`

## 🔗 Links

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Production Frontend**: https://your-app.vercel.app
- **Production API**: https://your-backend.onrender.com
