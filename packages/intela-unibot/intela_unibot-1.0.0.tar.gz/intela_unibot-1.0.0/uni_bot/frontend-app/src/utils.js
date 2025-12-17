/**
 * Capitalizes the first letter of a string and makes the rest of the string lowercase.
 *
 * @param {string} str - The string to capitalize.
 * @returns {string} The capitalized string, or the original input if it is not a string or is empty.
 */
export const capitalize = (str) => {
  if (typeof str !== 'string' || str.length === 0) {
    return str;
  }
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

/**
 * Converts a snake_case string to camelCase.
 * @param {string} snakeCaseString - The snake_case string to be converted.
 * @returns {string} - The converted camelCase string.
 */
function toCamelCase(snakeCaseString) {
  return snakeCaseString.replace(/_([a-z])/g, (match, letter) => letter.toUpperCase());
}

/**
 * Recursively converts all keys of an object or an array of objects from snake_case to camelCase.
 * @param {Object|Array} obj - The object or array of objects to be converted.
 * @returns {Object|Array} - The object or array of objects with camelCase keys.
 */
export function convertKeysToCamelCase(obj) {
  if (Array.isArray(obj)) {
    return obj.map(item => convertKeysToCamelCase(item));
  } if (obj !== null && typeof obj === 'object') {
    return Object.keys(obj).reduce((acc, key) => {
      const camelCaseKey = toCamelCase(key);
      acc[camelCaseKey] = convertKeysToCamelCase(obj[key]);
      return acc;
    }, {});
  }
  return obj;
}

/**
 * Converts a camelCase string to snake_case.
 *
 * @param {string} camelCaseString - The camelCase string to be converted.
 * @returns {string} The converted snake_case string.
 */
function toSnakeCase(camelCaseString) {
  return camelCaseString.replace(/([A-Z])/g, '_$1').toLowerCase();
}

/**
 * Recursively converts all keys in an object or array from camelCase to snake_case.
 *
 * @param {Object|Array} obj - The object or array to be converted.
 * @returns {Object|Array} The converted object or array with snake_case keys.
 */
export function convertKeysToSnakeCase(obj) {
  if (Array.isArray(obj)) {
    return obj.map(item => convertKeysToSnakeCase(item));
  }

  if (obj !== null && typeof obj === 'object') {
    return Object.keys(obj).reduce((acc, key) => {
      const snakeCaseKey = toSnakeCase(key);
      acc[snakeCaseKey] = convertKeysToSnakeCase(obj[key]);
      return acc;
    }, {});
  }
  return obj;
}

/**
 * Converts a string to kebab-case.
 *
 * @param {string} str - The string to be converted.
 * @returns {string} The converted snake_case string.
 */
export function toKebabCase(str) {
  return str.replace(/ /g, '-').toLowerCase();
}
