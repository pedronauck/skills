# Responsive Design Essentials

Mobile-first approach: start with mobile, progressively enhance for larger screens.

## Breakpoints

| Range | Pixels | Devices | Strategy |
|-------|--------|---------|----------|
| **XS** | 0-479px | Small phones | Single column, stacked nav, 44px touch targets |
| **SM** | 480-767px | Large phones | Single column, bottom nav, simplified UI |
| **MD** | 768-1023px | Tablets | 2 columns possible, sidebar nav |
| **LG** | 1024-1439px | Laptops | Multi-column, full nav, desktop UI |
| **XL** | 1440px+ | Desktop | Max-width containers, multi-panel layouts |

## Tailwind Responsive

```tsx
// Mobile-first: base styles, then scale up
<div className="
  w-full          // mobile: full width
  sm:w-1/2        // 480px+: half
  md:w-1/3        // 768px+: third
  lg:w-1/4        // 1024px+: quarter
">

// Responsive grid
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">

// Responsive typography
<h1 className="text-3xl md:text-4xl lg:text-5xl">

// Show/hide by breakpoint
<div className="block md:hidden">Mobile only</div>
<div className="hidden md:block">Desktop only</div>
```

## Fluid Typography

```css
h1 { font-size: clamp(2rem, 5vw, 4rem); }
p { font-size: clamp(1rem, 2.5vw, 1.25rem); }
```

## Touch Targets

- Minimum **44x44px** for all interactive elements
- Use `touch-manipulation` to prevent 300ms tap delay
- Adequate spacing between targets

```tsx
<button className="min-w-[44px] min-h-[44px] touch-manipulation">
```

## Mobile Simplification

| Desktop | Mobile |
|---------|--------|
| Full nav bar | Hamburger menu |
| Side-by-side fields | Stacked fields |
| Multi-column grid | Single column |
| Inline buttons | Fixed bottom bar |
| Data table | Collapsed cards |
| Visible sidebar | Hidden/collapsible |

## Images

```tsx
// Responsive images
<img
  srcSet="image-400w.jpg 400w, image-800w.jpg 800w, image-1200w.jpg 1200w"
  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
  loading="lazy"
/>

// Next.js
<Image src="/hero.jpg" width={1200} height={600} priority className="w-full h-auto" />
```

## Testing

Test at these widths:
- 375px (iPhone SE)
- 390px (iPhone 14)
- 768px (iPad)
- 1024px (iPad Pro)
- 1280px+ (Desktop)

## Resources

- [Tailwind Responsive](https://tailwindcss.com/docs/responsive-design)
