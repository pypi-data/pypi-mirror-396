import { SORTING_TYPES } from '@routes/constants';


/**
 * Performs a stable sort on an array using the provided comparator function.
 * Stable sort maintains the relative order of items with equal keys.
 *
 * @param {Array} array - The array to be sorted.
 * @param {Function} comparator - The comparator function used to determine the order of elements.
 * @returns {Array} The sorted array.
 */
export const stableSort = (array, comparator) => (
  array
    .map((el, index) => ({ el, index }))
    .sort((a, b) => {
      const order = comparator(a.el, b.el);
      return order !== 0 ? order : a.index - b.index;
    })
    .map(({ el }) => el)
);

/**
 * Comparator function for sorting in descending order based on a specific property.
 *
 * @param {Object} a - The first object to compare.
 * @param {Object} b - The second object to compare.
 * @param {string} orderBy - The property name to sort by.
 * @returns {number} -1 if `a[orderBy]` should come after `b[orderBy]`, 1 if it should come before, 0 if they are equal.
 */
export const descendingComparator = (a, b, orderBy) => {
  if (b[orderBy] < a[orderBy]) {
    return -1;
  }
  if (b[orderBy] > a[orderBy]) {
    return 1;
  }
  return 0;
};

/**
 * Returns a comparator function based on the specified order and property.
 *
 * @param {string} order - The order direction, can be either "asc" or "desc".
 * @param {string} orderBy - The property name to sort by.
 * @returns {Function} A comparator function that can be used to sort an array.
 */
export const getComparator = (order, orderBy) => (
  order === SORTING_TYPES.desc
    ? (a, b) => descendingComparator(a, b, orderBy)
    : (a, b) => -descendingComparator(a, b, orderBy)
);

