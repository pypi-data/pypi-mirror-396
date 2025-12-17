import axios from 'axios';

import { convertKeysToCamelCase } from '../utils';
import { apiSlice } from './apiSlice';
import { POLLING_INTERVAL } from './constants';
import { createAbortController } from './utils';


const fetchAdditionalContent = async (courseId, options = {}) => {
  const response = await axios.get(`/uni_bot/api/additional_content/${courseId}/`, {
    signal: options.signal,
  });
  return convertKeysToCamelCase(response.data);
};

const contentAbortController = createAbortController('additionalContentPolling');

const pollUntilComplete = async (
  api,
  dispatch,
  courseId,
  resolve,
  reject,
  abortController = contentAbortController,
) => {
  try {
    const data = await fetchAdditionalContent(courseId, { signal: abortController.signal });

    dispatch(api.util.updateQueryData('fetchAdditionalContent', courseId, (draft) => {
      if (JSON.stringify(draft) !== JSON.stringify(data)) {
        Object.assign(draft, data);
      }
    }));

    if (data.progress === 1 || !data.contexts.length) {
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
    fetchAdditionalContent: builder.query({
      query: (courseId) => `/additional_content/${courseId}/`,
      providesTags: (result) => (
        result
          ? [...result.contexts.map(({ sectionId }) => ({ type: 'AdditionalContent', id: sectionId })), 'AdditionalContent']
          : ['AdditionalContent']
      ),
    }),
    deleteSection: builder.mutation({
      query: ({ courseId, uuid }) => ({
        url: `/additional_content/${courseId}/${uuid}/`,
        method: 'DELETE',
      }),
      async onQueryStarted(newData, { dispatch, queryFulfilled }) {
        const patchResult = dispatch(
          courseContentApi.util.updateQueryData('fetchAdditionalContent', newData.courseId, (draft) => {
            const context = draft.contexts.filter(section => section.uuid !== newData.uuid);
            if (context) {
              Object.assign(draft, context);
            }
          }),
        );

        try {
          await queryFulfilled;
        } catch (err) {
          patchResult.undo();
        }
      },
      invalidatesTags: ['AdditionalContent'],
    }),
    dynamicPingAdditionalContent: builder.mutation({
      queryFn: async ({ courseId }, { dispatch }) => {
        const dynamicPingAbortController = createAbortController('dynamicPingAdditionalContent');
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
      invalidatesTags: ['AdditionalContent'],
    }),
  }),
  overrideExisting: false,
});

export const {
  useFetchAdditionalContentQuery,
  useDeleteSectionMutation,
  useDynamicPingAdditionalContentMutation,
} = courseContentApi;
