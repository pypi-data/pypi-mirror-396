import axios from 'axios';

import { apiSlice } from './apiSlice';
import { convertKeysToCamelCase } from '../utils';
import { createAbortController } from './utils';
import { POLLING_INTERVAL } from './constants';


const fetchCourseContent = async (courseId, options = {}) => {
  const response = await axios.get(`/uni_bot/api/course_context/${courseId}/`, {
    signal: options.signal,
  });
  return convertKeysToCamelCase(response.data);
};

export const courseAbortController = createAbortController('courseContentPolling');

const pollUntilComplete = async (api, dispatch, courseId, resolve, reject, abortController = courseAbortController) => {
  try {
    const data = await fetchCourseContent(courseId, { signal: abortController.signal });

    dispatch(api.util.updateQueryData('fetchCourseContent', courseId, (draft) => {
      if (JSON.stringify(draft) !== JSON.stringify(data)) {
        Object.assign(draft, data);
      }
    }));

    if (data.progress === 1) {
      resolve({ data });
    } else {
      setTimeout(() => pollUntilComplete(api, dispatch, courseId, resolve, reject, abortController), POLLING_INTERVAL);
    }
  } catch (error) {
    if (error.name === 'AbortError') {
      // eslint-disable-next-line no-console
      console.error('Polling aborted');
    } else {
      reject(error);
    }
  }
};

export const courseContentApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    fetchCourseContent: builder.query({
      query: (courseId) => `/course_context/${courseId}/`,
      providesTags: (result) => (
        result
          ? [...result.contexts.map(({ sectionId }) => ({ type: 'CourseContent', id: sectionId })), 'CourseContent']
          : ['CourseContent']
      ),
    }),
    updateCourseContent: builder.mutation({
      query: (courseId) => ({
        url: `/course_context/${courseId}/`,
        method: 'POST',
        body: {},
      }),
      async onQueryStarted(courseId, { dispatch, queryFulfilled }) {
        try {
          const { data: newData } = await queryFulfilled;
          dispatch(
            courseContentApi.util.updateQueryData('fetchCourseContent', courseId, (draft) => {
              Object.assign(draft, newData);
            }),
          );
        } catch (err) {
          // eslint-disable-next-line no-console
          console.error('Error while updating cache:', err);
        }
      },
      invalidatesTags: ['BotStatuses'],
    }),
    updateCourseSection: builder.mutation({
      query: ({ sectionId, isActive, courseId }) => ({
        url: `/course_context/${courseId}/${sectionId}/`,
        method: 'PUT',
        body: { is_active: isActive },
      }),
      async onQueryStarted(newData, { dispatch, queryFulfilled }) {
        const patchResult = dispatch(
          courseContentApi.util.updateQueryData('fetchCourseContent', newData.courseId, (draft) => {
            const context = draft.contexts.find(section => section.sectionId === newData.sectionId);
            if (context) {
              context.status = newData.isActive ? 'Active' : 'Disabled';
            }
          }),
        );

        try {
          await queryFulfilled;
        } catch (err) {
          patchResult.undo();
        }
      },
    }),
    dynamicPingCourseContent: builder.mutation({
      queryFn: async ({ courseId }, { dispatch }) => {
        const dynamicPingAbortController = createAbortController('dynamicPingCourseContent');
        return new Promise((resolve, reject) => {
          pollUntilComplete(courseContentApi, dispatch, courseId, resolve, reject, dynamicPingAbortController);
        });
      },
      async onQueryStarted(data, { queryFulfilled, abort }) {
        try {
          await queryFulfilled;
        } catch (err) {
          // eslint-disable-next-line no-console
          console.error('Polling failed', err);
        }
        return () => {
          abort();
        };
      },
      invalidatesTags: ['BotStatuses'],
    }),
  }),
  overrideExisting: false,
});

export const {
  useFetchCourseContentQuery,
  useUpdateCourseContentMutation,
  useUpdateCourseSectionMutation,
  useDynamicPingCourseContentMutation,
} = courseContentApi;
