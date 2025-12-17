import { createTheme } from '@mui/material/styles';


const STYLE_CONSTANTS = {
  colors: {
    black10: 'rgba(28, 28, 28, 0.1)',
    black40: 'rgba(28, 28, 28, 0.4)',
    black80: 'rgba(28, 28, 28, 0.8)',
    primaryAccent: '#4040f2',
    primaryAccentHover: '#2C2ca9',
    primaryLight: '#f7fafb',
    primaryBlue: 'rgba(64, 64, 242, 0.05)',
    secondaryModalBlue: 'rgba(57, 101, 255, 0.1)',
    error: 'rgb(211, 47, 47)',
    error40: 'rgb(211, 47, 47, 0.4)',
    error10: 'rgb(211, 47, 47, 0.1)',
  },
  fonts: {
    primary: '"Open Sans", sans-serif',
    secondary: '"Inter", sans-serif',
  },
};

const theme = createTheme({
  palette: {
    primary: {
      main: STYLE_CONSTANTS.colors.primaryAccent,
    },
  },
  typography: {
    fontFamily: STYLE_CONSTANTS.fonts.primary,
    caption: {
      color: STYLE_CONSTANTS.colors.black40,
      fontFamily: STYLE_CONSTANTS.fonts.secondary,
      fontSize: '12px',
      lineHeight: '20px',
    },
    body1: {
      fontFamily: STYLE_CONSTANTS.fonts.primary,
    },
    body2: {
      fontFamily: STYLE_CONSTANTS.fonts.primary,
    },
    button: {
      fontFamily: STYLE_CONSTANTS.fonts.primary,
    },
    h1: {
      fontFamily: STYLE_CONSTANTS.fonts.primary,
    },
    h2: {
      fontFamily: STYLE_CONSTANTS.fonts.primary,
    },
    h3: {
      fontFamily: STYLE_CONSTANTS.fonts.primary,
      fontSize: '28px',
      lineHeight: '40px',
      fontWeight: 400,
    },
    h4: {
      fontSize: '24px',
      lineHeight: '32px',
      fontWeight: 500,
      fontFamily: STYLE_CONSTANTS.fonts.primary,
    },
    h5: {
      fontFamily: STYLE_CONSTANTS.fonts.primary,
    },
    h6: {
      fontFamily: STYLE_CONSTANTS.fonts.primary,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: ({ ownerState }) => ({
          fontWeight: 600,
          fontSize: '14px',
          lineHeight: '19px',
          letterSpacing: '0.2px',
          borderRadius: '8px',
          textTransform: 'capitalize',
          backgroundImage: 'none',
          boxShadow: 'none',
          textShadow: 'none',
          ...(['outlined', 'contained'].includes(ownerState.variant) && {
            border: `2px solid ${STYLE_CONSTANTS.colors.primaryAccent}`,
            height: '46px',
            padding: '14px 16px',
          }),
          ...(['muted-danger'].includes(ownerState.variant) && {
            border: `2px solid ${STYLE_CONSTANTS.colors.black80}`,
            color: STYLE_CONSTANTS.colors.black80,
            height: '46px',
            padding: '14px 16px',
          }),
          '&:hover:not(:disabled)': {
            boxShadow: 'none',
            textShadow: 'none',
            border: 'none',
            background: 'rgba(64, 64, 242, 0.04)',
            ...(['text'].includes(ownerState.variant) && {
              color: STYLE_CONSTANTS.colors.primaryAccentHover,
            }),
            ...(['text'].includes(ownerState.variant) && ['error'].includes(ownerState.color) && {
              color: STYLE_CONSTANTS.colors.error,
              background: STYLE_CONSTANTS.colors.error10,
            }),
            ...(['contained'].includes(ownerState.variant) && {
              border: `2px solid ${STYLE_CONSTANTS.colors.primaryAccent}`,
              background: STYLE_CONSTANTS.colors.primaryAccentHover,
            }),
            ...(['outlined'].includes(ownerState.variant) && {
              border: `2px solid ${STYLE_CONSTANTS.colors.primaryAccent}`,
              color: STYLE_CONSTANTS.colors.primaryAccent,
            }),
            ...(['muted-danger'].includes(ownerState.variant) && {
              color: `${STYLE_CONSTANTS.colors.error} !important`,
              border: `2px solid ${STYLE_CONSTANTS.colors.error40} !important`,
              background: `${STYLE_CONSTANTS.colors.error10} !important`,
            }),
          },
          '&:disabled': {
            ...(['contained', 'outlined'].includes(ownerState.variant) && {
              border: `2px solid ${STYLE_CONSTANTS.colors.black10}`,
            }),
          },
          '&:active:not(:disabled)': {
            boxShadow: 'none',
            border: 'none',
          },
          '&:focus:not(:disabled)': {
            boxShadow: 'none',
            textShadow: 'none',
            border: 'none',
            ...(['contained', 'outlined'].includes(ownerState.variant) && {
              border: `2px solid ${STYLE_CONSTANTS.colors.primaryAccent}`,
            }),
            ...(['outlined'].includes(ownerState.variant) && {
              border: `2px solid ${STYLE_CONSTANTS.colors.primaryAccent}`,
            }),
            ...(['muted-danger'].includes(ownerState.variant) && {
              color: STYLE_CONSTANTS.colors.black80,
              border: `2px solid ${STYLE_CONSTANTS.colors.black80}`,
            }),
          },
        }),
      },
    },
    MuiButtonOutlined: {
      styleOverrides: {
        root: {
          border: '1px solid red',
          color: '#000',
          textTransform: 'capitalize',
        },
      },
    },
    MuiInputBase: {
      styleOverrides: {
        root: {
          backgroundColor: STYLE_CONSTANTS.colors.primaryLight,
          color: STYLE_CONSTANTS.colors.black80,
          fontSize: '14px',
          lineHeight: '22px',
          height: '46px',
          display: 'flex',
          alignItems: 'center',
          '&:hover': {
            backgroundColor: STYLE_CONSTANTS.colors.primaryBlue,
          },
          '&.Mui-focused': {
            backgroundColor: STYLE_CONSTANTS.colors.primaryBlue,
          },
          '& input': {
            height: '100%',
            boxSizing: 'border-box',
            padding: '0 14px',
            display: 'flex',
            alignItems: 'center',
            fontFamily: STYLE_CONSTANTS.fonts.secondary,
          },
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          height: '46px',
          display: 'flex',
          alignItems: 'center',
          '&:hover': {
            backgroundColor: STYLE_CONSTANTS.colors.primaryBlue,
          },
          '&.Mui-focused': {
            backgroundColor: STYLE_CONSTANTS.colors.primaryBlue,
          },
          '& input': {
            background: 'transparent',
            border: 'none',
            boxShadow: 'none !important',
            height: '100%',
            boxSizing: 'border-box',
            padding: '0 14px',
            display: 'flex',
            alignItems: 'center',
            fontFamily: STYLE_CONSTANTS.fonts.secondary,
          },
        },
        notchedOutline: {
          border: 'none',
        },
      },
    },
    MuiFormLabel: {
      styleOverrides: {
        root: {
          color: STYLE_CONSTANTS.colors.black40,
          fontFamily: STYLE_CONSTANTS.fonts.secondary,
          fontSize: '12px',
          '&.MuiInputLabel-shrink': {
            top: '-10px',
            left: '-14px',
            fontSize: '16px',
            lineHeight: '20px',
          },
          '&.Mui-focused': {
            color: STYLE_CONSTANTS.colors.black40,
          },
        },
      },
    },
    MuiFormHelperText: {
      styleOverrides: {
        root: {
          marginLeft: 0,
        },
      },
    },
    MuiSlider: {
      styleOverrides: {
        thumb: {
          color: STYLE_CONSTANTS.colors.primaryAccent,
        },
        track: {
          color: STYLE_CONSTANTS.colors.primaryAccent,
        },
        rail: {
          color: STYLE_CONSTANTS.colors.secondaryModalBlue,
        },
      },
    },
    MuiTable: {
      styleOverrides: {
        root: {
          tableLayout: 'auto',
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          padding: '11px',
        },
      },
    },
  },
});

export default theme;
