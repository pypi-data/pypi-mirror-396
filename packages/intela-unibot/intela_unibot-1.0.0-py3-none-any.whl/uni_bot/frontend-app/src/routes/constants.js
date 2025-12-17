export const ROUTES = {
  introduction: 'introduction',
  settings: 'settings',
  availableModels: 'available-models',
  scanCourse: 'scan-course',
  restrictedQuestions: 'restricted-questions',
  additionalContent: 'additional-content',
  dashboard: 'dashboard',
};

export const ROUTER_ORDER = [
  ROUTES.introduction,
  ROUTES.settings,
  ROUTES.availableModels,
  ROUTES.scanCourse,
  ROUTES.restrictedQuestions,
  ROUTES.additionalContent,
  ROUTES.dashboard,
];

export const SORTING_TYPES = {
  asc: 'asc',
  desc: 'desc',
};

export const SCANNING_STATUSES = {
  active: 'Active',
  started: 'Started',
  disabled: 'Disabled',
};

export const BOT_STATUSES = {
  deactivated: 'deactivated',
  inTraining: 'in_training',
  active: 'active',
};
