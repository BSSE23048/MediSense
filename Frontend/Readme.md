# MediSense AI Frontend

## Overview
MediSense AI Frontend is a modern, ultra-minimal Angular 19 application designed for a professional medical platform. It empowers patients with AI-driven medical insights, intelligent report analysis, and natural language symptom checking. The frontend is crafted for clarity, accessibility, and seamless user experience, leveraging a medical-grade color palette and advanced UI features.

## Features
- **Intelligent Healthcare Assistant**: Continuous running text slider for instant engagement.
- **Smooth Navbar Animation**: Responsive pill-shaped navbar that contracts/expands based on scroll direction.
- **Sleek Footer**: Organized, minimal footer with platform, resources, and connect sections.
- **Medical Statistics Visualization**: Chart.js integration for disease prevalence, healthcare access, and AI accuracy charts.
- **Professional Color Scheme**: Deep Navy, AI Teal, Soft Sky, Clean White, Slate Grey, and Soft Red for optimal readability and trust.
- **Accessible Forms**: Clean, readable input and textarea styling for symptom and report submission.
- **File Upload**: Minimal, elegant Choose File button for medical report uploads.
- **About Page**: Detailed platform mission, features, tech stack, and process with visually consistent icons.

## Technology Stack
- **Angular 19**: Standalone components, signals, new control flow syntax
- **TypeScript**: Strict typing for reliability
- **Chart.js 4.4.0**: Medical data visualization
- **Phosphor Icons**: Modern iconography via CDN
- **CSS Variables**: Medical palette, responsive design, and smooth transitions
- **Fonts**: Elms Sans (body), Syncopate (display/headings)

## Folder Structure
```
Frontend/
├── angular.json
├── package.json
├── README.md
├── tsconfig.app.json
├── tsconfig.json
├── tsconfig.spec.json
├── public/
├── src/
│   ├── index.html
│   ├── main.ts
│   ├── styles.css
│   └── app/
│       ├── app.component.*
│       ├── app.config.ts
│       ├── app.routes.ts
│       ├── pages/
│       │   ├── home/
│       │   ├── report/
│       │   ├── symptoms/
│       │   ├── about/
│       │   └── ...
│       └── shared/
│           ├── navbar/
│           ├── footer/
│           ├── text-slider/
│           └── ...
```

## Design System
- **Color Palette**:
  - Deep Navy (`#0B2447`): Headers, navbar, footer
  - AI Teal (`#19A7CE`): Buttons, icons, accents
  - Soft Sky (`#D2E9E9`): Section backgrounds, highlights
  - Clean White (`#FFFFFF`): Cards, input backgrounds
  - Slate Grey (`#334155`): Body text
  - Soft Red (`#EF4444`): Errors, warnings
- **Typography**:
  - Elms Sans: Body text
  - Syncopate: Headings, display
- **Components**:
  - Standalone Angular components for each page and shared UI
  - Responsive grid layouts for features, tech stack, and process
  - Accessible forms and buttons

## Key Components
- `navbar`: Animated, scroll-responsive navigation
- `footer`: Minimal, organized footer
- `text-slider`: Infinite running text for engagement
- `home`: Hero, medical statistics charts, features
- `report`: File upload, AI-powered analysis
- `symptoms`: Natural language symptom checker
- `about`: Mission, features, tech stack, process, disclaimer

## Setup & Installation
1. **Install Dependencies**
   ```sh
   npm install
   ```
2. **Run Development Server**
   ```sh
   npm start
   ```
   or
   ```sh
   ng serve
   ```
3. **Build for Production**
   ```sh
   ng build --configuration production
   ```

## Customization
- **Color Scheme**: Edit `src/styles.css` for palette changes
- **Charts**: Update medical statistics in `home.component.ts`
- **Icons**: Use Phosphor Icons via CDN or update icon classes in components
- **Text Slider**: Customize running text in `text-slider` component

## Accessibility & Responsiveness
- All components are designed for accessibility (WCAG AA contrast)
- Responsive layouts for desktop, tablet, and mobile
- Keyboard and screen reader friendly forms

## Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push to your branch and open a pull request

## License
This project is licensed under the MIT License.

## Contact
For questions or support, please contact the MediSense AI team via the repository issues page.
