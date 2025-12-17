/**
 * Retrieves the CSRF token from cookies.
 *
 * This function searches for a cookie named 'csrftoken' in the document's cookies,
 * and returns its value if found. If the cookie is not found, it returns null.
 *
 * @returns {string|null} The CSRF token if found, otherwise null.
 */
export function getCsrfToken() {
  const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
  return cookie ? cookie.split('=')[1] : null;
}

/**
 * Creates headers for a HTTP request, including the CSRF token and additional parameters.
 *
 * @param {string} csrfToken - The CSRF token to include in the headers.
 * @param {Object} params - Additional headers to include in the request.
 * @returns {Object} The headers object to be used in an HTTP request.
 */
export const createHeaders = (csrfToken, params) => ({
  Accept: 'application/json',
  'X-CSRFToken': csrfToken,
  ...params,
});

/**
 * Builds a list of model objects with specific properties.
 *
 * @param {Object} model - The model object containing the data to extract.
 * @param {number} index -  The index of the model in the list.
 * @returns {{
 * credentials: string,
 * name: string,
 * description: string,
 * id: string,
 * value: string,
 * mutable: boolean,
 * message: string | null,
 * configurationLevel: string,
 * }}
 * An object representing the model with properties.
 */
export const buildModelsList = (model, index) => ({
  id: index + 1,
  name: model.label,
  value: model.value,
  mutable: model?.mutable,
  message: model?.message,
  configurationLevel: model?.configurationLevel,
  description: model?.data?.description,
  credentials: model?.data?.credentials,
});

/**
 * A Map to store active AbortControllers by their unique keys.
 * @type {Map<string, AbortController>}
 */
const abortControllers = new Map();

/**
 * Creates a new AbortController, associates it with a given key,
 * and stores it in the controllers Map.
 *
 * @param {string} key - A unique identifier for the AbortController.
 * @returns {AbortController} - The created AbortController instance.
 */
export const createAbortController = (key) => {
  const controller = new AbortController();
  abortControllers.set(key, controller);
  return controller;
};

/**
 * Aborts all active requests by invoking the `abort` method
 * on every stored AbortController and clears the controllers Map.
 */
export const abortAllRequests = () => {
  abortControllers.forEach((controller) => controller.abort());
  abortControllers.clear();
};
