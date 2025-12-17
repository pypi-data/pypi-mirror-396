/**
 * Converts a HEX color to RGBA format.
 *
 * @param {string} hex - The HEX color value (e.g., '#ff0000' or '#f00').
 * @param {number} alpha - The alpha value (opacity) ranging from 0 to 1.
 * @returns {string} The RGBA color value (e.g., 'rgba(255, 0, 0, 0.5)').
 */
export function hexToRgba(hex, alpha) {
  let r = 0; let g = 0; let b = 0;

  // Handle 3-digit HEX color format (e.g., '#f00')
  if (hex.length === 4) {
    r = parseInt(hex[1] + hex[1], 16);
    g = parseInt(hex[2] + hex[2], 16);
    b = parseInt(hex[3] + hex[3], 16);

    // Handle 6-digit HEX color format (e.g., '#ff0000')
  } else if (hex.length === 7) {
    r = parseInt(hex[1] + hex[2], 16);
    g = parseInt(hex[3] + hex[4], 16);
    b = parseInt(hex[5] + hex[6], 16);
  }

  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/**
 * Converts an RGB color to RGBA format by adding an alpha value.
 *
 * @param {string} rgb - The RGB color value (e.g., 'rgb(255, 0, 0)').
 * @param {number} alpha - The alpha value (opacity) ranging from 0 to 1.
 * @returns {string} The RGBA color value (e.g., 'rgba(255, 0, 0, 0.5)').
 */
export function rgbToRgba(rgb, alpha) {
  return rgb.replace('rgb', 'rgba').replace(')', `, ${alpha})`);
}

/**
 * Converts any valid color format (HEX, RGB, or named color) to RGBA format with an alpha value.
 *
 * @param {string} color - The color value in HEX, RGB, or named format (e.g., '#ff0000', 'rgb(255, 0, 0)', 'red').
 * @param {number} alpha - The alpha value (opacity) ranging from 0 to 1.
 * @returns {string} The RGBA color value (e.g., 'rgba(255, 0, 0, 0.5)').
 */
export function getRgbaColor(color, alpha) {
  if (color.startsWith('#')) {
    return hexToRgba(color, alpha);
  }
  if (color.startsWith('rgb')) {
    return rgbToRgba(color, alpha);
  }
  // For named colors, we need a conversion utility
  const tempElement = document.createElement('div');
  tempElement.style.color = color;
  document.body.appendChild(tempElement);
  const computedColor = getComputedStyle(tempElement).color;
  document.body.removeChild(tempElement);
  return rgbToRgba(computedColor, alpha);
}
