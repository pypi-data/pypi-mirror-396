import { apiSlice } from './apiSlice';


export const botStatusesApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    fetchBotStatuses: builder.query({
      query: (courseId) => `/bot_status/${courseId}/`,
      providesTags: ['BotStatuses'],
    }),
    updateBotStatuses: builder.mutation({
      query: ({ courseId, isDisabled }) => ({
        url: `/bot_status/${courseId}/`,
        method: 'PUT',
        body: { is_disabled: isDisabled },
      }),
      async onQueryStarted({ courseId }, { dispatch, queryFulfilled }) {
        try {
          const { data: newData } = await queryFulfilled;
          dispatch(
            botStatusesApi.util.updateQueryData('fetchBotStatuses', courseId, (draft) => {
              Object.assign(draft, newData);
            }),
          );
        } catch (err) {
          // eslint-disable-next-line no-console
          console.error('Error while updating cache:', err);
        }
      },
    }),
  }),
});

export const {
  useFetchBotStatusesQuery,
  useUpdateBotStatusesMutation,
} = botStatusesApi;
