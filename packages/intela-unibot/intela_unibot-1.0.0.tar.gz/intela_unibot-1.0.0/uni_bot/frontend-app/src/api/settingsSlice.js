import axios from 'axios';

import { createHeaders, abortAllRequests } from '@api/utils';
import { apiSlice } from './apiSlice';


export const taSettingsApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    fetchWidgetSettings: builder.query({
      query: (courseId) => `/ta_settings/${courseId}`,
      providesTags: ['WidgetSettings'],
    }),
    saveWidgetSettings: builder.mutation({
      query: (data) => ({
        url: `/ta_settings/${data.courseId}/`,
        method: 'POST',
        body: {
          widget: {
            name: data.widget.name || '',
            description: data.widget.description || '',
            greeting_string: data.widget.greetingString || '',
            feedback_string: data.widget.feedbackString || '',
            width: `${data.widget.width}` || '',
            height: `${data.widget.height}` || '',
            bg_color: data.widget.bgColor || '',
            accent_color: data.widget.accentColor || '',
            text_color: data.widget.textColor || '',
            avatar: data.widget.avatar || '',
            tab_name: data.widget.tab_name || '',
          },
          languages: data.languages || [{
            value: 'gb',
            label: 'English',
          }],
        },
      }),
      invalidatesTags: ['WidgetSettings'],
    }),
    uploadAvatar: builder.mutation({
      queryFn: async ({ formData, csrfToken, courseId }) => {
        try {
          const response = await axios.post(
            `/uni_bot/api/ta_settings/${courseId}/avatar/`,
            formData,
            { headers: createHeaders(csrfToken) },
          );
          return { data: response.data };
        } catch (error) {
          return {
            error: {
              status: error.response?.status,
              data: error.response?.data || 'Failed to upload avatar',
            },
          };
        }
      },
      invalidatesTags: ['WidgetSettings'],
    }),
    resetSettings: builder.mutation({
      query: (courseId) => ({
        url: `/course_widget_control/${courseId}/reset_widget/`,
        method: 'POST',
        body: {},
      }),
      invalidatesTags: ['WidgetSettings', 'CourseContent', 'RestrictedQuestions', 'AdditionalContent', 'BotStatuses', 'Models'],
      async onQueryStarted(_, { queryFulfilled }) {
        try {
          await queryFulfilled;
          abortAllRequests();
        } catch (err) {
          // eslint-disable-next-line no-console
          console.error('Failed to reset settings:', err);
        }
      },
    }),
  }),
  overrideExisting: false,
});

export const {
  useFetchWidgetSettingsQuery,
  useSaveWidgetSettingsMutation,
  useUploadAvatarMutation,
  useResetSettingsMutation,
} = taSettingsApi;
