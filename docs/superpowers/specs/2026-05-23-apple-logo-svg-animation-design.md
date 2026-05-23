# Apple Logo SVG Drawing Animation Design

## Goal
Create a standalone `apple-logo-animation.html` page that shows an Apple-style logo being gradually drawn with SVG line animation, then filled in.

## Scope
- One self-contained HTML file.
- Pure HTML, CSS, and inline SVG.
- No external libraries, images, fonts, or network requests.
- Use an original approximate Apple-style outline rather than embedding official logo artwork.

## User Experience
The page opens to a centered SVG on a clean light background. The apple body outline draws first, followed by the leaf. After the outline completes, a black fill fades in while the stroke softens. The animation loops so it remains useful as a visual demo.

## Implementation Design
The SVG will contain two primary paths:
- `body-path`: the apple body silhouette.
- `leaf-path`: the top leaf.

CSS keyframes will animate `stroke-dashoffset` from the full path length to zero. A second keyframe will fade in the fill after the drawing phase. The body and leaf use staggered animation delays so the drawing feels sequential.

The page layout will use flexbox to center the SVG in the viewport and CSS variables for sizing, colors, and timing. The SVG will be responsive with a `viewBox`, fixed maximum width, and scalable dimensions.

## Testing
Open `apple-logo-animation.html` in a browser and verify:
- The page loads without external assets.
- The apple body outline draws before the leaf.
- The fill fades in after the outline is complete.
- The animation loops smoothly.
- The SVG remains centered and responsive at different window sizes.
