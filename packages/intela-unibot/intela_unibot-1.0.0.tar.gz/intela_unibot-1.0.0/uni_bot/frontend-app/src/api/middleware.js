import { fetchBaseQuery } from '@reduxjs/toolkit/query/react';

import { convertKeysToCamelCase, convertKeysToSnakeCase } from '../utils';
import { API_BASE_URL } from './constants';
import { getCsrfToken } from './utils';


const baseQuery = fetchBaseQuery({
  baseUrl: API_BASE_URL,
  prepareHeaders: (headers) => {
    const csrfToken = getCsrfToken();
    if (csrfToken) {
      headers.set('X-CSRFToken', csrfToken);
    }
    return headers;
  },
});

/**
 * Base query function with CSRF token and data transformation.
 *
 * @param {object} args - The arguments for the query.
 * @param {object} api - The API object provided by Redux Toolkit Query.
 * @param {object} extraOptions - Any extra options for the query.
 * @returns {Promise<object>} The result of the query.
 */
// eslint-disable-next-line import/prefer-default-export
export const baseQueryWithTransforms = async (args, api, extraOptions) => {
  if (args.body) {
    // eslint-disable-next-line no-param-reassign
    args.body = convertKeysToSnakeCase(args.body);
  }

  const result = await baseQuery(args, api, extraOptions);

  if (result.data) {
    result.data = convertKeysToCamelCase(result.data);
  }

  return result;
};
