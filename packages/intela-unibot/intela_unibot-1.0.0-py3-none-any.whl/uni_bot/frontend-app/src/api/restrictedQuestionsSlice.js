import { apiSlice } from './apiSlice';


export const restrictedQuestionsApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    fetchRestrictedQuestions: builder.query({
      query: (courseId) => `/restricted_question/${courseId}/`,
      providesTags: (result) => (
        result ? result.questions.flatMap(
          ({ restrictedQuestions }) => restrictedQuestions.map(
            (question) => ({ type: 'RestrictedQuestions', id: question.uuid }),
          ),
        ) : ['RestrictedQuestions']
      ),
    }),
    updateRestrictedQuestionItem: builder.mutation({
      query: ({
        questionId, isActive, courseId, hint,
      }) => ({
        url: `/restricted_question/${courseId}/${questionId}/`,
        method: 'PUT',
        body: { is_active: isActive, hint },
      }),
      async onQueryStarted(newData, { dispatch, queryFulfilled }) {
        const patchResult = dispatch(
          restrictedQuestionsApi.util.updateQueryData('fetchRestrictedQuestions', newData.courseId, (draft) => {
            const context = draft.questions
              .flatMap(({ restrictedQuestions }) => restrictedQuestions)
              .find(question => question.uuid === newData.questionId);
            if (context) {
              context.status = newData.isActive ? 'Active' : 'Disabled';
              context.hint = newData.hint;
            }
          }),
        );

        try {
          await queryFulfilled;
        } catch (err) {
          patchResult.undo();
          // eslint-disable-next-line no-console
          console.error('Error while updating restricted question item:', err);
        }
      },
    }),
    restrictQuestions: builder.mutation({
      query: ({ courseId, restrictGraded, restrictNonGraded }) => ({
        url: `/restricted_question/${courseId}/restrict/`,
        method: 'POST',
        body: { restrict_graded: restrictGraded, restrict_non_graded: restrictNonGraded },
      }),
      invalidatesTags: ['RestrictedQuestions'],
    }),
  }),
  overrideExisting: false,
});

export const {
  useFetchRestrictedQuestionsQuery,
  useUpdateRestrictedQuestionItemMutation,
  useRestrictQuestionsMutation,
} = restrictedQuestionsApi;
