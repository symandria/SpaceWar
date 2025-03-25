# SpaceWar Style Guide

## Design Vision
SpaceWar's visual design draws inspiration from classic sci-fi aesthetics, featuring a futuristic, high-tech interface dominated by glowing blue elements and sleek, cyber-inspired components. The design emphasizes immersion while maintaining clarity and usability.

## Color Palette

### Primary Colors
- **Deep Space Background** (`#0A0F1E`) - Main game background
- **Electric Blue** (`#0077FF`) - Primary UI elements, ship highlights
- **Cyan Glow** (`#00FFFF`) - Energy effects, weapon fire, shields
- **Dark Navy** (`#162137`) - Secondary UI backgrounds

### Secondary Colors
- **Interface Text** (`#E0E0E0`) - Primary text color
- **Accent Blue** (`#4D9FFF`) - Borders, highlights
- **Disabled State** (`rgba(224, 224, 224, 0.5)`) - Inactive elements

### Gradients
```css
/* Primary Button Gradient */
background: linear-gradient(to right, #0077FF, #00FFFF);

/* Header Text Gradient */
background: linear-gradient(to right, #0077FF, #4D9FFF);

/* UI Panel Background */
background: rgba(22, 33, 55, 0.6); /* #162137 with 60% opacity */
```

## Typography

### Font Family
- Primary Font: Orbitron
  - Used for headers, ship names, and important UI elements
  - Conveys a futuristic, technological feel
- Secondary Font: Arial
  - Used for body text and detailed information
  - Ensures readability at smaller sizes

### Font Sizes
- Large Headers: 32px
- Section Headers: 24px
- Button Text: 18px
- Body Text: 16px
- Small Text: 14px

### Text Effects
- Headers use gradient text effects for emphasis
- Important elements have a subtle glow effect
- Menu items have hover states with increased glow

## UI Components

### Extracted Components

#### GlowingButton
A button with a gradient background and interactive glow effects.
```css
Colors:
- Base Gradient: #0077FF to #00FFFF
- Border: #4D9FFF (30% opacity)
- Text: #E0E0E0
```
**Potential Uses:**
- Main menu navigation buttons
- Action buttons in battle (Fire, Move, etc.)
- Confirmation buttons in dialogs
- Ship ability activation buttons

#### GlassPanel
A semi-transparent panel with glowing borders.
```css
Colors:
- Background: #162137 (60% opacity)
- Border: #4D9FFF (30% opacity)
- Glow: #0077FF (10% opacity)
```
**Potential Uses:**
- Ship status displays
- Weapon selection panels
- Battle statistics overlays
- Menu backgrounds
- Information panels during gameplay

#### GradientDivider
A horizontal line with gradient fade effect.
```css
Colors:
- Line: #4D9FFF (30% opacity to transparent)
```
**Potential Uses:**
- Separating different sections in menus
- Dividing ship statistics
- Breaking up long lists of items
- Visual breaks between different control groups

#### LoadingSpinner
Three rotating rings with different speeds and directions.
```css
Colors:
- Rings: #4D9FFF
Speeds:
- Outer Ring: 3.0 (2.0s per rotation)
- Middle Ring: -3.75 (1.6s per rotation)
- Inner Ring: 2.5 (2.4s per rotation)
```
**Potential Uses:**
- Loading screens
- Battle transition animations
- Ship scanning effects
- Shield recharge indicators
- Weapon charging animations

#### Modal
A centered dialog with fade effects and semi-transparent overlay.
```css
Colors:
- Overlay: Black (50% opacity)
- Content: Uses GlassPanel
```
**Potential Uses:**
- Battle results display
- Ship customization interface
- Settings menus
- Confirmation dialogs
- Tutorial popups

### Component Adaptation for SpaceWar

While these components were extracted from a web interface, they need adaptation for our game:

1. **Battle HUD Elements**
   - Use GlassPanel for weapon/shield status
   - GradientDivider to separate different ship systems
   - LoadingSpinner for cooldown indicators

2. **Ship Interface**
   - GlowingButtons for weapon activation
   - GlassPanel for ship statistics
   - GradientDivider between subsystems

3. **Menu System**
   - GlowingButtons for main options
   - Modal for settings and confirmations
   - GradientDivider for menu sections

4. **Loading Screens**
   - LoadingSpinner as primary indicator
   - GlassPanel for progress information
   - GradientDivider for visual interest

### Implementation Guidelines

1. **Performance Considerations**
   - Cache textures rather than recreating them
   - Use sprite batching for UI elements
   - Limit number of simultaneous effects

2. **Accessibility**
   - Ensure sufficient contrast with background
   - Make interactive elements obvious
   - Consider colorblind-friendly alternatives

3. **Consistency**
   - Use standard colors across all components
   - Maintain consistent animation speeds
   - Keep padding and margins uniform

## Animation Guidelines

### Transitions
- Button hover: 300ms ease-in-out
- Panel fade: 200ms ease
- Menu transitions: 300ms ease
- Ship movements: Variable based on action type

### Effects
- Energy weapons: Bright cyan glow with particle effects
- Shields: Translucent blue bubble with ripple effect
- Explosions: Orange/red with blue particle dispersion
- UI Feedback: Subtle glows and pulses in primary colors

## Game-Specific Elements

### Ships
- Detailed models with blue energy highlights
- Shield effects using cyan gradient overlays
- Weapon systems with appropriate glow effects
- Damage states shown through texture and lighting changes

### Battle Effects
- Weapon fire: Electric blue to cyan trails
- Shield impacts: Rippling energy effects
- Explosions: Multi-stage with particle systems
- Movement trails: Subtle blue energy trails

### HUD Elements
- Ship status displays with gradient borders
- Energy/shield bars with glowing effects
- Targeting systems with holographic overlays
- Minimalist design with essential information only

## Accessibility

### Contrast
- Maintain minimum 4.5:1 contrast ratio for text
- Use glow effects to enhance visibility
- Provide high-contrast alternatives for important elements

### Visual Feedback
- Clear hover and selection states
- Distinct visual feedback for actions
- Multiple indicators for important events (color + animation)

## Implementation Notes

### MonoGame Specific
- Use `SpriteBatch` for efficient rendering
- Implement particle system for effects
- Use shader effects for gradients and glows
- Cache frequently used textures and effects

### Performance
- Optimize particle effects
- Use sprite atlases for UI elements
- Implement object pooling for effects
- Limit simultaneous animations

### Asset Creation
- Create assets at 2x resolution for HD displays
- Use vector sources when possible
- Maintain consistent light source in UI elements
- Export sprites with appropriate padding for glow effects 