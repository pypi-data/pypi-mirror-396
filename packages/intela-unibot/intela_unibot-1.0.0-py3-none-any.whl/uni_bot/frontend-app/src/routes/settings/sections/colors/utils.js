import {
  DEFAULT_BACKGROUND_COLOR,
  DEFAULT_ACCENT_COLOR,
  DEFAULT_TEXT_COLOR,
  PICKERS,
} from '@context/widget';

/**
 * Retrieves the color value from the provided picker.
 * If the color is not found, it returns the default color '#fff'.
 *
 * @param {string} picker - The name of the color picker.
 * @param {object} colors - An object containing color values.
 * @returns {string} The color value associated with the picker.
 */
// eslint-disable-next-line import/prefer-default-export
export const getColor = (picker, colors) => {
  switch (picker) {
    case PICKERS.BACKGROUND:
      return colors[PICKERS.BACKGROUND] || DEFAULT_BACKGROUND_COLOR;
    case PICKERS.ACCENT:
      return colors[PICKERS.ACCENT] || DEFAULT_ACCENT_COLOR;
    case PICKERS.TEXT:
      return colors[PICKERS.TEXT] || DEFAULT_TEXT_COLOR;
    default:
      return DEFAULT_BACKGROUND_COLOR;
  }
};
