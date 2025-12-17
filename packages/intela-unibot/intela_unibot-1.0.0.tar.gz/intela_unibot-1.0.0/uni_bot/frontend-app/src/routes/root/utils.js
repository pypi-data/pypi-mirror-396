/**
 * Extracts the course ID from the given URL pathname.
 *
 * @param {string} pathname - The URL pathname from which to extract the course ID.
 * @returns {string|null} The extracted course ID if found, otherwise null.
 */
// eslint-disable-next-line import/prefer-default-export
export const getCourseIdFromPathname = (pathname) => {
  const match = pathname.match(/\/(course-v1:[^/]+)/);
  return match ? match[1] : null;
};
