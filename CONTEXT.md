# NAWI Design System Reference

## Overview
This document defines the Neubrutalism design system for the NAWI project.
It serves as the single source of truth for design tokens, components, and rules.

## Design Tokens (CSS Variables)
- `--bg`: `#F5F5EF` (Background color)
- `--surface`: `#FFFFFF` (Surface / Card background)
- `--text`: `#0D0D0D` (Primary text color)
- `--border`: `#000000` (Universal border color)
- `--accent`: `#EEFF00` (Primary accent / button background)
- `--accent-hover`: `#B5FF4D` (Primary accent hover state)
- `--pass`: `#00E676` (Success / Pass background)
- `--fail`: `#FF1744` (Danger / Fail background)
- `--disabled`: `#D9D9D9` (Disabled state background)
- `--header-bg`: `#0D0D0D` (Header background)
- `--shadow`: `4px 4px 0px #000000` (Default shadow offset)
- `--shadow-hover`: `6px 6px 0px #000000` (Hover shadow offset)
- `--border-width`: `2.5px` (Universal border width)
- `--font`: `'Space Grotesk', sans-serif` (Universal font family)

## Typography
- H1-H6: Bold (700)
- Body: Medium (500)
- `Space Grotesk` is strictly used across all elements.

## Component Classes
- **Buttons**: `.btn`, `.btn-primary`, `.btn-dark`, `.btn-ghost`, `.btn-full`, `.btn-disabled`
- **Cards**: `.card`, `.card-locked`, `.card-accent-top`
- **Forms**: `.input-field`, `.select-field`, `.textarea-field`, `.field-label`
- **Typography/Structure**: `.section-header`, `.result-panel`, `.result-value`
- **Layout**: `.grid-2`, `.grid-3`, `.stack`, `.container`, `.table-container`
- **Badges**: `.badge`, `.badge-pass`, `.badge-fail`, `.badge-warn`
- **Alerts**: `.alert`, `.alert-success`, `.alert-danger`

## Strict Rules
1. **Zero Border Radius**: `border-radius: 0` is strictly enforced for all UI elements (buttons, inputs, cards, dialogs, etc.).
2. **Shadows**: Only hard, offset box-shadows are permitted (`X Y 0px #000000`). No blur or spread.
3. **Button Hover Effects**: Translate elements diagonally (`transform: translate(-2px, -2px)`) and increase shadow size. Active state pushes elements back (`transform: translate(4px, 4px)`) and drops shadow to `0px`.
4. **Input Focus**: Inputs must turn `#FAFFA0` (pale yellow) on focus, while maintaining their thick black border and acquiring the default box-shadow.
