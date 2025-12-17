export const DEFAULT_TEXT_COLOR = '474848';
export const DEFAULT_BACKGROUND_COLOR = 'f7fafb';
export const DEFAULT_ACCENT_COLOR = '4040f2';

export const PICKERS = {
  BACKGROUND: 'bgColor',
  ACCENT: 'accentColor',
  TEXT: 'textColor',
};

export const defaultParams = {
  widget: {
    name: '',
    description: '',
    greetingString: '',
    feedbackString: '',
    width: '',
    height: '',
    [PICKERS.BACKGROUND]: '',
    [PICKERS.ACCENT]: '',
    [PICKERS.TEXT]: '',
  },
  languages: {
    selected: [],
    available: [
      {
        value: 'en',
        label: 'English',
      },
    ],
  },
};
