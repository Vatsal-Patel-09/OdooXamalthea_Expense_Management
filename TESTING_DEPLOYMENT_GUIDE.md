# 🧪 Testing & Deployment Guide

## Pre-Deployment Testing Checklist

### ✅ Functionality Testing

#### Authentication
- [ ] Signup works with valid data
- [ ] Signup validates email format
- [ ] Signup validates password length (min 8 chars)
- [ ] Country selection auto-fills currency
- [ ] Country dropdown scrolls properly
- [ ] Login works with correct credentials
- [ ] Login fails with incorrect credentials
- [ ] Logout clears session
- [ ] Protected routes redirect to login

#### Theme Toggle
- [ ] Theme toggle visible on all pages
- [ ] Can switch to Light mode
- [ ] Can switch to Dark mode
- [ ] Can switch to System mode
- [ ] Theme persists after page reload
- [ ] Theme applies correctly across all pages
- [ ] No FOUC (Flash of Unstyled Content)
- [ ] Smooth transition between themes

#### Dashboard
- [ ] Stats cards display correct counts
- [ ] Recent expenses load correctly
- [ ] Create expense button navigates correctly
- [ ] View all expenses button navigates correctly
- [ ] Click on expense navigates to detail view
- [ ] Empty state shows when no expenses
- [ ] Loading state shows while fetching

#### Expenses List
- [ ] All expenses load correctly
- [ ] Search filters expenses correctly
- [ ] Status filter works
- [ ] Can click to view expense details
- [ ] Edit button works for draft expenses
- [ ] Submit button works for draft expenses
- [ ] Delete button works for draft expenses
- [ ] View button works for non-draft expenses
- [ ] Receipt link opens in new tab
- [ ] Empty state shows when no results
- [ ] Stats cards show correct counts

#### Expense Details
- [ ] Expense details load correctly
- [ ] Status badge displays correctly
- [ ] Amount displays correctly
- [ ] Date formats correctly
- [ ] Category shows correctly
- [ ] Description displays if present
- [ ] Receipt link works if present
- [ ] Submitter info shows correctly
- [ ] Edit button shows for drafts
- [ ] Submit button shows for drafts
- [ ] Back button navigates correctly
- [ ] Error state shows for invalid IDs

### 📱 Responsive Testing

#### Mobile (375px - 767px)
- [ ] Navbar collapses to hamburger menu
- [ ] Mobile menu opens/closes correctly
- [ ] All cards stack vertically
- [ ] Buttons are touch-friendly (44x44px min)
- [ ] Text is readable (14px+ font size)
- [ ] Forms are usable with soft keyboard
- [ ] Scrolling works smoothly
- [ ] No horizontal scroll
- [ ] Images scale appropriately

#### Tablet (768px - 1023px)
- [ ] Grid layouts use 2 columns where appropriate
- [ ] Navigation shows all items
- [ ] Cards display properly
- [ ] Forms are comfortable to use
- [ ] Stats cards in 2x2 grid

#### Desktop (1024px+)
- [ ] Full navigation visible
- [ ] Optimal use of screen space
- [ ] Stats cards in single row
- [ ] Forms use appropriate width
- [ ] No wasted whitespace
- [ ] Hover effects work

### 🎨 Visual Testing

#### Light Mode
- [ ] All text is readable
- [ ] Sufficient contrast ratios (4.5:1 min)
- [ ] Borders are visible
- [ ] Cards have proper shadows
- [ ] Primary green looks professional
- [ ] Status badges are distinct
- [ ] No pure black (#000000)
- [ ] Consistent spacing

#### Dark Mode
- [ ] All text is readable
- [ ] Sufficient contrast ratios (4.5:1 min)
- [ ] Borders are visible
- [ ] Cards stand out from background
- [ ] Primary green is bright enough
- [ ] Status badges are distinct
- [ ] No pure white (#FFFFFF)
- [ ] Consistent spacing

### ♿ Accessibility Testing

#### Keyboard Navigation
- [ ] Tab order is logical
- [ ] All interactive elements focusable
- [ ] Focus indicators visible
- [ ] Can navigate entire app with keyboard
- [ ] Escape closes modals/dropdowns
- [ ] Enter/Space activates buttons
- [ ] Arrow keys work in dropdowns

#### Screen Readers
- [ ] All images have alt text
- [ ] Form fields have labels
- [ ] Buttons have descriptive text
- [ ] Status updates announced
- [ ] Error messages announced
- [ ] Loading states announced
- [ ] ARIA labels where needed

#### Color Blindness
- [ ] Not relying solely on color for info
- [ ] Status uses icons + color
- [ ] Sufficient contrast in all modes
- [ ] Patterns/icons supplement color

### ⚡ Performance Testing

#### Load Times
- [ ] Initial page load < 3 seconds
- [ ] Time to Interactive < 3 seconds
- [ ] First Contentful Paint < 2 seconds
- [ ] Largest Contentful Paint < 2.5 seconds
- [ ] No layout shifts (CLS < 0.1)

#### Network
- [ ] Works on slow 3G
- [ ] Handles offline gracefully
- [ ] Shows loading states
- [ ] Error handling for failed requests
- [ ] No unnecessary re-fetches

#### Bundle Size
- [ ] Total JS < 500KB gzipped
- [ ] CSS < 100KB gzipped
- [ ] Images optimized (webp preferred)
- [ ] Fonts optimized (woff2)
- [ ] No unused dependencies

### 🔒 Security Testing

- [ ] No sensitive data in localStorage
- [ ] Tokens are httpOnly (backend)
- [ ] HTTPS in production
- [ ] No console.log in production
- [ ] Input sanitization
- [ ] CSRF protection
- [ ] XSS protection
- [ ] Rate limiting on API

## 🚀 Deployment Steps

### 1. Pre-Deployment

\`\`\`bash
# Run all tests
cd frontend
pnpm test

# Check for TypeScript errors
pnpm tsc --noEmit

# Run linter
pnpm lint

# Build for production
pnpm build

# Test production build locally
pnpm start
\`\`\`

### 2. Environment Variables

Create `.env.production`:
\`\`\`env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_key
\`\`\`

### 3. Deployment (Vercel)

\`\`\`bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
cd frontend
vercel --prod
\`\`\`

### 4. Post-Deployment

- [ ] Verify all pages load
- [ ] Test critical user flows
- [ ] Check analytics integration
- [ ] Monitor error tracking
- [ ] Run Lighthouse audit
- [ ] Test on real devices
- [ ] Check all environment variables
- [ ] Verify API endpoints

## 📊 Monitoring

### Metrics to Track

1. **Performance**
   - Page load times
   - API response times
   - Error rates
   - User sessions

2. **User Behavior**
   - Most used features
   - Drop-off points
   - Search queries
   - Theme preference

3. **Technical**
   - Browser versions
   - Device types
   - Screen resolutions
   - Network speeds

### Tools

- **Analytics**: Google Analytics / Plausible
- **Error Tracking**: Sentry
- **Performance**: Lighthouse CI / WebPageTest
- **Uptime**: UptimeRobot / Pingdom

## 🐛 Common Issues & Fixes

### Theme Not Persisting
**Issue**: Theme resets on page reload
**Fix**: Check localStorage is enabled, verify ThemeProvider in layout.tsx

### Navbar Not Sticky
**Issue**: Navbar scrolls with page
**Fix**: Check `position: sticky` in Navbar component

### Mobile Menu Not Closing
**Issue**: Menu stays open after clicking link
**Fix**: Add setMobileMenuOpen(false) to all nav links

### Country Dropdown Not Scrolling
**Issue**: Can't scroll to see all countries
**Fix**: Verify max-h and overflow-y-auto classes on select

### Dark Mode Colors Wrong
**Issue**: Text not visible in dark mode
**Fix**: Check CSS variables in globals.css .dark section

### API Calls Failing
**Issue**: 404 or CORS errors
**Fix**: Verify NEXT_PUBLIC_API_URL and backend CORS settings

## 📝 Release Notes Template

\`\`\`markdown
# Release v1.0.0 - Frontend Redesign

## 🎨 New Features
- Complete UI redesign with modern green theme
- Dark/Light/System theme support
- Fully responsive design for all devices
- Improved navigation with mobile menu
- Enhanced expense viewing experience

## 🐛 Bug Fixes
- Fixed country selector scrolling issue
- Improved form validation feedback
- Better error handling and messages

## 🚀 Performance
- Optimized bundle size
- Faster page loads
- Smooth animations

## ⚠️ Breaking Changes
- None

## 📦 Dependencies Updated
- next-themes@0.4.6
- lucide-react@0.544.0
- @radix-ui/react-dialog@1.1.15

## 🔄 Migration Guide
- No migration needed
- Theme preference will default to system

## 🙏 Contributors
- Your Name
\`\`\`

## 🎯 Success Criteria

Deployment is successful when:
- [ ] ✅ All critical paths work (signup, login, dashboard, expenses)
- [ ] ✅ No console errors in production
- [ ] ✅ Lighthouse score > 90
- [ ] ✅ No accessibility issues
- [ ] ✅ Mobile experience is smooth
- [ ] ✅ Theme toggle works perfectly
- [ ] ✅ All pages are responsive
- [ ] ✅ Loading/error states work
- [ ] ✅ API integration successful
- [ ] ✅ Monitoring is active

---

## Quick Test Commands

\`\`\`bash
# Run development server
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start

# Run linter
pnpm lint

# Check types
pnpm tsc --noEmit
\`\`\`

## Need Help?

1. Check console for errors
2. Verify environment variables
3. Clear browser cache
4. Test in incognito mode
5. Check network tab in DevTools

---

✨ **Ready to deploy a production-grade expense tracker!** ✨
