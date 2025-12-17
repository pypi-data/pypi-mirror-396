import { createApi } from '@reduxjs/toolkit/query/react';

import { baseQueryWithTransforms } from './middleware';


// eslint-disable-next-line import/prefer-default-export
export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithTransforms,
  tagTypes: ['WidgetSettings', 'CourseContent', 'RestrictedQuestions', 'AdditionalContent', 'Models', 'BotStatuses'],
  endpoints: () => ({}),
});
