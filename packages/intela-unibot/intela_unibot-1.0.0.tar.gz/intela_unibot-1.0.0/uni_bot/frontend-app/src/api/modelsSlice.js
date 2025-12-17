import { apiSlice } from './apiSlice';
import { buildModelsList } from './utils';


export const modelsApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    fetchModels: builder.query({
      query: (courseId) => `/models/${courseId}`,
      transformResponse: (response) => Object.keys(response)
        .map((modelGroup) => ({
          modelName: modelGroup,
          models: modelGroup === 'selected'
            ? [buildModelsList(response[modelGroup][0], 0)]
            : response[modelGroup].map((model, index) => buildModelsList(model, index)),
        })),
      providesTags: ['Models'],
    }),
    fetchModel: builder.query({
      query: ({ courseId, modelId }) => `/models/${courseId}/${modelId}/`,
    }),
    updateSelectedModel: builder.mutation({
      query: ({ courseId, id, body }) => ({
        url: `/models/${courseId}/${id}/`,
        method: 'PUT',
        body,
      }),
      invalidatesTags: (result) => [
        ...(result ? ['Models'] : []),
        ...(result?.enableLongpolling ? ['AdditionalContent', 'CourseContent'] : []),
      ],
    }),
  }),
  overrideExisting: false,
});

export const {
  useFetchModelsQuery,
  useFetchModelQuery,
  useUpdateSelectedModelMutation,
} = modelsApi;
