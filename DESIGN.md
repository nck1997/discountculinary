# DICE — design rules

The site should feel like a home cook's fridge door and a student's notebook:
photos held up with blue painter's tape, names written on the tape in marker,
sticky notes for the things you'd actually scribble. The food photos and the
recipes are the point. Everything else stays quiet.

## Imagery
- Photos are the largest element on every recipe card and recipe page. (block)
- Every recipe photo is held by a strip of blue painter's tape carrying the recipe name. (warn)
- Do NOT use stock illustration, emoji icons, or decorative icon sets. (warn)

## Color
- One paper background, one ink color, painter's-tape blue as the only brand accent. (block)
- Sticky-note colors (yellow, pink, green, orange) are reserved for sticky notes and never used for buttons, links, or text. (warn)
- Do NOT use gradients on surfaces, buttons, or text. (block)
- Do NOT use glow, neon, or large colored blur shadows. (block)
- Text contrast meets WCAG AA everywhere, including on tape and sticky notes. (block) (raven:audit_contrast)

## Typography
- Marker handwriting is only for tape labels and page titles. (block)
- Pen handwriting is only for sticky notes and short margin notes. (block)
- Ingredients, steps, numbers, controls, and anything longer than two lines use the plain text face. (block)
- Do NOT set body copy below 16px. (warn)

## Layout
- Sticky notes and tape may tilt a few degrees; text blocks, controls, and data never tilt. (warn)
- Every sticky note carries real content: macros, cook's notes, a tip, a filter summary. No decorative notes. (block)
- Interactive targets are at least 44px on touch. (block) (raven:audit_tap_targets)
- Do NOT use glassmorphism, frosted panels, or pill-shaped everything. (warn)
- Corners are square or barely rounded, like paper. (nit)

## Motion
- Motion is limited to small paper-like responses (a note lifting on hover) and respects prefers-reduced-motion. (warn)

## Voice
- Plain, dry, first-person home cook. The Institute joke appears in small doses. (warn)
- Do NOT use hype words (unlock, elevate, seamless, supercharge, game-changing, effortless, revolutionize). (warn)
