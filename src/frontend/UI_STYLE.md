# Dazza UI Style Guide

> Elegant Dark Interface Design System for AI-powered Deepfake Detection

---

## Design Philosophy

Dazza follows the **Elegant Dark Interface** design language—a premium, research-grade aesthetic that prioritizes clarity, depth, and professional polish. The UI evokes a sense of cutting-edge technology while maintaining exceptional readability and usability.

### Core Principles

1. **Depth & Dimension** — Glass-morphism panels with subtle transparency and blur create visual hierarchy
2. **Restrained Elegance** — Minimal color palette with strategic accent usage
3. **Micro-interactions** — Smooth, purposeful animations that feel natural
4. **Accessibility First** — High contrast ratios and keyboard navigation support
5. **Space Ambience** — Subtle cosmic background that adds atmosphere without distraction

---

## Color Palette

### Void (Background) Scale
| Token | Hex | Usage |
|-------|-----|-------|
| `void-950` | `#030305` | Primary background |
| `void-900` | `#07080c` | Elevated surfaces |
| `void-850` | `#0a0c12` | Card backgrounds |
| `void-800` | `#0e1018` | Input backgrounds |
| `void-700` | `#14161f` | Borders, dividers |

### Surface (Glass Panels)
| Token | Value | Usage |
|-------|-------|-------|
| `surface-900` | `rgba(14, 16, 24, 0.85)` | Primary panels |
| `surface-800` | `rgba(20, 22, 31, 0.75)` | Secondary panels |
| `surface-700` | `rgba(30, 33, 45, 0.65)` | Tertiary/hover states |

### Accent Colors
| Token | Hex | Usage |
|-------|-----|-------|
| `accent-violet` | `#8b5cf6` | Primary accent, CTAs |
| `accent-indigo` | `#6366f1` | Gradient endpoints |
| `accent-purple` | `#a855f7` | Hover states |
| `accent-glow` | `rgba(139, 92, 246, 0.15)` | Glow effects |

### Semantic Colors
| State | Color | Usage |
|-------|-------|-------|
| Real/Safe | `#22c55e` → `#4ade80` | Positive detection result |
| Deepfake/Alert | `#ef4444` → `#f87171` | Negative detection result |
| Error | `#ef4444` | Error messages |

### Neutral Scale
Used for text, borders, and subtle UI elements:
- **50-100**: Primary text
- **200-300**: Secondary text
- **400-500**: Tertiary/placeholder text
- **600**: Disabled text, subtle borders

---

## Typography

### Font Stack
```css
--font-sans: "Inter", "SF Pro Display", system-ui, -apple-system, sans-serif;
--font-mono: "JetBrains Mono", "SF Mono", Consolas, monospace;
```

### Type Scale
| Size | Class | Usage |
|------|-------|-------|
| 40-50px | `text-4xl`/`text-5xl` | Hero titles |
| 24px | `text-2xl` | Section headings |
| 18-20px | `text-lg`/`text-xl` | Card titles, large values |
| 16px | `text-base` | Body text |
| 14px | `text-sm` | Secondary text, labels |
| 12px | `text-xs` | Captions, metadata |
| 10px | `text-2xs` | Micro labels, stat labels |

### Font Weights
- **300**: Light (sparingly used)
- **400**: Regular body text
- **500**: Medium emphasis
- **600**: Semibold headings
- **700**: Bold for maximum emphasis

---

## Spacing System

Based on 4px base unit with emphasis on 16/24/32px rhythm:

| Token | Value | Usage |
|-------|-------|-------|
| `p-4` | 16px | Compact card padding |
| `p-6` | 24px | Standard panel padding |
| `p-8` | 32px | Generous panel padding |
| `gap-3` | 12px | Tight element spacing |
| `gap-4` | 16px | Standard element spacing |
| `gap-6` | 24px | Section spacing |
| `mb-10` | 40px | Large section margins |
| `mb-14` | 56px | Hero/header margins |

---

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `rounded-lg` | 8px | Small elements, badges |
| `rounded-xl` | 12px | Buttons, inputs, stat cards |
| `rounded-2xl` | 16px | Primary panels |
| `rounded-3xl` | 24px | Hero elements |
| `rounded-full` | 9999px | Pills, avatars |

---

## Components

### Glass Panel
```css
.glass-panel {
  background: linear-gradient(135deg, rgba(14,16,24,0.9), rgba(20,22,31,0.8));
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 1rem;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
```

### Primary Button
```css
.btn-primary {
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  box-shadow: 0 4px 16px rgba(139,92,246,0.25);
  transition: transform 0.3s, box-shadow 0.3s;
}
.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(139,92,246,0.35);
}
```

### Stat Card
```css
.stat-card {
  background: rgba(20, 22, 31, 0.5);
  border: 1px solid rgba(255,255,255,0.04);
  border-radius: 0.75rem;
  padding: 1rem;
}
```

### Badge
```css
.badge-real {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
  border: 1px solid rgba(34, 197, 94, 0.2);
}
.badge-deepfake {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.2);
}
```

---

## Animation Guidelines

### Timing Functions
- **ease-out**: Entry animations, reveals
- **ease-in-out**: Hover states, continuous animations
- **linear**: Loading spinners

### Duration
| Type | Duration |
|------|----------|
| Micro (hover) | 200-300ms |
| Standard | 400ms |
| Entrance | 500ms |
| Background | 4-8s |

### Animation Classes
```css
.animate-in     /* Slide up + fade in */
.delay-100      /* 100ms delay */
.delay-200      /* 200ms delay */
.delay-300      /* 300ms delay */
```

---

## Accessibility

### Color Contrast
- All text maintains **WCAG AA** minimum (4.5:1 for body, 3:1 for large text)
- Critical UI elements have **WCAG AAA** contrast where possible

### Focus States
```css
.focus-ring:focus-visible {
  outline: none;
  ring: 2px solid rgba(139,92,246,0.5);
  ring-offset: 2px;
  ring-offset-color: #030305;
}
```

### Keyboard Navigation
- All interactive elements are focusable
- Tab order follows visual hierarchy
- Focus visible states on all buttons/inputs

---

## Extending the Design System

### Adding New Components

1. **Use existing color tokens** — Never hardcode colors
2. **Follow spacing rhythm** — Stick to 4/8/12/16/24/32px
3. **Apply glass morphism** — Use `.glass-panel` for elevated surfaces
4. **Add micro-interactions** — Subtle hover lifts (`translateY(-2px)`)
5. **Maintain accessibility** — Test with keyboard, check contrast

### Example: New Feature Card
```jsx
<div className="glass-panel p-6 glow-effect animate-in">
  <h3 className="text-lg font-semibold text-neutral-100 mb-4">
    Feature Title
  </h3>
  <p className="text-sm text-neutral-400">
    Feature description with proper hierarchy.
  </p>
</div>
```

---

## File Structure

```
src/frontend/
├── src/
│   ├── index.css      # Tailwind + custom Dazza styles
│   ├── App.jsx        # Main application component
│   └── main.jsx       # React entry point
├── tailwind.config.cjs # Extended Tailwind configuration
├── index.html         # HTML template with meta tags
└── UI_STYLE.md        # This documentation
```

---

## Credits

Design inspired by the "Elegant Dark Interfaces" aesthetic — premium dark-themed product dashboards with glass morphism, subtle gradients, and refined typography.

Built with:
- [React](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [Vite](https://vitejs.dev)
- [Inter Font](https://rsms.me/inter/)
