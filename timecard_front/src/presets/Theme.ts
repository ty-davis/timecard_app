import { definePreset } from '@primeuix/themes';
import Aura from '@primeuix/themes/aura';
import { colors } from '@/config/colors';

const TheTheme = definePreset(Aura, {
    semantic: {
        primary: colors.primary,
        colorScheme: {
            light: {
                primary: {
                color: '{primary.950}',
                contrastColor: '#ffffff',
                hoverColor: '{primary.900}',
                activeColor: '{primary.800}'
                },
                highlight: {
                background: '{primary.950}',
                focusBackground: '{primary.700}',
                color: '#ffffff',
                focusColor: '#ffffff'
                },
            },
            dark: {
                primary: {
                color: '{primary.50}',
                contrastColor: '{primary.950}',
                hoverColor: '{primary.100}',
                activeColor: '{primary.200}'
                },
                highlight: {
                background: '{primary.50}',
                focusBackground: '{primary.300}',
                color: '{primary.950}',
                focusColor: '{primary.950}'
                }
            }
        }
    }
});

export default TheTheme;
